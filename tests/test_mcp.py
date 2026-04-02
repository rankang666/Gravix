#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: test_mcp.py
@Author: Jerry
@Software: PyCharm
@Desc: Test MCP connection
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.mcp.manager import MCPManager
from app.utils.logger import logger


async def test_mcp():
    """Test MCP connection"""

    logger.info("=" * 60)
    logger.info("Testing MCP Connection")
    logger.info("=" * 60)

    # Initialize MCP Manager
    manager = MCPManager()

    try:
        # Connect to MCP servers
        await manager.initialize()

        # Get connected servers
        servers = manager.get_connected_servers()
        logger.info(f"\n✅ Connected to {len(servers)} MCP server(s)")

        # List tools from all servers
        logger.info("\n" + "=" * 60)
        logger.info("Available Tools")
        logger.info("=" * 60)

        all_tools = await manager.list_all_tools()

        for server_name, tools in all_tools.items():
            logger.info(f"\n📦 {server_name} - {len(tools)} tools:")
            for i, tool in enumerate(tools[:10], 1):
                tool_name = tool.get('name', 'N/A')
                tool_desc = tool.get('description', 'N/A')
                logger.info(f"  {i}. {tool_name}")
                logger.info(f"     {tool_desc[:80]}")

            if len(tools) > 10:
                logger.info(f"  ... and {len(tools) - 10} more tools")

        logger.info("\n" + "=" * 60)
        logger.info("✅ MCP Test Completed Successfully!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ MCP Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        await manager.shutdown()


if __name__ == '__main__':
    try:
        asyncio.run(test_mcp())
    except KeyboardInterrupt:
        logger.info("\nTest interrupted")
