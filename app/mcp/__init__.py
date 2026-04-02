#!/usr/bin/env python
# encoding: utf-8
"""
MCP Module - Model Context Protocol Implementation

This module provides both MCP Server and MCP Client capabilities:
- Server: Expose tools and resources to MCP clients
- Client: Consume tools and resources from external MCP servers
"""

from app.mcp.protocol import MCPMessage, MCPMessageType, MCPTool, MCPResource
from app.mcp.server import MCPServer
from app.mcp.client import MCPClient

__all__ = [
    'MCPMessage',
    'MCPMessageType',
    'MCPTool',
    'MCPResource',
    'MCPServer',
    'MCPClient'
]
