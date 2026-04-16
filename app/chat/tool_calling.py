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
from app.tools import execute_maxcompute_tool


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

        # Pattern 1: ::tool_name{...} - use a more robust parsing approach
        # Find all ::tool_name{...} patterns and manually parse the braces
        pattern1 = r'::([a-zA-Z0-9_.]+)\{'
        matches1 = list(re.finditer(pattern1, text))

        for match in matches1:
            try:
                tool_name = match.group(1)
                start_pos = match.end() - 1  # Position of opening brace

                # Find the matching closing brace
                brace_count = 0
                i = start_pos
                while i < len(text):
                    if text[i] == '{':
                        brace_count += 1
                    elif text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            # Found matching closing brace
                            params_str = text[start_pos + 1:i]
                            params = ToolCallParser._parse_params(params_str) if params_str else {}
                            calls.append(ToolCall(tool_name, params))
                            logger.info(f"Parsed tool call: {tool_name} with params: {params}")
                            break
                    i += 1

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
        - JSON format (with or without outer braces)
        """
        params = {}

        # Try JSON first
        try:
            return json.loads(params_str)
        except:
            # Try wrapping in braces for JSON-like strings
            try:
                wrapped = '{' + params_str + '}'
                return json.loads(wrapped)
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

        # Check if it's a MaxCompute tool (format: maxcompute.tool_name)
        if tool_name.startswith('maxcompute.') or tool_name in ['list_tables', 'describe_table', 'get_latest_partition', 'read_query']:
            # Normalize tool name
            if not tool_name.startswith('maxcompute.'):
                tool_name = f'maxcompute.{tool_name}'

            logger.info(f"Executing MaxCompute tool: {tool_name}")
            result = await execute_maxcompute_tool(tool_name, params)
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


class ReActResponse:
    """Represents a ReAct-style response from LLM"""

    def __init__(self, thought: str = None, action: str = None, answer: str = None, tool_call: ToolCall = None):
        self.thought = thought
        self.action = action
        self.answer = answer
        self.tool_call = tool_call  # Store the parsed ToolCall object

    def has_action(self) -> bool:
        """Check if response has an action to execute"""
        return self.action is not None or self.tool_call is not None

    def has_answer(self) -> bool:
        """Check if response has a final answer"""
        return self.answer is not None

    def get_tool_call(self) -> ToolCall:
        """Get the parsed ToolCall object"""
        return self.tool_call

    def __repr__(self):
        if self.has_answer():
            return f"ReActResponse(answer={self.answer[:50]}...)"
        elif self.has_action():
            return f"ReActResponse(thought={self.thought[:30]}..., action={self.action})"
        else:
            return f"ReActResponse(thought={self.thought[:50]}...)"


class ReActParser:
    """
    Parse ReAct-style responses from LLM

    Supports formats:
    - Thought: ... / Action: ...
    - Thought: ... / Answer: ...
    - Action:::tool_name{...}
    """

    @staticmethod
    def parse(text: str) -> ReActResponse:
        """
        Parse ReAct response from text

        Args:
            text: LLM response text

        Returns:
            ReActResponse object
        """
        thought = None
        action = None
        answer = None

        lines = text.strip().split('\n')

        for i, line in enumerate(lines):
            # Parse Thought
            if line.strip().startswith('Thought:') or line.strip().startswith('思考:'):
                thought = line.split(':', 1)[1].strip()
                # Try to get multi-line thought
                j = i + 1
                while j < len(lines) and not lines[j].startswith(('Action:', 'Answer:', '行动:', '答案:')):
                    thought += '\n' + lines[j].strip()
                    j += 1

            # Parse Action
            elif line.strip().startswith('Action:') or line.strip().startswith('行动:'):
                action = line.split(':', 1)[1].strip()

            # Parse Answer
            elif line.strip().startswith('Answer:') or line.strip().startswith('答案:'):
                answer = line.split(':', 1)[1].strip()
                # Get the rest as answer
                answer += '\n' + '\n'.join(lines[i+1:])

        # If no explicit ReAct format, try to detect tool calls directly
        tool_call_obj = None
        if not action and not answer:
            # Check if there's a tool call in the text
            tool_calls = ToolCallParser.parse(text)
            if tool_calls:
                # Use first tool call as action
                tool_call_obj = tool_calls[0]
                params_str = ','.join(f'{k}={v}' for k, v in tool_call_obj.parameters.items())
                action = f"::{tool_call_obj.tool_name}{{{params_str}}}"
                thought = text.replace(action, '').strip() or "I'll use a tool to help with this."
            else:
                # Treat entire text as answer
                answer = text
                thought = None

        # If thought is empty but we have action, generate default thought
        if not thought and action:
            thought = "I need to use a tool to gather information."

        logger.info(f"Parsed ReAct response: thought={thought is not None}, action={action is not None}, answer={answer is not None}")

        return ReActResponse(thought=thought, action=action, answer=answer, tool_call=tool_call_obj)

    @staticmethod
    def extract_tool_call(react_response: ReActResponse) -> ToolCall:
        """
        Extract tool call from ReAct response

        Args:
            react_response: ReActResponse object

        Returns:
            ToolCall object
        """
        # First try to use the cached tool_call object
        if react_response.tool_call:
            return react_response.tool_call

        # Otherwise parse from action string
        if react_response.action:
            calls = ToolCallParser.parse(react_response.action)

            if calls:
                return calls[0]

        raise ValueError(f"Could not extract tool call from ReAct response")
