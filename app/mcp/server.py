#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: server.py
@Author: Claude
@Software: PyCharm
@Desc: MCP Server Implementation
"""

import json
from typing import Dict, Callable, Any, Optional
from app.mcp.protocol import (
    MCPMessage,
    MCPMessageType,
    MCPTool,
    MCPResource,
    MCPToolResult,
    MCPResourceContents,
    create_error_response,
    MCPError
)
from app.utils.logger import logger


class MCPServer:
    """
    MCP Server implementation

    The server exposes tools and resources that can be called by MCP clients.
    It follows the Model Context Protocol specification for communication.

    Example:
        ```python
        server = MCPServer("my-server", "1.0.0")

        # Register a tool
        async def hello(name: str) -> str:
            return f"Hello, {name}!"

        server.register_tool(
            name="hello",
            description="Say hello",
            input_schema={"type": "object"},
            handler=hello
        )

        # Handle messages
        response = await server.handle_message(message_json)
        ```
    """

    def __init__(self, name: str = "gravix-mcp-server", version: str = "1.0.0"):
        """
        Initialize MCP server

        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self._tools: Dict[str, Dict[str, Any]] = {}
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ):
        """
        Register a tool that can be called by MCP clients

        Args:
            name: Unique tool name
            description: Tool description
            input_schema: JSON Schema for input validation
            handler: Async function that implements the tool
        """
        self._tools[name] = {
            'tool': MCPTool(name, description, input_schema),
            'handler': handler
        }
        logger.info(f"Registered MCP tool: {name}")

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        mime_type: str = "text/plain",
        handler: Callable = None
    ):
        """
        Register a resource that can be read by MCP clients

        Args:
            uri: Unique resource URI
            name: Resource name
            description: Resource description
            mime_type: MIME type of the resource
            handler: Async function that returns resource content
        """
        self._resources[uri] = {
            'resource': MCPResource(uri, name, description, mime_type),
            'handler': handler
        }
        logger.info(f"Registered MCP resource: {uri}")

    async def handle_message(self, message: str) -> str:
        """
        Handle incoming MCP message

        Args:
            message: JSON string containing the MCP message

        Returns:
            JSON string containing the response
        """
        try:
            msg_dict = json.loads(message)
            msg = MCPMessage(**msg_dict)

            # Route to appropriate handler
            if msg.method == MCPMessageType.INITIALIZE:
                return await self._handle_initialize(msg)
            elif msg.method == MCPMessageType.LIST_TOOLS:
                return await self._handle_list_tools(msg)
            elif msg.method == MCPMessageType.CALL_TOOL:
                return await self._handle_call_tool(msg)
            elif msg.method == MCPMessageType.LIST_RESOURCES:
                return await self._handle_list_resources(msg)
            elif msg.method == MCPMessageType.READ_RESOURCE:
                return await self._handle_read_resource(msg)
            else:
                error_response = create_error_response(
                    msg.id,
                    MCPError.METHOD_NOT_FOUND.value,
                    f"Unknown method: {msg.method}"
                )
                return json.dumps(error_response)

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MCP message: {e}")
            error_response = create_error_response(
                None,
                MCPError.PARSE_ERROR.value,
                "Invalid JSON"
            )
            return json.dumps(error_response)
        except Exception as e:
            logger.error(f"Error handling MCP message: {e}", exc_info=True)
            error_response = create_error_response(
                None,
                MCPError.INTERNAL_ERROR.value,
                str(e)
            )
            return json.dumps(error_response)

    async def _handle_initialize(self, request: MCPMessage) -> str:
        """
        Handle initialize request

        Args:
            request: MCP initialize message

        Returns:
            JSON response with server capabilities
        """
        self._initialized = True

        response = {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": self.name,
                    "version": self.version
                },
                "capabilities": {
                    "tools": {},
                    "resources": {}
                }
            }
        }

        logger.info(f"MCP server initialized: {self.name} v{self.version}")
        return json.dumps(response)

    async def _handle_list_tools(self, request: MCPMessage) -> str:
        """
        Handle list_tools request

        Args:
            request: MCP list_tools message

        Returns:
            JSON response with list of available tools
        """
        tools = [
            tool_data['tool'].to_dict()
            for tool_data in self._tools.values()
        ]

        response = {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {"tools": tools}
        }

        return json.dumps(response)

    async def _handle_call_tool(self, request: MCPMessage) -> str:
        """
        Handle call_tool request

        Args:
            request: MCP call_tool message

        Returns:
            JSON response with tool execution result
        """
        tool_name = request.params.get('name')
        arguments = request.params.get('arguments', {})

        if tool_name not in self._tools:
            error_response = create_error_response(
                request.id,
                MCPError.INVALID_PARAMS.value,
                f"Tool not found: {tool_name}"
            )
            return json.dumps(error_response)

        try:
            handler = self._tools[tool_name]['handler']

            # Call the tool handler
            result = await handler(**arguments)

            # Format result as MCP response
            if isinstance(result, MCPToolResult):
                content = result.content
            elif isinstance(result, str):
                content = [{"type": "text", "text": result}]
            elif isinstance(result, dict):
                content = [{"type": "text", "text": json.dumps(result)}]
            else:
                content = [{"type": "text", "text": str(result)}]

            response = {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "content": content
                }
            }

            logger.info(f"MCP tool '{tool_name}' executed successfully")
            return json.dumps(response)

        except Exception as e:
            logger.error(f"Error executing MCP tool '{tool_name}': {e}")
            error_response = create_error_response(
                request.id,
                MCPError.INTERNAL_ERROR.value,
                str(e)
            )
            return json.dumps(error_response)

    async def _handle_list_resources(self, request: MCPMessage) -> str:
        """
        Handle list_resources request

        Args:
            request: MCP list_resources message

        Returns:
            JSON response with list of available resources
        """
        resources = [
            resource_data['resource'].to_dict()
            for resource_data in self._resources.values()
        ]

        response = {
            "jsonrpc": "2.0",
            "id": request.id,
            "result": {"resources": resources}
        }

        return json.dumps(response)

    async def _handle_read_resource(self, request: MCPMessage) -> str:
        """
        Handle read_resource request

        Args:
            request: MCP read_resource message

        Returns:
            JSON response with resource contents
        """
        uri = request.params.get('uri')

        if uri not in self._resources:
            error_response = create_error_response(
                request.id,
                MCPError.INVALID_PARAMS.value,
                f"Resource not found: {uri}"
            )
            return json.dumps(error_response)

        try:
            resource_data = self._resources[uri]

            if resource_data['handler']:
                # Call the handler to get content
                content = await resource_data['handler']()
            else:
                # No handler, return default message
                content = f"Resource: {uri}"

            response = {
                "jsonrpc": "2.0",
                "id": request.id,
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "text": content
                        }
                    ]
                }
            }

            return json.dumps(response)

        except Exception as e:
            logger.error(f"Error reading resource '{uri}': {e}")
            error_response = create_error_response(
                request.id,
                MCPError.INTERNAL_ERROR.value,
                str(e)
            )
            return json.dumps(error_response)

    def get_tool_count(self) -> int:
        """Get number of registered tools"""
        return len(self._tools)

    def get_resource_count(self) -> int:
        """Get number of registered resources"""
        return len(self._resources)
