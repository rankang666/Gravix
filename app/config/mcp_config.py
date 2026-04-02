#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: mcp_config.py
@Author: Jerry
@Software: PyCharm
@Desc: MCP Server Configuration
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class MCPServerConfig:
    """MCP Server configuration"""
    name: str
    enabled: bool = True
    transport_type: str = "stdio"  # stdio or sse
    command: str = None
    args: List[str] = None
    url: str = None
    env: Dict[str, str] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.env is None:
            self.env = {}


# MCP Servers Configuration
MCP_SERVERS = {
    "dataworks": MCPServerConfig(
        name="alibabacloud-dataworks-mcp-server",
        enabled=True,
        transport_type="stdio",
        command="npx",
        args=["-y", "alibabacloud-dataworks-mcp-server"],
        env={}
    ),

    # 可以添加更多MCP服务器
    # "filesystem": MCPServerConfig(
    #     name="filesystem",
    #     enabled=False,
    #     transport_type="stdio",
    #     command="npx",
    #     args=["-y", "@modelcontextprotocol/server-filesystem", "/Users/jerry/Desktop"]
    # ),

    # "fastapi": MCPServerConfig(
    #     name="fastapi-mcp",
    #     enabled=False,
    #     transport_type="sse",
    #     url="http://localhost:8000/mcp"
    # ),
}


def get_enabled_mcp_servers() -> Dict[str, MCPServerConfig]:
    """Get all enabled MCP servers"""
    return {
        name: config
        for name, config in MCP_SERVERS.items()
        if config.enabled
    }


def get_mcp_server(name: str) -> MCPServerConfig:
    """Get specific MCP server configuration"""
    return MCP_SERVERS.get(name)
