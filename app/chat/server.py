#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: server.py
@Author: Claude
@Software: PyCharm
@Desc: WebSocket-based Chat Server with LLM integration
"""

import asyncio
import json
from typing import Dict, Set, Optional
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
from app.chat.session import ChatSession
from app.chat.integration.skills_bridge import SkillsBridge
from app.chat.integration.mcp_bridge import MCPBridge
from app.chat.tool_calling import ToolCallParser, ToolExecutor
from app.llm.service import LLMService
from app.llm.base import Message
from app.utils.logger import logger


class ChatServer:
    """
    WebSocket-based chat server with LLM integration

    Provides real-time chat interface with integrated Skills, MCP, and LLM capabilities.

    Example:
        ```python
        llm_service = LLMService(provider='claude')
        server = ChatServer(host="0.0.0.0", port=8765, llm_service=llm_service)
        await server.start()
        ```
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8765,
        skills_bridge: SkillsBridge = None,
        mcp_bridge: MCPBridge = None,
        llm_service: LLMService = None,
        system_prompt: str = None
    ):
        """
        Initialize chat server

        Args:
            host: Server host
            port: Server port
            skills_bridge: Optional skills integration
            mcp_bridge: Optional MCP integration
            llm_service: Optional LLM service for AI responses
            system_prompt: Optional system prompt for LLM
        """
        self.host = host
        self.port = port
        self.skills_bridge = skills_bridge
        self.mcp_bridge = mcp_bridge
        self.llm_service = llm_service
        self.sessions: Dict[str, ChatSession] = {}
        self.clients: Dict[str, WebSocketServerProtocol] = {}

        # System prompt will be built on first use
        self._system_prompt = system_prompt
        self.system_prompt = system_prompt or self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build system prompt with available tools"""
        prompt = """You are Gravix, a helpful AI assistant integrated with a task queue system.

You have access to the following tools and capabilities:

"""

        # Add Skills information
        if self.skills_bridge:
            prompt += "## Available Skills\n\n"
            try:
                skills = self.skills_bridge.executor.registry.list_skills()
                for skill in skills:
                    skill_id = skill['skill_id']
                    skill_name = skill['name']
                    skill_desc = skill.get('description', 'No description')
                    prompt += f"- **{skill_id}** ({skill_name}): {skill_desc}\n"

                prompt += "\nYou can execute these skills when users ask for related functionality.\n\n"
            except Exception as e:
                logger.warning(f"Failed to get skills list: {e}")
                prompt += "- Skills system available (failed to list specific skills)\n\n"

        # Add MCP information
        if self.mcp_bridge:
            prompt += "## Available MCP Tools\n\n"
            try:
                # Get connected MCP servers (synchronous access to manager.clients)
                if hasattr(self.mcp_bridge, 'manager') and self.mcp_bridge.manager:
                    servers = list(self.mcp_bridge.manager.clients.keys())
                else:
                    servers = []

                if servers:
                    prompt += f"Connected MCP Servers: {', '.join(servers)}\n\n"
                    prompt += "You can call MCP tools using the format: server_name.tool_name\n\n"
                else:
                    prompt += "- MCP system available (no servers connected)\n\n"
            except Exception as e:
                logger.warning(f"Failed to get MCP info: {e}")
                prompt += "- MCP system available\n\n"

        # Add usage instructions
        prompt += """
## How to Use Tools

When a user request requires using a skill or MCP tool, use this format:

For simple function calls:
::tool_name{param1=value1, param2=value2}

For complex calls with JSON:
::tool_name{"param1": "value1", "param2": "value2"}

Examples:
- ::calculate{expression=2 + 2 * 3}
- ::system_info{info_type=all}
- ::echo{message=Hello World}
- ::dataworks.ListProjects{}

**IMPORTANT**: Always use the tool call format when you need to execute a skill or MCP tool. Do NOT just describe what you would do - actually call the tool!

## General Instructions

- Be concise, friendly, and helpful
- Answer questions directly when possible
- **Actually execute tools using the format above** when they can help fulfill user requests
- Explain what tools you're using and why
- If a tool call fails, explain the error to the user
- After tool execution, provide a clear summary of the results
"""

        return prompt

    def _default_system_prompt(self) -> str:
        """Get default system prompt (deprecated, use _build_system_prompt)"""
        return self._build_system_prompt()

    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle a client connection

        Args:
            websocket: WebSocket connection
            path: URL path
        """
        client_id = id(websocket)
        logger.info(f"New client connected: {client_id}")

        self.clients[client_id] = websocket
        session = ChatSession(str(client_id))
        self.sessions[client_id] = session

        # Send welcome message
        await self.send_message(client_id, {
            'type': 'system',
            'content': 'Connected to Gravix Chat Server',
            'timestamp': datetime.utcnow().isoformat()
        })

        try:
            async for message in websocket:
                await self.handle_message(client_id, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
            if client_id in self.sessions:
                del self.sessions[client_id]

    async def handle_message(self, client_id: str, message: str):
        """
        Handle incoming message from client

        Args:
            client_id: Client identifier
            message: JSON message string
        """
        try:
            data = json.loads(message)
            session = self.sessions.get(client_id)

            if not session:
                await self.send_error(client_id, "Session not found")
                return

            msg_type = data.get('type')

            if msg_type == 'chat':
                await self.handle_chat_message(client_id, data)
            elif msg_type == 'skill_call':
                await self.handle_skill_call(client_id, data)
            elif msg_type == 'mcp_call':
                await self.handle_mcp_call(client_id, data)
            elif msg_type == 'list_skills':
                await self.handle_list_skills(client_id)
            elif msg_type == 'get_history':
                await self.handle_get_history(client_id, data)
            else:
                await self.send_error(client_id, f"Unknown message type: {msg_type}")

        except json.JSONDecodeError:
            await self.send_error(client_id, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(client_id, str(e))

    async def handle_chat_message(self, client_id: str, data: dict):
        """
        Handle chat message

        Args:
            client_id: Client identifier
            data: Message data
        """
        content = data.get('content', '')
        session = self.sessions[client_id]

        # Add user message to session
        session.add_message('user', content)

        # Generate response
        response = await self._generate_response(client_id, content)

        # Add assistant response to session
        session.add_message('assistant', response)

        # Send response
        await self.send_message(client_id, {
            'type': 'chat_response',
            'content': response,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def handle_skill_call(self, client_id: str, data: dict):
        """
        Handle skill execution request

        Args:
            client_id: Client identifier
            data: Request data
        """
        skill_id = data.get('skill_id')
        parameters = data.get('parameters', {})

        if not self.skills_bridge:
            await self.send_error(client_id, "Skills bridge not configured")
            return

        try:
            result = await self.skills_bridge.execute(
                skill_id=skill_id,
                parameters=parameters,
                context={'client_id': client_id}
            )

            await self.send_message(client_id, {
                'type': 'skill_response',
                'skill_id': skill_id,
                'result': {
                    'success': result.success,
                    'data': result.data,
                    'error': result.error
                },
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as e:
            await self.send_error(client_id, f"Skill execution failed: {e}")

    async def handle_mcp_call(self, client_id: str, data: dict):
        """
        Handle MCP tool call request

        Args:
            client_id: Client identifier
            data: Request data
        """
        tool_name = data.get('tool_name')
        arguments = data.get('arguments', {})

        if not self.mcp_bridge:
            await self.send_error(client_id, "MCP bridge not configured")
            return

        try:
            result = await self.mcp_bridge.call_tool(tool_name, arguments)

            await self.send_message(client_id, {
                'type': 'mcp_response',
                'tool_name': tool_name,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as e:
            await self.send_error(client_id, f"MCP call failed: {e}")

    async def handle_list_skills(self, client_id: str):
        """
        Handle list skills request

        Args:
            client_id: Client identifier
        """
        if not self.skills_bridge:
            await self.send_error(client_id, "Skills bridge not configured")
            return

        skills = await self.skills_bridge.list_skills()

        await self.send_message(client_id, {
            'type': 'skills_list',
            'skills': skills,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def handle_get_history(self, client_id: str, data: dict):
        """
        Handle get history request

        Args:
            client_id: Client identifier
            data: Request data (optional limit parameter)
        """
        session = self.sessions.get(client_id)
        if not session:
            await self.send_error(client_id, "Session not found")
            return

        limit = data.get('limit')
        history = session.get_history(limit=limit)

        await self.send_message(client_id, {
            'type': 'history',
            'history': history,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def _generate_response(self, client_id: str, message: str) -> str:
        """
        Generate response to user message using LLM

        Args:
            client_id: Client identifier
            message: User message

        Returns:
            Response string
        """
        # Check for special commands first
        if message.startswith('/'):
            return await self._handle_command(client_id, message)

        # Use LLM if available
        if self.llm_service and self.llm_service.is_available():
            try:
                session = self.sessions.get(client_id)
                history = session.get_history() if session else []

                # Build message list for LLM
                messages = [self.llm_service.create_system_message(self.system_prompt)]

                # Add conversation history (last 20 messages to avoid token limit)
                for msg in history[-20:]:
                    messages.append(Message(role=msg['role'], content=msg['content']))

                # Add current user message
                messages.append(Message(role='user', content=message))

                # Generate response
                response = await self.llm_service.chat(messages)
                response_text = response.content

                # Check for tool calls in response
                tool_calls = ToolCallParser.parse(response_text)

                if tool_calls:
                    logger.info(f"Detected {len(tool_calls)} tool call(s) in LLM response")

                    # Execute tools and collect results
                    tool_executor = ToolExecutor(self.skills_bridge, self.mcp_bridge)
                    tool_results = []

                    for call in tool_calls:
                        try:
                            result = await tool_executor.execute(call)
                            tool_results.append(f"Tool '{call.tool_name}' result: {result}")
                        except Exception as e:
                            tool_results.append(f"Tool '{call.tool_name}' error: {str(e)}")

                    # Add tool results to conversation and get final response
                    messages.append(Message(role='assistant', content=response_text))
                    messages.append(Message(role='user', content=f"Tool results:\n" + "\n".join(tool_results)))

                    # Get final response from LLM
                    final_response = await self.llm_service.chat(messages)
                    return final_response.content

                return response_text

            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                import traceback
                traceback.print_exc()
                return f"Sorry, I encountered an error: {str(e)}"

        # Fallback to simple response
        return f"Received: {message}\n\n(Note: LLM service not configured. Use /help for available commands.)"

    async def _handle_command(self, client_id: str, message: str) -> str:
        """
        Handle special commands

        Args:
            client_id: Client identifier
            message: Command message

        Returns:
            Response string
        """
        parts = message.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command == '/help':
            return """**Available Commands:**

**Chat Commands:**
- `/help` - Show this help message
- `/clear` - Clear conversation history
- `/history` - Show conversation statistics

**Skills Commands:**
- `/skills` - List available skills
- `/skill <skill_id> [params]` - Execute a skill (JSON format for params)
- `/skill_info <skill_id>` - Get detailed information about a skill

**MCP Commands:**
- `/mcp_list` - List available MCP tools
- `/mcp_call <tool_name> [args]` - Call an MCP tool

**Example:**
`/skill calculate {"expression": "2 + 2 * 3"}`
"""

        elif command == '/clear':
            session = self.sessions.get(client_id)
            if session:
                session.clear_history()
                return "✅ Conversation history cleared"
            return "❌ No session found"

        elif command == '/history':
            session = self.sessions.get(client_id)
            if session:
                count = session.get_message_count()
                duration = session.get_duration()
                return f"📊 Session statistics:\n- Messages: {count}\n- Duration: {duration:.0f} seconds"
            return "❌ No session found"

        elif command == '/skills':
            if self.skills_bridge:
                try:
                    skills = await self.skills_bridge.list_skills()
                    skill_list = '\n'.join([
                        f"- **{s['skill_id']}**: {s.get('description', 'No description')}"
                        for s in skills
                    ])
                    return f"**Available Skills:**\n{skill_list}\n\nUse `/skill_info <id>` for details."
                except Exception as e:
                    return f"❌ Error listing skills: {e}"
            else:
                return "❌ Skills system not available"

        elif command == '/skill_info':
            skill_id = args.strip()
            if not skill_id:
                return "❌ Usage: `/skill_info <skill_id>`"

            if self.skills_bridge:
                try:
                    skills = await self.skills_bridge.list_skills()
                    skill = next((s for s in skills if s['skill_id'] == skill_id), None)
                    if skill:
                        info = f"**Skill: {skill['skill_id']}**\n\n"
                        info += f"Description: {skill.get('description', 'N/A')}\n"
                        info += f"Category: {skill.get('category', 'N/A')}\n"
                        info += f"Version: {skill.get('version', 'N/A')}\n"
                        if 'parameters_schema' in skill:
                            info += f"\nParameters:\n```json\n{json.dumps(skill['parameters_schema'], indent=2)}\n```"
                        return info
                    return f"❌ Skill '{skill_id}' not found"
                except Exception as e:
                    return f"❌ Error getting skill info: {e}"
            return "❌ Skills system not available"

        elif command == '/skill':
            parts = args.strip().split(maxsplit=1)
            skill_id = parts[0] if parts else ""
            params_json = parts[1] if len(parts) > 1 else "{}"

            if not skill_id:
                return "❌ Usage: `/skill <skill_id> [params_json]`\nExample: `/skill calculate {\"expression\": \"2+2\"}`"

            if self.skills_bridge:
                try:
                    params = json.loads(params_json) if params_json else {}
                    result = await self.skills_bridge.execute(
                        skill_id=skill_id,
                        parameters=params,
                        context={'client_id': client_id}
                    )

                    if result.success:
                        return f"✅ **Skill '{skill_id}' executed successfully:**\n\n```json\n{json.dumps(result.data, indent=2)}\n```"
                    else:
                        return f"❌ **Skill '{skill_id}' failed:**\n\n{result.error}"
                except json.JSONDecodeError:
                    return f"❌ Invalid JSON parameters: {params_json}"
                except Exception as e:
                    return f"❌ Error executing skill: {e}"
            return "❌ Skills system not available"

        elif command == '/mcp_list':
            if self.mcp_bridge:
                try:
                    # Get all tools from all servers
                    all_tools = await self.mcp_bridge.list_tools()

                    result = ["**Connected MCP Servers:**\n"]

                    if isinstance(all_tools, dict):
                        for server_name, tools in all_tools.items():
                            result.append(f"\n📦 **{server_name}** ({len(tools)} tools):")
                            # Show first 10 tools
                            for tool in tools[:10]:
                                result.append(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}")
                            if len(tools) > 10:
                                result.append(f"  ... and {len(tools) - 10} more tools")
                    elif isinstance(all_tools, list):
                        result.append(f"\n📦 **Available Tools** ({len(all_tools)}):")
                        for tool in all_tools[:10]:
                            result.append(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}")
                        if len(all_tools) > 10:
                            result.append(f"  ... and {len(all_tools) - 10} more tools")

                    return "\n".join(result)
                except Exception as e:
                    return f"❌ Error listing MCP tools: {str(e)}"
            return "❌ MCP system not available"

        elif command == '/mcp_call':
            if self.mcp_bridge:
                # Parse tool name and arguments
                # Format: /mcp_call tool_name {"arg": "value"} or /mcp_call server.tool_name arg1=value1
                import re
                import json

                # Try to parse JSON args first
                args_match = re.search(r'\s+(\{.*\})$', args)
                tool_name = args
                tool_args = {}

                if args_match:
                    try:
                        tool_args = json.loads(args_match.group(1))
                        tool_name = args[:args_match.start()].strip()
                    except:
                        pass
                else:
                    # Parse key=value pairs
                    params = args.split()
                    if params:
                        tool_name = params[0]
                        for param in params[1:]:
                            if '=' in param:
                                k, v = param.split('=', 1)
                                tool_args[k] = v

                if not tool_name:
                    return "❌ Missing tool name\nUsage: `/mcp_call <tool_name> [args]`"

                try:
                    # Check if tool_name contains server prefix
                    if '.' in tool_name:
                        server_name, tool = tool_name.split('.', 1)
                        result = await self.mcp_bridge.call_tool(tool, tool_args, server_name)
                    else:
                        # Try to call on default server
                        result = await self.mcp_bridge.call_tool(tool_name, tool_args, "dataworks")

                    # Format result
                    if isinstance(result, dict):
                        if 'content' in result and isinstance(result['content'], list):
                            content = result['content'][0].get('text', str(result))
                        else:
                            content = json.dumps(result, indent=2, ensure_ascii=False)
                    else:
                        content = str(result)

                    return f"✅ **Tool '{tool_name}' Result:**\n\n```\n{content}\n```"
                except Exception as e:
                    return f"❌ Tool call failed: {e}"
            return "❌ MCP system not available"

        else:
            return f"❌ Unknown command: {command}\nUse `/help` for available commands."

    async def send_message(self, client_id: str, data: dict):
        """
        Send message to client

        Args:
            client_id: Client identifier
            data: Message data
        """
        client = self.clients.get(client_id)
        if client:
            try:
                await client.send(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")

    async def send_error(self, client_id: str, error: str):
        """
        Send error message to client

        Args:
            client_id: Client identifier
            error: Error message
        """
        await self.send_message(client_id, {
            'type': 'error',
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def start(self):
        """Start the chat server"""
        logger.info(f"Starting chat server on {self.host}:{self.port}")

        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"Chat server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.clients)

    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)

    def has_llm(self) -> bool:
        """Check if LLM service is configured"""
        return self.llm_service is not None and self.llm_service.is_available()
