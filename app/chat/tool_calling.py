#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: tool_calling.py
@Author: Jerry
@Software: PyCharm
@Desc: Tool calling utilities for LLM
"""

import json
import re
from typing import Dict, Any, Optional, List
from app.utils.logger import logger


class ToolCall:
    """Represents a tool call from LLM"""

    def __init__(self, tool_name: str, parameters: Dict[str, Any]):
        self.tool_name = tool_name
        self.parameters = parameters

    def __repr__(self):
        return f"ToolCall({self.tool_name}, {self.parameters})"


class ToolCallParser:
    """
    Parse tool calls from LLM responses

    Supports formats:
    - ::tool_name{param1=value1, param2=value2}
    - CALL tool_name(param1=value1, param2=value2)
    - JSON format
    """

    @staticmethod
    def parse(text: str) -> List[ToolCall]:
        """
        Parse tool calls from text

        Args:
            text: LLM response text

        Returns:
            List of ToolCall objects
        """
        calls = []

        # Pattern 1: ::tool_name{...} (supports server.tool_name format)
        pattern1 = r'::([a-zA-Z0-9_.]+)\{([^}]*)\}'
        matches1 = re.findall(pattern1, text)

        for tool_name, params_str in matches1:
            try:
                params = ToolCallParser._parse_params(params_str) if params_str else {}
                calls.append(ToolCall(tool_name, params))
                logger.info(f"Parsed tool call: {tool_name} with params: {params}")
            except Exception as e:
                logger.warning(f"Failed to parse tool call: {e}")

        # Pattern 2: CALL tool_name(...)
        pattern2 = r'CALL\s+([a-zA-Z0-9_.]+)\(([^)]*)\)'
        matches2 = re.findall(pattern2, text)

        for tool_name, params_str in matches2:
            try:
                params = ToolCallParser._parse_params(params_str) if params_str else {}
                calls.append(ToolCall(tool_name, params))
                logger.info(f"Parsed tool call: {tool_name} with params: {params}")
            except Exception as e:
                logger.warning(f"Failed to parse tool call: {e}")

        return calls

    @staticmethod
    def _parse_params(params_str: str) -> Dict[str, Any]:
        """
        Parse parameters string

        Supports:
        - key=value
        - "key"="value"
        - JSON format
        """
        params = {}

        # Try JSON first
        try:
            return json.loads(params_str)
        except:
            pass

        # Parse key=value pairs
        # Remove quotes
        params_str = params_str.replace('"', '').replace("'", "")

        # Split by comma
        pairs = params_str.split(',')

        for pair in pairs:
            if '=' in pair:
                key, value = pair.split('=', 1)
                params[key.strip()] = value.strip()

        return params


class ToolExecutor:
    """Execute tool calls"""

    def __init__(self, skills_bridge, mcp_bridge):
        self.skills_bridge = skills_bridge
        self.mcp_bridge = mcp_bridge

    async def execute(self, call: ToolCall) -> Any:
        """
        Execute a tool call

        Args:
            call: ToolCall to execute

        Returns:
            Tool execution result
        """
        tool_name = call.tool_name
        params = call.parameters

        # Check if it's a skill
        if self.skills_bridge:
            skills = self.skills_bridge.executor.registry.list_skills()
            skill_ids = [s['skill_id'] for s in skills]

            if tool_name in skill_ids:
                logger.info(f"Executing skill: {tool_name}")
                result = await self.skills_bridge.execute(
                    skill_id=tool_name,
                    parameters=params
                )
                return result

        # Check if it's an MCP tool (format: server.tool_name)
        if '.' in tool_name and self.mcp_bridge:
            server_name, tool = tool_name.split('.', 1)
            logger.info(f"Executing MCP tool: {server_name}.{tool}")
            result = await self.mcp_bridge.call_tool(tool, params, server_name)
            return result

        # Try MCP tool without server prefix
        if self.mcp_bridge:
            try:
                logger.info(f"Executing MCP tool: {tool_name}")
                result = await self.mcp_bridge.call_tool(tool_name, params, "dataworks")
                return result
            except:
                pass

        raise ValueError(f"Unknown tool: {tool_name}")
