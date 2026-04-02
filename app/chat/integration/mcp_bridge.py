#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: mcp_bridge.py
@Author: Claude
@Software: PyCharm
@Desc: Bridge between chat and MCP system
"""

from typing import Any, Dict, List
from app.mcp.client import MCPClient
from app.mcp.manager import MCPManager
from app.utils.logger import logger


class MCPBridge:
    """
    Bridge between chat interface and MCP system

    Supports both single MCP client and MCP manager for multiple servers.

    Example with single client:
        ```python
        client = MCPClient()
        await client.connect()
        bridge = MCPBridge(client)
        result = await bridge.call_tool('my_tool', {'param': 'value'})
        ```

    Example with MCP manager:
        ```python
        manager = MCPManager()
        await manager.initialize()
        bridge = MCPBridge(manager)
        result = await bridge.call_tool('dataworks', 'list_tables', {})
        ```
    """

    def __init__(self, client_or_manager):
        """
        Initialize MCP bridge

        Args:
            client_or_manager: MCPClient or MCPManager instance
        """
        self.client = None
        self.manager = None

        if isinstance(client_or_manager, MCPClient):
            self.client = client_or_manager
        elif isinstance(client_or_manager, MCPManager):
            self.manager = client_or_manager
        else:
            raise TypeError("Expected MCPClient or MCPManager")

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
        server_name: str = None
    ) -> Any:
        """
        Call an MCP tool

        Args:
            tool_name: Tool name (or server.tool format if using manager)
            arguments: Tool arguments
            server_name: MCP server name (required if using manager)

        Returns:
            Tool execution result
        """
        if self.manager:
            # Parse server.tool format
            if server_name is None:
                if '.' in tool_name:
                    server_name, tool_name = tool_name.split('.', 1)
                else:
                    raise ValueError("server_name required when using MCPManager")

            logger.info(f"Calling MCP tool: {server_name}.{tool_name}")
            return await self.manager.call_tool(server_name, tool_name, arguments)

        elif self.client:
            logger.info(f"Calling MCP tool via bridge: {tool_name}")
            return await self.client.call_tool(tool_name, arguments)

        else:
            raise RuntimeError("No MCP client or manager configured")

    async def list_tools(self, server_name: str = None) -> Any:
        """
        List available MCP tools

        Args:
            server_name: MCP server name (required if using manager)

        Returns:
            List of tool definitions or dict of tools by server
        """
        if self.manager:
            if server_name:
                return await self.manager.list_tools(server_name)
            else:
                return await self.manager.list_all_tools()

        elif self.client:
            return await self.client.list_tools()

        else:
            raise RuntimeError("No MCP client or manager configured")

    async def list_resources(self, server_name: str = None) -> list:
        """
        List available MCP resources

        Args:
            server_name: MCP server name (required if using manager)

        Returns:
            List of resource definitions
        """
        if self.manager:
            if not server_name:
                raise ValueError("server_name required when using MCPManager")
            return await self.manager.list_resources(server_name)

        elif self.client:
            return await self.client.list_resources()

        else:
            raise RuntimeError("No MCP client or manager configured")

    async def read_resource(self, uri: str, server_name: str = None) -> str:
        """
        Read an MCP resource

        Args:
            uri: Resource URI
            server_name: MCP server name (required if using manager)

        Returns:
            Resource content
        """
        if self.manager:
            if not server_name:
                raise ValueError("server_name required when using MCPManager")
            return await self.manager.read_resource(server_name, uri)

        elif self.client:
            return await self.client.read_resource(uri)

        else:
            raise RuntimeError("No MCP client or manager configured")

    async def get_connected_servers(self) -> List[str]:
        """
        Get list of connected MCP servers (only works with manager)

        Returns:
            List of server names
        """
        if self.manager:
            return self.manager.get_connected_servers()
        else:
            return ["default"]
