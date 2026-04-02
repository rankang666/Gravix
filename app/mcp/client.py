#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: client.py
@Author: Claude
@Software: PyCharm
@Desc: MCP Client Implementation
"""

import json
from typing import Dict, List, Any, Optional
from app.mcp.protocol import (
    MCPMessage,
    MCPMessageType,
    create_error_response,
    MCPError
)
from app.mcp.adapters.stdio import StdioTransport
from app.utils.logger import logger


class MCPClient:
    """
    MCP Client for connecting to external MCP servers

    The client can connect to MCP servers and call their tools and resources.

    Example:
        ```python
        transport = StdioTransport()
        client = MCPClient(transport)

        await client.connect()

        # List available tools
        tools = await client.list_tools()

        # Call a tool
        result = await client.call_tool("my_tool", {"param": "value"})
        ```
    """

    def __init__(self, transport=None):
        """
        Initialize MCP client

        Args:
            transport: Transport adapter for communication (default: StdioTransport)
        """
        self.transport = transport or StdioTransport()
        self._initialized = False
        self._server_info: Optional[Dict[str, Any]] = None
        self._message_id = 0

    async def connect(self):
        """
        Connect to MCP server and initialize session

        Raises:
            Exception: If connection or initialization fails
        """
        await self.transport.connect()

        # Send initialize request
        init_message = MCPMessage(
            jsonrpc="2.0",
            id=self._next_id(),
            method=MCPMessageType.INITIALIZE,
            params={
                "protocolVersion": "2024-11-05",
                "clientInfo": {
                    "name": "gravix-mcp-client",
                    "version": "1.0.0"
                },
                "capabilities": {}
            }
        )

        response_str = await self.transport.send_and_receive(
            json.dumps(init_message.to_dict())
        )
        response = json.loads(response_str)

        if 'error' in response:
            raise Exception(f"MCP initialization failed: {response['error']}")

        self._server_info = response.get('result', {}).get('serverInfo')
        self._initialized = True

        logger.info(f"Connected to MCP server: {self._server_info}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from the server

        Returns:
            List of tool definitions

        Raises:
            Exception: if not initialized or request fails
        """
        if not self._initialized:
            await self.connect()

        message = MCPMessage(
            jsonrpc="2.0",
            id=self._next_id(),
            method=MCPMessageType.LIST_TOOLS
        )

        response = await self._send_message(message)

        if 'error' in response:
            raise Exception(f"Failed to list tools: {response['error']}")

        return response.get('result', {}).get('tools', [])

    async def call_tool(
        self,
        name: str,
        arguments: Dict[str, Any]
    ) -> Any:
        """
        Call a tool on the server

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            Exception: If tool call fails
        """
        if not self._initialized:
            await self.connect()

        # Ensure arguments is a dict
        if arguments is None:
            arguments = {}
        elif not isinstance(arguments, dict):
            arguments = {}

        message = MCPMessage(
            jsonrpc="2.0",
            id=self._next_id(),
            method=MCPMessageType.CALL_TOOL,
            params={
                "name": name,
                "arguments": arguments
            }
        )

        response = await self._send_message(message)

        if 'error' in response:
            raise Exception(f"Tool call failed: {response['error']}")

        return response.get('result')

    async def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources from the server

        Returns:
            List of resource definitions

        Raises:
            Exception: If request fails
        """
        if not self._initialized:
            await self.connect()

        message = MCPMessage(
            jsonrpc="2.0",
            id=self._next_id(),
            method=MCPMessageType.LIST_RESOURCES
        )

        response = await self._send_message(message)

        if 'error' in response:
            raise Exception(f"Failed to list resources: {response['error']}")

        return response.get('result', {}).get('resources', [])

    async def read_resource(self, uri: str) -> str:
        """
        Read a resource from the server

        Args:
            uri: Resource URI

        Returns:
            Resource content as string

        Raises:
            Exception: If read fails
        """
        if not self._initialized:
            await self.connect()

        message = MCPMessage(
            jsonrpc="2.0",
            id=self._next_id(),
            method=MCPMessageType.READ_RESOURCE,
            params={"uri": uri}
        )

        response = await self._send_message(message)

        if 'error' in response:
            raise Exception(f"Resource read failed: {response['error']}")

        contents = response.get('result', {}).get('contents', [])
        if contents and 'text' in contents[0]:
            return contents[0]['text']

        return ""

    async def _send_message(self, message: MCPMessage) -> Dict[str, Any]:
        """
        Send message and wait for response

        Args:
            message: MCP message to send

        Returns:
            Response dictionary
        """
        msg_str = json.dumps(message.to_dict())
        response_str = await self.transport.send_and_receive(msg_str)
        return json.loads(response_str)

    def _next_id(self) -> int:
        """Get next message ID"""
        self._message_id += 1
        return self._message_id

    async def disconnect(self):
        """Disconnect from server"""
        await self.transport.disconnect()
        self._initialized = False
        logger.info("Disconnected from MCP server")

    def get_server_info(self) -> Optional[Dict[str, Any]]:
        """Get connected server information"""
        return self._server_info
