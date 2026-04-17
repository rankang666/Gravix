#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/16
@Project: Gravix
@File: http_server.py
@Author: Claude
@Software: PyCharm
@Desc: HTTP + WebSocket Server for Gravix Chat
"""

import asyncio
import json
from pathlib import Path
from typing import Dict, Set, Optional
from datetime import datetime

from aiohttp import web, WSMessage, WSMsgType

from app.chat.session import ChatSession
from app.chat.session_manager import SessionManager
from app.chat.database_session_manager import DatabaseSessionManager
from app.chat.integration.skills_bridge import SkillsBridge
from app.chat.integration.mcp_bridge import MCPBridge
from app.chat.tool_calling import ToolCallParser, ToolExecutor
from app.llm.service import LLMService
from app.llm.base import Message
from app.utils.logger import logger
from app.utils.reloader import HotReloadManager
from app.database import DatabaseAdapterFactory
from app.database.migration import auto_migrate_if_needed


class ChatHTTPServer:
    """
    HTTP + WebSocket Chat Server

    Provides:
    - HTTP server for serving static files (HTML, CSS, JS)
    - WebSocket server for real-time chat communication
    """

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8765,
        skills_bridge: SkillsBridge = None,
        mcp_bridge: MCPBridge = None,
        llm_service: LLMService = None,
        system_prompt: str = None,
        enable_hot_reload: bool = False
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
            enable_hot_reload: Enable hot reload in development
        """
        self.host = host
        self.port = port
        self.skills_bridge = skills_bridge
        self.mcp_bridge = mcp_bridge
        self.llm_service = llm_service
        self.sessions: Dict[str, Set] = {}
        self.clients: Dict[str, Set] = {}

        # Database Session Manager
        import os
        use_database = os.getenv('USE_DATABASE', 'true').lower() == 'true'

        if use_database:
            # Create database adapter from environment
            db_adapter = DatabaseAdapterFactory.create_from_env()
            logger.info("✅ Using database storage")

            # Auto-migrate from JSON if needed
            auto_migrate_if_needed(db_adapter)

            # Use database session manager
            self.session_manager = DatabaseSessionManager(db_adapter)
        else:
            # Fall back to JSON file storage
            logger.info("ℹ️  Using JSON file storage")
            self.session_manager = SessionManager()

        logger.info(f"✅ Session Manager initialized")

        # Plan confirmation mode
        self.require_confirmation = True
        self.pending_plans: Dict[str, dict] = {}

        # System prompt
        self._system_prompt = system_prompt
        self.system_prompt = system_prompt or self._build_system_prompt()

        # Static files directory
        self.static_dir = Path(__file__).parent.parent.parent / 'web' / 'static'

        # Hot reload
        self.enable_hot_reload = enable_hot_reload
        self.hot_reload_manager = None
        self.app_runner = None

        logger.info(f"Static files directory: {self.static_dir}")
        if self.enable_hot_reload:
            logger.info("♻️  Hot reload enabled - Server will auto-reload on code changes")

    def _build_system_prompt(self) -> str:
        """Build system prompt with session context"""
        prompt = """You are Gravix, a helpful AI assistant with access to various tools.

## Plan-First Mode: Human-in-the-Loop Execution

**IMPORTANT**: When user questions require tool calls, you must FIRST create and present a plan to the user for confirmation. DO NOT execute tools immediately.

### Workflow:

1. **Understand the question** - Analyze what the user is asking
2. **Create a plan** - Design step-by-step approach if tools are needed
3. **Present the plan** - Show the plan and wait for user confirmation
4. **Execute (only if confirmed)** - After user confirms, execute the tools

### Available Tools

"""

        # Add Skills information
        if self.skills_bridge:
            prompt += "### Skills\n\n"
            try:
                skills = self.skills_bridge.executor.registry.list_skills()
                for skill in skills:
                    skill_id = skill['skill_id']
                    skill_name = skill['name']
                    skill_desc = skill.get('description', 'No description')
                    prompt += f"- **{skill_id}** ({skill_name}): {skill_desc}\n"
                prompt += "\n"
            except Exception as e:
                logger.warning(f"Failed to get skills list: {e}")
                prompt += "- Skills system available\n\n"

        # Add MaxCompute information
        prompt += "### MaxCompute/ODPS Tools\n\n"
        prompt += "- **maxcompute.list_tables**{}: List all tables in the MaxCompute project\n"
        prompt += "- **maxcompute.describe_table**{table_name}: Get schema information for a specific table\n"
        prompt += "- **maxcompute.get_latest_partition**{table_name}: Get the latest partition name for a table\n"
        prompt += "- **maxcompute.read_query**{query}: Execute a SELECT SQL query (only SELECT queries allowed)\n\n"

        # Add MCP information
        if self.mcp_bridge:
            prompt += "### MCP Tools\n\n"
            try:
                if hasattr(self.mcp_bridge, 'manager') and self.mcp_bridge.manager:
                    servers = list(self.mcp_bridge.manager.clients.keys())
                else:
                    servers = []

                if servers:
                    prompt += f"Connected Servers: {', '.join(servers)}\n\n"
                    prompt += "Use format: `::server.tool_name{params}` or `::tool_name{params}` (defaults to dataworks server)\n\n"
                else:
                    prompt += "- MCP system available (no servers connected)\n\n"
            except Exception as e:
                logger.warning(f"Failed to get MCP info: {e}")
                prompt += "- MCP system available\n\n"

        # Add session context information
        prompt += "### Session Context\n\n"
        try:
            current_session = self.session_manager.get_current_session()
            if current_session:
                prompt += f"**Current Session:** {current_session.title}\n"
                prompt += f"**Messages:** {current_session.get_message_count()}\n"

            # Get recent sessions for context
            recent_sessions = self.session_manager.get_recent_sessions(limit=3)
            if recent_sessions:
                prompt += "\n**Recent Sessions:**\n"
                for i, sess in enumerate(recent_sessions, 1):
                    prompt += f"{i}. {sess['title']} ({sess['message_count']} messages)\n"
                    prompt += f"   Preview: {sess['preview'][:100]}...\n"
                prompt += "\nYou can reference these sessions using commands like:\n"
                prompt += "- `/sessions_list` - List all sessions\n"
                prompt += "- `/session_context <ID>` - Load content from a specific session\n"
                prompt += "- `/session_search <keyword>` - Search for sessions\n"
        except Exception as e:
            logger.warning(f"Failed to get session context: {e}")
            prompt += "- Session context available\n"

        prompt += """
## Response Style

- Be concise and clear
- Always create plans before tool execution
- Show tool calls exactly as they will be executed
- Explain the purpose of each step
- Wait for user confirmation before executing
- When user mentions "previous conversations" or "history", suggest using `/sessions_list` or `/session_search`

Remember: **Plan first, execute only after confirmation!**
"""

        return prompt

    async def handle_http(self, request: web.Request) -> web.Response:
        """Handle HTTP requests for static files"""
        try:
            # Get the file path
            file_path = request.path.strip('/')

            # Handle favicon.ico - return empty response
            if file_path == 'favicon.ico':
                return web.Response(status=204)  # No content

            # Default to index.html
            if not file_path or file_path == 'index.html':
                file_path = 'index.html'

            # Security check: prevent directory traversal
            if '..' in file_path or file_path.startswith('/'):
                return web.Response(text="Access denied", status=403)

            full_path = self.static_dir / file_path

            # Check if file exists
            if not full_path.exists():
                # Try as index.html for directory paths
                if file_path and not file_path.endswith('.html'):
                    full_path = self.static_dir / file_path / 'index.html'

                if not full_path.exists():
                    return web.Response(text=f"File not found: {file_path}", status=404)

            # Determine content type
            content_types = {
                '.html': 'text/html',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.json': 'application/json',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.gif': 'image/gif',
                '.svg': 'image/svg+xml',
                '.ico': 'image/x-icon',
                '.woff': 'font/woff',
                '.woff2': 'font/woff2',
            }

            ext = full_path.suffix.lower()
            content_type = content_types.get(ext, 'application/octet-stream')

            # Read and return file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return web.Response(text=content, content_type=content_type)

        except web.HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Error serving file {request.path}: {e}")
            return web.Response(text=f"Internal server error: {str(e)}", status=500)

    async def handle_websocket(self, request: web.Request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        client_id = id(ws)
        logger.info(f"New WebSocket client connected: {client_id}")

        # Initialize client and session
        if client_id not in self.clients:
            self.clients[client_id] = set()
        if client_id not in self.sessions:
            self.sessions[client_id] = ChatSession(str(client_id))

        self.clients[client_id].add(ws)

        # Send welcome message
        await self.send_to_client(ws, {
            'type': 'system',
            'content': '✅ Connected to Gravix AI Chat Server',
            'timestamp': datetime.utcnow().isoformat()
        })

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self.handle_message(client_id, ws, data)
                    except json.JSONDecodeError:
                        await self.send_error_to_client(ws, "Invalid JSON message")
                    except Exception as e:
                        logger.error(f"Error handling message: {e}")
                        await self.send_error_to_client(ws, str(e))
                elif msg.type == WSMsgType.ERROR:
                    logger.error(f"WebSocket error: {ws.exception()}")

        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")

        finally:
            # Cleanup
            self.clients[client_id].discard(ws)
            if not self.clients[client_id]:
                del self.clients[client_id]
                if client_id in self.sessions:
                    del self.sessions[client_id]
            logger.info(f"Client {client_id} disconnected")

        return ws

    async def handle_message(self, client_id: str, ws, data: dict):
        """Handle incoming WebSocket message"""
        msg_type = data.get('type')

        if msg_type == 'chat':
            await self.handle_chat_message(client_id, ws, data)
        elif msg_type == 'skill_call':
            await self.handle_skill_call(client_id, ws, data)
        else:
            await self.send_error_to_client(ws, f"Unknown message type: {msg_type}")

    async def handle_chat_message(self, client_id: str, ws, data: dict):
        """Handle chat message with streaming output"""
        content = data.get('content', '')

        # Get current session from session manager
        session = self.session_manager.get_current_session()
        if not session:
            session = self.session_manager.create_session()

        # Add user message to session
        session.add_message('user', content)

        # Send thinking status
        await self.send_to_client(ws, {
            'type': 'thinking',
            'content': '🤔 正在分析您的问题...',
            'timestamp': datetime.utcnow().isoformat()
        })

        await asyncio.sleep(0.3)

        # Generate streaming response
        await self._generate_response_stream(client_id, ws, content)

        # Note: Session will be updated in stream handler when complete

    async def handle_skill_call(self, client_id: str, ws, data: dict):
        """Handle skill execution request"""
        skill_id = data.get('skill_id')
        parameters = data.get('parameters', {})

        if not self.skills_bridge:
            await self.send_error_to_client(ws, "Skills bridge not configured")
            return

        try:
            result = await self.skills_bridge.execute(
                skill_id=skill_id,
                parameters=parameters,
                context={'client_id': client_id}
            )

            await self.send_to_client(ws, {
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
            await self.send_error_to_client(ws, f"Skill execution failed: {e}")

    async def _generate_response_stream(self, client_id: str, ws, message: str):
        """
        Generate response with streaming output

        Args:
            client_id: Client identifier
            ws: WebSocket connection
            message: User message

        Streams the response token by token to the client
        """
        # Get current session
        session = self.session_manager.get_current_session()

        # Handle special commands
        if message.startswith('/'):
            response = await self._handle_command(client_id, message)
            # Send as complete message (non-streaming for commands)
            await self.send_to_client(ws, {
                'type': 'chat_response',
                'content': response,
                'timestamp': datetime.utcnow().isoformat()
            })
            if session:
                session.add_message('assistant', response)
            return

        # Use LLM if available
        if self.llm_service and self.llm_service.is_available():
            try:
                history = session.get_history() if session else []

                # Build message list
                messages = [self.llm_service.create_system_message(self.system_prompt)]

                for msg in history[-20:]:
                    messages.append(Message(role=msg['role'], content=msg['content']))

                messages.append(Message(role='user', content=message))

                # Send thinking status
                await self.send_to_client(ws, {
                    'type': 'thinking',
                    'content': '💭 正在生成回复...',
                    'timestamp': datetime.utcnow().isoformat()
                })

                # Start streaming response
                full_response = ""
                message_id = f"{client_id}_{datetime.utcnow().timestamp()}"

                # Send start of stream marker
                await self.send_to_client(ws, {
                    'type': 'stream_start',
                    'message_id': message_id,
                    'timestamp': datetime.utcnow().isoformat()
                })

                # Stream the response
                async for chunk in self.llm_service.chat_stream(messages):
                    full_response += chunk

                    # Send chunk to client
                    await self.send_to_client(ws, {
                        'type': 'stream_chunk',
                        'chunk': chunk,
                        'message_id': message_id,
                        'timestamp': datetime.utcnow().isoformat()
                    })

                # Send end of stream marker
                await self.send_to_client(ws, {
                    'type': 'stream_end',
                    'message_id': message_id,
                    'content': full_response,
                    'timestamp': datetime.utcnow().isoformat()
                })

                # Save to session
                if session:
                    session.add_message('assistant', full_response)

                return full_response

            except Exception as e:
                logger.error(f"LLM streaming error: {e}")
                import traceback
                traceback.print_exc()

                error_msg = f"⚠️ AI服务遇到错误：{str(e)}\n\n请使用 /help 查看可用命令，或稍后重试。"

                # Send error as stream
                await self.send_to_client(ws, {
                    'type': 'stream_end',
                    'content': error_msg,
                    'error': True,
                    'timestamp': datetime.utcnow().isoformat()
                })

                if session:
                    session.add_message('assistant', error_msg)

                return error_msg

        # Fallback response
        fallback_msg = f"Received: {message}\n\n(Note: LLM service not configured. Use /help for available commands.)"

        await self.send_to_client(ws, {
            'type': 'stream_end',
            'content': fallback_msg,
            'timestamp': datetime.utcnow().isoformat()
        })

        return fallback_msg

    async def _generate_response(self, client_id: str, ws, message: str) -> str:
        """Generate response to user message"""
        # Handle special commands
        if message.startswith('/'):
            return await self._handle_command(client_id, message)

        # Use LLM if available
        if self.llm_service and self.llm_service.is_available():
            try:
                session = self.sessions.get(client_id)
                history = session.get_history() if session else []

                # Build message list
                messages = [self.llm_service.create_system_message(self.system_prompt)]

                for msg in history[-20:]:
                    messages.append(Message(role=msg['role'], content=msg['content']))

                messages.append(Message(role='user', content=message))

                # Send thinking status
                await self.send_to_client(ws, {
                    'type': 'thinking',
                    'content': '💭 正在生成回复...',
                    'timestamp': datetime.utcnow().isoformat()
                })

                # Generate response
                response = await self.llm_service.chat(messages)
                response_text = response.content

                # Check for tool calls
                tool_calls = ToolCallParser.parse(response_text)

                if tool_calls and self.require_confirmation:
                    return await self._create_and_present_plan(
                        client_id,
                        ws,
                        response_text,
                        tool_calls,
                        messages
                    )

                return response_text

            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                return f"⚠️ AI服务遇到错误：{str(e)}\n\n请使用 /help 查看可用命令，或稍后重试。"

        return f"Received: {message}\n\n(Note: LLM service not configured. Use /help for available commands.)"

    async def _handle_command(self, client_id: str, message: str) -> str:
        """Handle special commands"""
        command = message.strip().lower()

        if command == '/help':
            return """**可用命令:**

📖 **/help** - 显示此帮助信息
🔧 **/skills** - 列出所有可用技能
⚡ **/mcp_list** - 列出已连接的 MCP 服务器
🔧 **/mcp_call tool_name {params}** - 调用 MCP 工具
📊 **/history** - 显示当前对话历史
🗑️ **/clear** - 清空当前对话历史

**📝 会话管理:**
/sessions_list - 列出所有会话
/sessions_new <标题> - 创建新会话
/sessions_recent - 显示最近会话
/session_context <ID> [行数] - 加载会话上下文
/session_search <关键词> - 搜索会话

**MCP 工具调用示例:**
- `/mcp_call dataworks.ListProjects {}`
- `/mcp_call dataworks.ConvertTimestamps {"Timestamps": [1714567890]}`

**会话上下文示例:**
- `/sessions_list` - 查看所有会话
- `/session_context <session_id>` - 加载指定会话的内容
- `/session_search python` - 搜索包含 'python' 的会话
"""

        elif command == '/skills':
            if self.skills_bridge:
                skills = self.skills_bridge.executor.registry.list_skills()
                skills_list = "\n".join([
                    f"- **{s['skill_id']}**: {s.get('description', s.get('name', 'No description'))}"
                    for s in skills
                ])
                return f"**Available Skills:**\n\n{skills_list}"
            return "No skills configured."

        elif command == '/mcp_list':
            if self.mcp_bridge and hasattr(self.mcp_bridge, 'manager'):
                servers = list(self.mcp_bridge.manager.clients.keys())
                return f"**Connected MCP Servers:**\n\n{', '.join(servers) if servers else 'No servers connected'}"
            return "No MCP bridge configured."

        elif command == '/history':
            session = self.sessions.get(client_id)
            if session:
                history = session.get_history()
                history_text = "\n\n".join([
                    f"**{msg['role']}**: {msg['content']}"
                    for msg in history[-10:]
                ])
                return f"**Recent History:**\n\n{history_text}"
            return "No history available."

        elif command == '/clear':
            session = self.sessions.get(client_id)
            if session:
                session.clear_history()
            return "✅ Conversation history cleared."

        elif command.startswith('/mcp_call '):
            # Format: /mcp_call <tool_name> <json_params>
            # Example: /mcp_call dataworks.ListProjects {}
            try:
                # Remove '/mcp_call ' prefix
                params_part = message[len('/mcp_call '):].strip()

                # Parse tool name and JSON params
                # Format: tool_name {params} or tool_name { "key": "value" }
                import json
                import re

                # Extract tool name and JSON
                match = re.match(r'^(\S+)\s+(\{.*\})$', params_part)
                if not match:
                    return f"❌ Invalid format. Use: `/mcp_call tool_name {{params}}`\n\nExample: `/mcp_call dataworks.ListProjects {{}}`"

                tool_full_name = match.group(1)
                json_params = match.group(2)

                # Parse JSON params
                try:
                    params = json.loads(json_params)
                except json.JSONDecodeError as e:
                    return f"❌ Invalid JSON parameters: {e}"

                # Split tool name into server and tool
                # Format: server.tool_name or tool_name
                if '.' in tool_full_name:
                    server_name, tool_name = tool_full_name.split('.', 1)
                else:
                    return f"❌ Invalid tool format. Use: `server.tool_name`\n\nExample: `dataworks.ListProjects`"

                # Check if MCP bridge is available
                if not self.mcp_bridge or not hasattr(self.mcp_bridge, 'manager'):
                    return "❌ MCP bridge not configured."

                # Call the MCP tool
                result = await self.mcp_bridge.manager.call_tool(server_name, tool_name, params)

                # Format result
                if isinstance(result, dict):
                    result_str = json.dumps(result, indent=2, ensure_ascii=False)
                else:
                    result_str = str(result)

                return f"✅ **Tool `{server_name}.{tool_name}` executed:**\n\n```\n{result_str}\n```"

            except Exception as e:
                logger.error(f"Error calling MCP tool: {e}")
                return f"❌ Error calling MCP tool: {str(e)}\n\nUse `/mcp_list` to see available servers."

        elif command == '/sessions_list':
            """列出所有会话"""
            sessions = self.session_manager.list_sessions()
            if not sessions:
                return "📝 **暂无会话**\n\n使用 `/sessions_new` 创建新会话"

            result = ["📝 **所有会话:**\n"]
            for i, s in enumerate(sessions, 1):
                current = " (当前)" if s['is_current'] else ""
                result.append(
                    f"{i}. **{s['title']}**{current}\n"
                    f"   - 预览: {s['preview']}\n"
                    f"   - 消息数: {s['message_count']}\n"
                    f"   - ID: `{s['session_id']}`\n"
                )

            return "\n".join(result)

        elif command.startswith('/sessions_new '):
            """创建新会话"""
            parts = message.split(' ', 1)
            title = parts[1] if len(parts) > 1 else None

            session = self.session_manager.create_session(title)
            return f"✅ **新会话已创建:**\n\n- 标题: {session.title}\n- ID: `{session.session_id}`"

        elif command.startswith('/session_context '):
            """加载会话上下文"""
            try:
                # Extract session ID and optional lines limit
                params = message[len('/session_context '):].strip().split()
                session_id = params[0]
                max_lines = int(params[1]) if len(params) > 1 else 10

                context = self.session_manager.get_session_context(session_id, max_lines)
                if context:
                    return f"📋 **会话上下文:**\n\n{context}"
                else:
                    return f"❌ 未找到会话或会话为空: `{session_id}`"
            except Exception as e:
                return f"❌ 加载会话上下文失败: {e}\n\n用法: `/session_context <session_id> [lines]`"

        elif command.startswith('/session_search '):
            """搜索会话"""
            try:
                keyword = message[len('/session_search '):].strip()
                results = self.session_manager.search_sessions(keyword)

                if not results:
                    return f"🔍 **搜索结果:**\n\n未找到包含 '{keyword}' 的会话"

                output = [f"🔍 **包含 '{keyword}' 的会话:**\n"]
                for i, r in enumerate(results, 1):
                    current = " (当前)" if r['is_current'] else ""
                    output.append(
                        f"{i}. **{r['title']}**{current}\n"
                        f"   - 预览: {r['preview']}\n"
                        f"   - ID: `{r['session_id']}`\n"
                    )

                return "\n".join(output)
            except Exception as e:
                return f"❌ 搜索失败: {e}\n\n用法: `/session_search <keyword>`"

        elif command == '/sessions_recent':
            """显示最近会话"""
            recent = self.session_manager.get_recent_sessions(limit=5)

            if not recent:
                return "📝 **最近会话:**\n\n暂无其他会话"

            output = ["📝 **最近会话:**\n"]
            for i, r in enumerate(recent, 1):
                output.append(
                    f"{i}. **{r['title']}**\n"
                    f"   - 预览: {r['preview']}\n"
                    f"   - 消息数: {r['message_count']}\n"
                    f"   - ID: `{r['session_id']}`\n"
                )

            return "\n".join(output)

        else:
            return f"❌ Unknown command: {message}\n\nUse /help to see available commands."

    async def _create_and_present_plan(self, client_id: str, ws, response_text: str, tool_calls: list, messages: list) -> str:
        """Create and present a plan for user confirmation"""
        # Save the plan for later execution
        self.pending_plans[client_id] = {
            'tool_calls': tool_calls,
            'messages': messages
        }

        # Return the plan presentation
        return response_text

    async def send_to_client(self, ws, data: dict):
        """Send message to specific WebSocket connection"""
        try:
            await ws.send_json(data)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def send_error_to_client(self, ws, error: str):
        """Send error message to client"""
        await self.send_to_client(ws, {
            'type': 'error',
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        })

    # ==================== Session Management API ====================

    async def handle_api_sessions(self, request: web.Request):
        """GET /api/sessions - List all sessions"""
        try:
            sessions = self.session_manager.list_sessions()
            return web.json_response(sessions)
        except Exception as e:
            logger.error(f"Error listing sessions: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_api_create_session(self, request: web.Request):
        """POST /api/sessions - Create new session"""
        try:
            data = await request.json()
            title = data.get('title')
            session = self.session_manager.create_session(title)
            return web.json_response(session.to_dict())
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_api_get_session(self, request: web.Request):
        """GET /api/sessions/{session_id} - Get session details"""
        try:
            session_id = request.match_info['session_id']
            session_dict = self.session_manager.get_session_dict(session_id)
            if session_dict:
                return web.json_response(session_dict)
            return web.json_response({'error': 'Session not found'}, status=404)
        except Exception as e:
            logger.error(f"Error getting session: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_api_update_session(self, request: web.Request):
        """PATCH /api/sessions/{session_id} - Update session (switch/rename)"""
        try:
            session_id = request.match_info['session_id']

            # Try to parse JSON body (may be empty for switch requests)
            try:
                data = await request.json()
            except:
                data = {}

            # Update title if provided
            if 'title' in data:
                success = self.session_manager.update_session_title(session_id, data['title'])
            else:
                # Switch to session
                success = self.session_manager.switch_session(session_id)

            if success:
                session_dict = self.session_manager.get_session_dict(session_id)
                return web.json_response(session_dict)
            return web.json_response({'error': 'Operation failed'}, status=400)
        except Exception as e:
            logger.error(f"Error updating session: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_api_delete_session(self, request: web.Request):
        """DELETE /api/sessions/{session_id} - Delete session"""
        try:
            session_id = request.match_info['session_id']
            success = self.session_manager.delete_session(session_id)
            if success:
                return web.json_response({'success': True})
            return web.json_response({'error': 'Session not found'}, status=404)
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def handle_api_current_session(self, request: web.Request):
        """GET /api/sessions/current - Get current session"""
        try:
            session_dict = self.session_manager.get_current_session_dict()
            if session_dict:
                return web.json_response(session_dict)
            return web.json_response({'error': 'No current session'}, status=404)
        except Exception as e:
            logger.error(f"Error getting current session: {e}")
            return web.json_response({'error': str(e)}, status=500)

    async def start(self):
        """Start HTTP and WebSocket servers with optional hot reload"""
        # Create HTTP app
        app = web.Application()

        # Static files and WebSocket
        app.router.add_get('/', self.handle_http)
        app.router.add_get('/{path:.*}', self.handle_http)
        app.router.add_get('/ws', self.handle_websocket)  # WebSocket endpoint

        # Session Management API
        app.router.add_get('/api/sessions', self.handle_api_sessions)
        app.router.add_post('/api/sessions', self.handle_api_create_session)
        app.router.add_get('/api/sessions/current', self.handle_api_current_session)
        app.router.add_get('/api/sessions/{session_id}', self.handle_api_get_session)
        app.router.add_patch('/api/sessions/{session_id}', self.handle_api_update_session)
        app.router.add_delete('/api/sessions/{session_id}', self.handle_api_delete_session)

        # Start HTTP server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()

        self.app_runner = runner

        logger.info(f"✅ HTTP server started on http://{self.host}:{self.port}")
        logger.info(f"✅ WebSocket endpoint: ws://{self.host}:{self.port}/ws")
        logger.info(f"✅ Session API available at /api/sessions")
        logger.info(f"✅ Open browser: http://localhost:{self.port}")

        # Start hot reload if enabled
        if self.enable_hot_reload:
            self.hot_reload_manager = HotReloadManager(
                watch_paths=[Path(__file__).parent.parent.parent],  # Project root
                on_reload=self._handle_code_change,
                enabled=True
            )
            await self.hot_reload_manager.start()

        # Keep server running
        try:
            await asyncio.Future()
        except asyncio.CancelledError:
            logger.info("Server shutdown requested")
        finally:
            await self._shutdown()

    async def _shutdown(self):
        """Cleanup on shutdown"""
        # Stop hot reload
        if self.hot_reload_manager:
            self.hot_reload_manager.stop()

        # Cleanup HTTP server
        if self.app_runner:
            await self.app_runner.cleanup()

    async def _handle_code_change(self, changed_file: Path):
        """
        Handle code change and reload server

        Args:
            changed_file: File that was modified
        """
        try:
            logger.info(f"📝 Code changed: {changed_file}")
            logger.info("♻️  Reloading server configuration...")

            # Reload system prompt if file changed
            if 'system_prompt.txt' in str(changed_file):
                await self._reload_system_prompt()

            # Notify all connected clients about reload
            await self._broadcast_reload_notification(changed_file)

            # Rebuild system prompt if needed
            if changed_file.name.endswith('.py'):
                # Python file changed, potentially rebuild prompt
                old_prompt = self.system_prompt
                self.system_prompt = self._build_system_prompt()

                if old_prompt != self.system_prompt:
                    logger.info("📝 System prompt updated")
                else:
                    logger.debug("System prompt unchanged")

            logger.info("✅ Reload complete")

        except Exception as e:
            logger.error(f"Error during reload: {e}")
            import traceback
            traceback.print_exc()

    async def _reload_system_prompt(self):
        """Reload system prompt from file"""
        try:
            prompt_file = Path(__file__).parent.parent.parent / 'system_prompt.txt'
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    self.system_prompt = f.read()
                logger.info("✅ System prompt reloaded from file")
        except Exception as e:
            logger.error(f"Error reloading system prompt: {e}")

    async def _broadcast_reload_notification(self, changed_file: Path):
        """Notify all connected clients about server reload"""
        notification = {
            'type': 'system',
            'content': f'♻️  Server reloaded (change: {changed_file.name})',
            'timestamp': datetime.utcnow().isoformat()
        }

        for client_id, connections in self.clients.items():
            for ws in list(connections):  # Copy to avoid modification during iteration
                if not ws.closed:
                    try:
                        await self.send_to_client(ws, notification)
                    except Exception as e:
                        logger.error(f"Error notifying client {client_id}: {e}")

    async def reload_server(self, changed_file: Path = None):
        """
        Public method to trigger server reload

        Args:
            changed_file: Optional file that triggered the reload
        """
        await self._handle_code_change(changed_file or Path("manual"))

    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.clients)

    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)

    def has_llm(self) -> bool:
        """Check if LLM service is configured"""
        return self.llm_service is not None and self.llm_service.is_available()
