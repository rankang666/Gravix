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
from typing import Dict, Set, Optional, Any
from datetime import datetime
import websockets
from websockets.server import WebSocketServerProtocol
from app.chat.session import ChatSession
from app.chat.integration.skills_bridge import SkillsBridge
from app.chat.integration.mcp_bridge import MCPBridge
from app.chat.tool_calling import ToolCallParser, ToolExecutor, ReActParser, ReActResponse
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

        # Plan confirmation mode
        self.require_confirmation = True  # Default: require user confirmation for tool calls
        self.pending_plans: Dict[str, dict] = {}  # client_id -> pending plan

        # System prompt will be built on first use
        self._system_prompt = system_prompt
        self.system_prompt = system_prompt or self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build system prompt with available tools and plan-first mode"""
        prompt = """You are Gravix, a helpful AI assistant with access to various tools.

## Plan-First Mode: Human-in-the-Loop Execution

**IMPORTANT**: When user questions require tool calls, you must FIRST create and present a plan to the user for confirmation. DO NOT execute tools immediately.

### Workflow:

1. **Understand the question** - Analyze what the user is asking
2. **Create a plan** - Design step-by-step approach if tools are needed
3. **Present the plan** - Show the plan and wait for user confirmation
4. **Execute (only if confirmed)** - After user confirms, execute the tools

### Response Formats:

#### For simple questions (no tools needed):
```
Answer: [Your direct answer]
```

#### For questions needing tools (FIRST response):
```
**Plan:** [Brief description of what you'll do]

**Steps:**
1. [First step with tool call]
   - Tool: ::tool_name{params}
   - Purpose: [Why this step is needed]

2. [Second step if needed]
   - Tool: ::tool_name{params}
   - Purpose: [What information this provides]

**Expected Result:** [What the user will get after execution]

---

**Please confirm:** Should I proceed with this plan? (yes/no)
```

#### After user confirms:
```
**Step 1:** [Executing tool_name]
[Tool results]

**Step 2:** [Executing tool_name]
[Tool results]

**Answer:** [Final answer based on results]
```

### Example:

User: "How many tables are in project gcc_002?"

**Plan:** Query the DataWorks system to get the list of tables in the gcc_002 project and count them.

**Steps:**
1. List all tables in the gcc_002 project
   - Tool: ::dataworks.ListTables{"projectName":"gcc_002"}
   - Purpose: Get the complete table list

**Expected Result:** You'll know the exact number of tables in the project and their names.

---

**Please confirm:** Should I proceed with this plan? (yes/no)

[User says yes]

**Step 1:** Executing ListTables...
[Retrieved 23 tables: users, orders, products, ...]

**Answer:** The gcc_002 project contains **23 tables**.

### Important Rules:

1. **ALWAYS plan first** - Never execute tools without presenting the plan first
2. **Be specific** - Show exact tool calls with parameters
3. **Explain why** - Tell the user what each step accomplishes
4. **Wait for confirmation** - Only proceed after user approval
5. **Direct answers** - For simple questions you know, answer directly without tools

## Available Tools

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
                # Get connected MCP servers (synchronous access to manager.clients)
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

        # Add general instructions
        prompt += """
## Response Style

- Be concise and clear
- Always create plans before tool execution
- Show tool calls exactly as they will be executed
- Explain the purpose of each step
- Wait for user confirmation before executing

## Tool Call Examples

- ::calculate{expression=2+2}
- ::dataworks.ListProjects{}
- ::dataworks.ListTables{"projectName":"gcc_002"}
- ::maxcompute.list_tables{}
- ::maxcompute.read_query{"query":"SELECT * FROM users LIMIT 10"}
- ::system_info{info_type=all}

Remember: **Plan first, execute only after confirmation!**
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

        # Send thinking status - starting to analyze
        await self.send_message(client_id, {
            'type': 'thinking',
            'content': '🤔 正在分析您的问题...',
            'timestamp': datetime.utcnow().isoformat()
        })

        # Small delay to show the thinking status
        await asyncio.sleep(0.5)

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
        Generate response to user message with plan-first mode

        Args:
            client_id: Client identifier
            message: User message

        Returns:
            Response string
        """
        # Check for special commands first
        if message.startswith('/'):
            return await self._handle_command(client_id, message)

        # Check for plan confirmation (yes/no)
        if message.lower().strip() in ['yes', 'y', 'confirm', 'ok', 'continue', '执行', '确认']:
            return await self._execute_confirmed_plan(client_id)

        elif message.lower().strip() in ['no', 'n', 'cancel', 'stop', '取消', '否']:
            # Cancel pending plan
            if client_id in self.pending_plans:
                del self.pending_plans[client_id]
            return "❌ 计划已取消。如有需要，请重新描述您的问题。"

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

                # Send thinking status - generating response
                await self.send_message(client_id, {
                    'type': 'thinking',
                    'content': '💭 正在生成回复...',
                    'timestamp': datetime.utcnow().isoformat()
                })

                # Generate response
                response = await self.llm_service.chat(messages)
                response_text = response.content

                # Check if response contains tool calls
                tool_calls = ToolCallParser.parse(response_text)

                if tool_calls and self.require_confirmation:
                    # Send thinking status - planning tool calls
                    await self.send_message(client_id, {
                        'type': 'thinking',
                        'content': f'📋 正在制定计划（需要调用 {len(tool_calls)} 个工具）...',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                    await asyncio.sleep(0.3)
                    # Extract plan and ask for confirmation
                    return await self._create_and_present_plan(
                        client_id,
                        response_text,
                        tool_calls,
                        messages
                    )

                # No tool calls or confirmation not required - return direct response
                return response_text

            except Exception as e:
                logger.error(f"LLM generation error: {e}")
                import traceback
                traceback.print_exc()

                # Graceful degradation: provide helpful message
                error_msg = str(e)

                # Check if it's a rate limit or API error
                if '403' in error_msg or 'rate limit' in error_msg.lower():
                    return """⚠️ AI服务暂时不可用（可能是请求过于频繁）

请稍后再试。在此期间，您仍可使用以下功能：

📌 **命令模式：**
- /help - 查看所有可用命令
- /skills - 查看和调用技能
- /mcp_list - 查看DataWorks工具
- /mcp_call tool_name {} - 调用MCP工具

📌 **直接调用：**
- ::calculate{expression=2+2}
- ::system_info{info_type=all}
- ::dataworks.ListProjects{}

这些功能无需AI即可正常使用。"""

                else:
                    return f"⚠️ AI服务遇到错误：{error_msg}\n\n请使用 /help 查看可用命令，或稍后重试。"

        # Fallback to simple response
        return f"Received: {message}\n\n(Note: LLM service not configured. Use /help for available commands.)"

    def _format_observation(self, result: Any) -> str:
        """
        Format tool execution result as observation

        Args:
            result: Tool execution result

        Returns:
            Formatted observation string
        """
        import json

        if isinstance(result, dict):
            # Handle MCP tool result format
            if 'content' in result and isinstance(result['content'], list):
                # Extract text content from MCP result
                texts = []
                for item in result['content']:
                    if isinstance(item, dict) and 'text' in item:
                        texts.append(item['text'])
                    elif isinstance(item, str):
                        texts.append(item)
                content = '\n'.join(texts)

                # Try to parse as JSON for better formatting
                try:
                    parsed = json.loads(content)
                    return json.dumps(parsed, indent=2, ensure_ascii=False)
                except:
                    return content
            else:
                return json.dumps(result, indent=2, ensure_ascii=False)

        elif hasattr(result, 'success'):
            # Handle skill result format
            if result.success:
                return json.dumps(result.data, indent=2, ensure_ascii=False)
            else:
                return f"Error: {result.error}"

        else:
            return str(result)

    async def _create_and_present_plan(
        self,
        client_id: str,
        response_text: str,
        tool_calls: list,
        messages: list
    ) -> str:
        """
        Create a plan from tool calls and present to user for confirmation

        Args:
            client_id: Client identifier
            response_text: LLM response containing the plan
            tool_calls: List of tool calls to execute
            messages: Conversation messages

        Returns:
            Plan presentation message
        """
        # Save the plan for later execution
        self.pending_plans[client_id] = {
            'tool_calls': tool_calls,
            'messages': messages,
            'response_text': response_text,
            'timestamp': datetime.utcnow().isoformat()
        }

        # Extract tool calls for display
        steps = []
        for i, call in enumerate(tool_calls, 1):
            params_str = ', '.join(f'{k}={v}' for k, v in call.parameters.items())
            steps.append(f"{i}. **{call.tool_name}**")
            if params_str:
                steps.append(f"   参数: {params_str}")
            steps.append("")

        # Build confirmation message
        confirmation_msg = f"""📋 **执行计划**

{response_text}

**详细步骤：**

{chr(10).join(steps)}

---

⚠️ **需要您的确认：**

回复 `yes` 或 `确认` 开始执行此计划
回复 `no` 或 `取消` 取消执行

💡 提示：你也可以修改问题后重新发送
"""

        return confirmation_msg

    async def _execute_confirmed_plan(self, client_id: str) -> str:
        """
        Execute a previously confirmed plan

        Args:
            client_id: Client identifier

        Returns:
            Execution result message
        """
        # Check if there's a pending plan
        if client_id not in self.pending_plans:
            return "❌ 没有待执行的计划。请先提出您的问题。"

        plan = self.pending_plans[client_id]
        tool_calls = plan['tool_calls']
        messages = plan['messages']

        # Remove from pending
        del self.pending_plans[client_id]

        # Execute tool calls
        tool_executor = ToolExecutor(self.skills_bridge, self.mcp_bridge)
        execution_results = []

        for i, call in enumerate(tool_calls, 1):
            try:
                logger.info(f"Executing tool {i}/{len(tool_calls)}: {call.tool_name}")

                # Send thinking status - executing tool
                await self.send_message(client_id, {
                    'type': 'thinking',
                    'content': f'🔧 正在执行工具 {i}/{len(tool_calls)}: {call.tool_name}',
                    'timestamp': datetime.utcnow().isoformat()
                })

                result = await tool_executor.execute(call)
                observation = self._format_observation(result)

                execution_results.append(f"**步骤 {i}:** 执行 `{call.tool_name}`\n")
                execution_results.append(f"```\n{observation[:500]}\n```\n")

                # Add to messages for potential further processing
                messages.append(Message(role='assistant', content=call.tool_name))
                messages.append(Message(role='user', content=f"Result: {observation}"))

            except Exception as e:
                error_msg = f"❌ 工具执行失败: {str(e)}"
                logger.error(error_msg)
                execution_results.append(f"**步骤 {i}:** ❌ 失败\n{error_msg}\n")
                # Continue with remaining tools

        # If all tools executed successfully, try to get final answer from LLM
        if all("失败" not in r for r in execution_results):
            try:
                # Ask LLM to synthesize the results
                messages.append(Message(
                    role='user',
                    content="Based on the tool results above, please provide a clear and concise final answer to the user's question."
                ))

                final_response = await self.llm_service.chat(messages)

                execution_results.append("\n---\n\n")
                execution_results.append(f"**最终答案：**\n\n{final_response.content}")

            except Exception as e:
                logger.error(f"Failed to get final answer: {e}")

        return "\n".join(execution_results)

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

**Plan Confirmation Mode:**
- `/confirm_mode` - Toggle plan confirmation mode (current: {})
- `/auto_mode` - Enable automatic execution (no confirmation)
- `/plan_mode` - Enable plan confirmation mode (default)

**Skills Commands:**
- `/skills` - List available skills
- `/skill <skill_id> [params]` - Execute a skill (JSON format for params)
- `/skill_info <skill_id>` - Get detailed information about a skill

**MCP Commands:**
- `/mcp_list` - List available MCP tools
- `/mcp_call <tool_name> [args]` - Call an MCP tool

**Example:**
`/skill calculate {"expression": "2 + 2 * 3"}`
""".format("✅ 已启用" if self.require_confirmation else "❌ 已禁用")

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

        elif command in ['/confirm_mode', '/plan_mode']:
            self.require_confirmation = True
            return "✅ **计划确认模式已启用**\n\n工具调用前会先向您展示执行计划，等待您的确认。"

        elif command == '/auto_mode':
            self.require_confirmation = False
            return "⚡ **自动执行模式已启用**\n\n工具将直接执行，不会请求确认。"

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
