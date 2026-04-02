#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: mcp.py
@Author: Claude
@Software: PyCharm
@Desc: MCP-related data schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class MCPToolCallRequest(BaseModel):
    """MCP tool call request model"""
    tool_name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class MCPResourceReadRequest(BaseModel):
    """MCP resource read request model"""
    uri: str = Field(..., description="Resource URI to read")


class MCPToolInfo(BaseModel):
    """MCP tool information model"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPResourceInfo(BaseModel):
    """MCP resource information model"""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"
