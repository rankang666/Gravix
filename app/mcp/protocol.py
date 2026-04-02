#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: protocol.py
@Author: Claude
@Software: PyCharm
@Desc: MCP Protocol definitions and data structures
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class MCPMessageType(Enum):
    """MCP message types as per Model Context Protocol specification"""

    # Client to Server
    INITIALIZE = "initialize"
    LIST_TOOLS = "tools/list"
    CALL_TOOL = "tools/call"
    LIST_RESOURCES = "resources/list"
    READ_RESOURCE = "resources/read"

    # Server to Client
    INITIALIZE_RESPONSE = "initialize_response"
    LIST_TOOLS_RESPONSE = "tools/list_response"
    CALL_TOOL_RESPONSE = "tools/call_response"
    LIST_RESOURCES_RESPONSE = "resources/list_response"
    READ_RESOURCE_RESPONSE = "resources/read_response"

    # Errors
    ERROR = "error"


@dataclass
class MCPMessage:
    """
    Base MCP message structure following JSON-RPC 2.0 format

    All MCP messages use JSON-RPC 2.0 format with the following fields:
    - jsonrpc: Always "2.0"
    - id: Request identifier (optional for notifications)
    - method: Method name to invoke
    - params: Method parameters (optional)
    - result: Result data (in response messages)
    - error: Error data (in error responses)
    """

    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: Optional[MCPMessageType] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for JSON serialization"""
        msg_dict = {"jsonrpc": self.jsonrpc}

        if self.id is not None:
            msg_dict["id"] = self.id

        if self.method is not None:
            msg_dict["method"] = self.method.value

        if self.params is not None:
            msg_dict["params"] = self.params

        if self.result is not None:
            msg_dict["result"] = self.result

        if self.error is not None:
            msg_dict["error"] = self.error

        return msg_dict


@dataclass
class MCPTool:
    """
    MCP Tool definition

    Tools are callable functions that can be invoked by MCP clients.
    Each tool has a name, description, and JSON Schema for input validation.
    """

    name: str
    description: str
    input_schema: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary for protocol transmission"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


@dataclass
class MCPResource:
    """
    MCP Resource definition

    Resources are data sources that can be read by MCP clients.
    Examples: files, database queries, API endpoints
    """

    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"

    def to_dict(self) -> Dict[str, Any]:
        """Convert resource to dictionary for protocol transmission"""
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type
        }


@dataclass
class MCPToolResult:
    """
    Result from calling an MCP tool

    Attributes:
        content: List of content items (text, images, data, etc.)
        is_error: Whether the tool call resulted in an error
    """

    content: List[Dict[str, Any]]
    is_error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "content": self.content,
            "isError": self.is_error
        }


@dataclass
class MCPResourceContents:
    """
    Contents of an MCP resource

    Attributes:
        uri: URI of the resource
        text: Text content (for text-based resources)
        blob: Binary data (for binary resources)
    """

    uri: str
    text: Optional[str] = None
    blob: Optional[bytes] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {"uri": self.uri}

        if self.text is not None:
            result["text"] = self.text

        if self.blob is not None:
            # For binary data, we'd typically encode it (e.g., base64)
            result["blob"] = str(self.blob)

        return result


# MCP Error Codes (following JSON-RPC 2.0)
class MCPError(Enum):
    """Standard MCP error codes"""

    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603


def create_error_response(
    msg_id: Optional[Union[str, int]],
    error_code: int,
    error_message: str,
    error_data: Any = None
) -> Dict[str, Any]:
    """
    Create an MCP error response

    Args:
        msg_id: Message ID from the request
        error_code: Error code (see MCPError enum)
        error_message: Human-readable error message
        error_data: Additional error data (optional)

    Returns:
        Dictionary representing the error response
    """
    error_dict = {
        "code": error_code,
        "message": error_message
    }

    if error_data is not None:
        error_dict["data"] = error_data

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "error": error_dict
    }
