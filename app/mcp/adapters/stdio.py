#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: stdio.py
@Author: Claude
@Software: PyCharm
@Desc: STDIO Transport for MCP (local communication via subprocess)
"""

import asyncio
import json
from typing import Optional, List, Dict
from app.utils.logger import logger


class StdioTransport:
    """
    STDIO transport for MCP communication

    This transport spawns a subprocess and communicates via stdin/stdout,
    suitable for local MCP servers (e.g., DataWorks MCP Server).

    Example:
        ```python
        transport = StdioTransport(
            command="npx",
            args=["-y", "alibabacloud-dataworks-mcp-server"]
        )
        await transport.connect()
        response = await transport.send_and_receive('{"jsonrpc":"2.0",...}')
        ```
    """

    def __init__(
        self,
        command: str,
        args: List[str] = None,
        env: Dict[str, str] = None
    ):
        """
        Initialize STDIO transport

        Args:
            command: Command to execute (e.g., "npx")
            args: List of arguments
            env: Environment variables (default: None, uses current env)
        """
        self.command = command
        self.args = args or []
        self.env = env

        self.process: Optional[asyncio.subprocess.Process] = None
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self._connected = False

    async def connect(self):
        """Start the subprocess and establish communication"""
        try:
            # Prepare environment
            import os
            process_env = os.environ.copy()

            # Add Alibaba Cloud region to environment
            # DataWorks MCP reads REGION from environment (not ALIBABA_CLOUD_REGION_ID)
            if 'ALIBABA_CLOUD_REGION_ID' in os.environ:
                region_id = os.environ['ALIBABA_CLOUD_REGION_ID']
                process_env['REGION'] = region_id
                logger.info(f"Setting REGION: {region_id}")

            # Also set ALIBABA_CLOUD_REGION_ID for compatibility
            if 'ALIBABA_CLOUD_REGION_ID' in os.environ:
                process_env['ALIBABA_CLOUD_REGION_ID'] = os.environ['ALIBABA_CLOUD_REGION_ID']
                process_env['ALIBABA_CLOUD_ACCESS_KEY_ID'] = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')
                process_env['ALIBABA_CLOUD_ACCESS_KEY_SECRET'] = os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')

            if self.env:
                process_env.update(self.env)

            # Start subprocess
            cmd_str = f"{self.command} {' '.join(self.args)}"
            logger.info(f"Starting MCP server subprocess: {cmd_str}")

            self.process = await asyncio.create_subprocess_exec(
                self.command,
                *self.args,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=process_env
            )

            self.reader = self.process.stdout
            self.writer = self.process.stdin
            self._connected = True

            logger.info(f"✅ MCP server subprocess started (PID: {self.process.pid})")

            # Wait a bit for the server to initialize
            # DataWorks MCP may take 10-20 seconds to start
            await asyncio.sleep(2.0)

            # Check if process is still running
            if self.process.returncode is not None:
                stderr_output = await self.process.stderr.read()
                error_msg = stderr_output.decode('utf-8', errors='ignore')
                raise RuntimeError(f"MCP server exited immediately: {error_msg}")

        except Exception as e:
            logger.error(f"Failed to start MCP server subprocess: {e}")
            if self.process:
                self.process.terminate()
                await self.process.wait()
            raise

    async def send_and_receive(self, message: str) -> str:
        """
        Send message and read response

        Args:
            message: JSON message to send

        Returns:
            Response string
        """
        if not self._connected or not self.writer or not self.reader:
            raise RuntimeError("Not connected")

        response = None  # Initialize response variable

        try:
            # Send message
            data = message.encode('utf-8') + b'\n'
            self.writer.write(data)
            await self.writer.drain()

            logger.debug(f"Sent: {message[:100]}...")

            # Read response with a larger buffer
            response_data = bytearray()
            timeout = 30  # seconds
            read_timeout = 5  # Timeout for each read operation after first chunk

            try:
                while True:
                    try:
                        # Read chunk with timeout
                        chunk = await asyncio.wait_for(
                            self.reader.read(8192),
                            timeout=timeout if not response_data else read_timeout
                        )

                        if not chunk:
                            break  # EOF

                        response_data.extend(chunk)

                        # Try to decode and parse what we have so far
                        try:
                            data_str = response_data.decode('utf-8').strip()
                            # Try to find JSON in the data
                            parsed = json.loads(data_str)
                            response = data_str
                            break
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            # Not complete JSON or incomplete UTF-8 yet, continue reading
                            if len(response_data) > 10 * 1024 * 1024:  # 10MB limit
                                raise ValueError("Response too large (>10MB)")
                            continue

                    except asyncio.TimeoutError:
                        # If we have data, try to use it
                        if response_data:
                            break
                        raise TimeoutError(f"No response from MCP server within {timeout}s")

            except asyncio.TimeoutError:
                raise TimeoutError(f"No response from MCP server within {timeout}s")

            # Decode and find valid JSON
            if not response and response_data:
                data_str = response_data.decode('utf-8').strip()

                # Try to parse the complete data
                try:
                    json.loads(data_str)
                    response = data_str
                except json.JSONDecodeError:
                    # If still not valid JSON, search for JSON object
                    # Find the last complete JSON object
                    lines = data_str.split('\n')
                    for line in reversed(lines):
                        try:
                            json.loads(line.strip())
                            response = line.strip()
                            break
                        except json.JSONDecodeError:
                            continue

            # Validate response is JSON
            try:
                if response:
                    json.loads(response)
                else:
                    raise ValueError("Empty response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Invalid JSON response (read {len(response_data)} bytes)")
                logger.debug(f"Response data preview: {response_data[:500]}")
                raise ValueError(f"MCP server returned invalid JSON: {e}")

            logger.debug(f"Received: {response[:100]}...")
            return response

        except Exception as e:
            logger.error(f"Error in MCP communication: {e}")
            raise

    async def disconnect(self):
        """Terminate the subprocess"""
        if self.process:
            logger.info("Terminating MCP server subprocess...")

            try:
                self.writer.close()
                await self.writer.wait_closed()
            except:
                pass

            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
                logger.info("✅ MCP server terminated gracefully")
            except asyncio.TimeoutError:
                logger.warning("⚠️  MCP server did not terminate gracefully, killing...")
                self.process.kill()
                await self.process.wait()
                logger.info("✅ MCP server killed")

            self._connected = False
