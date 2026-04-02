#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: sse.py
@Author: Claude
@Software: PyCharm
@Desc: SSE/HTTP Transport for MCP
"""

import aiohttp
from typing import Optional
from app.utils.logger import logger


class SSETransport:
    """
    Server-Sent Events / HTTP transport for MCP

    This transport uses HTTP POST requests for MCP communication,
    suitable for remote MCP servers.
    """

    def __init__(self, base_url: str):
        """
        Initialize SSE/HTTP transport

        Args:
            base_url: Base URL of the MCP server (e.g., http://localhost:8080)
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self._connected = False

    async def connect(self):
        """Connect via HTTP"""
        self.session = aiohttp.ClientSession()
        self._connected = True
        logger.info(f"SSE transport connected to {self.base_url}")

    async def send_and_receive(self, message: str) -> str:
        """
        Send message via HTTP POST and receive response

        Args:
            message: JSON message to send

        Returns:
            Response string
        """
        if not self._connected:
            raise RuntimeError("Not connected")

        try:
            async with self.session.post(
                f"{self.base_url}/mcp",
                data=message,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response.raise_for_status()
                return await response.text()

        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            raise

    async def disconnect(self):
        """Disconnect and close session"""
        if self.session:
            await self.session.close()
        self._connected = False
        logger.info("SSE transport disconnected")
