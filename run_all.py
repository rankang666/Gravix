#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: run_all.py
@Author: Claude
@Software: PyCharm
@Desc: Start all Gravix services
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded environment variables from {env_path}")

load_env()

from app.chat.server import ChatServer
from app.skills.executor import SkillExecutor
from app.skills.registry import SkillRegistry
from app.chat.integration.skills_bridge import SkillsBridge
from app.chat.integration.mcp_bridge import MCPBridge
from app.mcp.manager import MCPManager
from app.llm.service import LLMService
from app.utils.logger import logger


async def start_server():
    """Start the chat server with skills and LLM integration"""

    logger.info("=" * 60)
    logger.info("Starting Gravix Services")
    logger.info("=" * 60)

    # Initialize Skills
    logger.info("Initializing Skills system...")
    registry = SkillRegistry()
    executor = SkillExecutor(registry)
    skills_bridge = SkillsBridge(executor)

    skills_list = registry.list_skills()
    logger.info(f"Loaded {len(skills_list)} skills:")
    for skill in skills_list:
        logger.info(f"  - {skill['skill_id']}: {skill['name']}")

    # Initialize MCP Manager
    logger.info("\nInitializing MCP system...")
    mcp_manager = MCPManager()
    await mcp_manager.initialize()

    connected_servers = mcp_manager.get_connected_servers()
    if connected_servers:
        logger.info(f"✅ Connected to {len(connected_servers)} MCP server(s):")
        for server in connected_servers:
            logger.info(f"  - {server}")

        # List available tools from all servers
        try:
            all_tools = await mcp_manager.list_all_tools()
            for server_name, tools in all_tools.items():
                logger.info(f"\n📦 {server_name} - {len(tools)} tools:")
                for tool in tools[:5]:  # Show first 5 tools
                    logger.info(f"    - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')[:60]}")
                if len(tools) > 5:
                    logger.info(f"    ... and {len(tools) - 5} more tools")
        except Exception as e:
            logger.warning(f"⚠️  Failed to list MCP tools: {e}")

        mcp_bridge = MCPBridge(mcp_manager)
    else:
        logger.warning("⚠️  No MCP servers connected")
        mcp_bridge = None

    # Initialize LLM Service (optional)
    llm_service = None
    llm_provider = os.getenv('LLM_PROVIDER', 'claude').lower()

    if llm_provider and llm_provider != 'none':
        try:
            logger.info(f"\nInitializing LLM service (provider: {llm_provider})...")
            llm_service = LLMService(provider=llm_provider)
            logger.info(f"✅ LLM service ready")
        except Exception as e:
            logger.warning(f"⚠️  LLM service initialization failed: {e}")
            logger.warning("The chat server will work in command-only mode")
            llm_service = None
    else:
        logger.info("\n⚠️  LLM service not configured (set LLM_PROVIDER env var)")
        logger.info("Available providers: claude, openai")

    # Initialize Chat Server
    logger.info("\nInitializing Chat Server...")

    # Load custom system prompt if available
    system_prompt = None
    prompt_file = Path(__file__).parent / 'system_prompt.txt'
    if prompt_file.exists():
        logger.info(f"Loading custom system prompt from {prompt_file}")
        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()
        logger.info(f"✅ Custom system prompt loaded ({len(system_prompt)} chars)")
    else:
        logger.info("Using default system prompt (Plan-First mode)")

    chat_server = ChatServer(
        host="0.0.0.0",
        port=8765,
        skills_bridge=skills_bridge,
        mcp_bridge=mcp_bridge,
        llm_service=llm_service,
        system_prompt=system_prompt
    )

    logger.info("\n" + "=" * 60)
    logger.info("🚀 Gravix Services Ready!")
    logger.info("=" * 60)
    logger.info(f"WebSocket Chat: ws://localhost:8765")
    logger.info(f"Web UI: file://{Path(__file__).parent / 'web' / 'static' / 'index.html'}")

    if llm_service:
        logger.info(f"LLM Provider: {llm_provider}")
        logger.info(f"LLM Model: {llm_service.provider.model if llm_service.provider else 'N/A'}")
    else:
        logger.info("LLM: Not configured (command-only mode)")

    if mcp_bridge:
        logger.info(f"MCP Servers: {', '.join(connected_servers)}")

    logger.info("\nPress Ctrl+C to stop all services")
    logger.info("=" * 60 + "\n")

    try:
        await chat_server.start()
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down Gravix services...")

        # Shutdown MCP connections
        if mcp_manager:
            await mcp_manager.shutdown()

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == '__main__':
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("Services stopped")
