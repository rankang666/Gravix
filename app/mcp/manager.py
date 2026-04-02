#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: manager.py
@Author: Jerry
@Software: PyCharm
@Desc: MCP Manager - Manage multiple MCP server connections
"""

import asyncio
from typing import Dict, List, Any, Optional
from app.mcp.client import MCPClient
from app.mcp.adapters.stdio import StdioTransport
from app.mcp.adapters.sse import SSETransport
from app.config.mcp_config import get_enabled_mcp_servers, MCPServerConfig
from app.utils.logger import logger


class MCPManager:
    """
    Manage multiple MCP server connections

    Example:
        ```python
        manager = MCPManager()
        await manager.initialize()

        # Call tool from any server
        result = await manager.call_tool("dataworks", "list_tables", {})

        # List tools from all servers
        all_tools = await manager.list_all_tools()
        ```
    """

    def __init__(self):
        """Initialize MCP manager"""
        self.clients: Dict[str, MCPClient] = {}
        self.server_configs: Dict[str, MCPServerConfig] = get_enabled_mcp_servers()
        self._initialized = False

    async def initialize(self):
        """Initialize all enabled MCP servers"""
        logger.info("=" * 60)
        logger.info("Initializing MCP Servers")
        logger.info("=" * 60)

        if not self.server_configs:
            logger.warning("⚠️  No MCP servers configured")
            self._initialized = True
            return

        init_tasks = []
        for name, config in self.server_configs.items():
            logger.info(f"Configuring MCP server: {name}")
            init_tasks.append(self._init_server(name, config))

        # Initialize all servers concurrently
        results = await asyncio.gather(*init_tasks, return_exceptions=True)

        successful = sum(1 for r in results if r is True)
        failed = len(results) - successful

        logger.info("\n" + "=" * 60)
        logger.info(f"MCP Servers Initialization Complete")
        logger.info(f"✅ Connected: {successful}/{len(self.server_configs)}")
        if failed > 0:
            logger.warning(f"❌ Failed: {failed}/{len(self.server_configs)}")
        logger.info("=" * 60 + "\n")

        self._initialized = True

    async def _init_server(self, name: str, config: MCPServerConfig) -> bool:
        """
        Initialize a single MCP server

        Args:
            name: Server name
            config: Server configuration

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create transport based on type
            if config.transport_type == "stdio":
                transport = StdioTransport(
                    command=config.command,
                    args=config.args,
                    env=config.env
                )
            elif config.transport_type == "sse":
                transport = SSETransport(
                    base_url=config.url
                )
            else:
                logger.error(f"Unknown transport type: {config.transport_type}")
                return False

            # Create and connect client
            client = MCPClient(transport)
            await client.connect()

            self.clients[name] = client
            server_info = client.get_server_info()
            logger.info(f"✅ {name}: Connected successfully")
            if server_info:
                logger.info(f"   Server: {server_info.get('name', 'N/A')} v{server_info.get('version', 'N/A')}")

            return True

        except Exception as e:
            logger.error(f"❌ {name}: Failed to connect - {e}")
            return False

    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool from a specific MCP server

        Args:
            server_name: Name of the MCP server
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result

        Raises:
            Exception: If server not found or tool call fails
        """
        if not self._initialized:
            await self.initialize()

        if server_name not in self.clients:
            raise Exception(f"MCP server not found: {server_name}")

        logger.info(f"Calling MCP tool: {server_name}.{tool_name}")
        return await self.clients[server_name].call_tool(tool_name, arguments)

    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List tools from a specific MCP server

        Args:
            server_name: Name of the MCP server

        Returns:
            List of tool definitions
        """
        if not self._initialized:
            await self.initialize()

        if server_name not in self.clients:
            raise Exception(f"MCP server not found: {server_name}")

        return await self.clients[server_name].list_tools()

    async def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        List tools from all connected MCP servers

        Returns:
            Dictionary mapping server names to their tool lists
        """
        if not self._initialized:
            await self.initialize()

        result = {}
        for name, client in self.clients.items():
            try:
                tools = await client.list_tools()
                result[name] = tools
                logger.info(f"{name}: {len(tools)} tools available")
            except Exception as e:
                logger.error(f"Failed to list tools for {name}: {e}")
                result[name] = []

        return result

    async def list_resources(self, server_name: str) -> List[Dict[str, Any]]:
        """
        List resources from a specific MCP server

        Args:
            server_name: Name of the MCP server

        Returns:
            List of resource definitions
        """
        if not self._initialized:
            await self.initialize()

        if server_name not in self.clients:
            raise Exception(f"MCP server not found: {server_name}")

        return await self.clients[server_name].list_resources()

    def get_connected_servers(self) -> List[str]:
        """Get list of connected server names"""
        return list(self.clients.keys())

    async def shutdown(self):
        """Shutdown all MCP connections"""
        logger.info("Shutting down MCP connections...")

        for name, client in self.clients.items():
            try:
                await client.disconnect()
                logger.info(f"Disconnected: {name}")
            except Exception as e:
                logger.error(f"Error disconnecting {name}: {e}")

        self.clients.clear()
        logger.info("All MCP connections closed")
