#!/usr/bin/env python
# 显示工具的参数要求

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, '/Users/jerry/PycharmProjects/Gravix')

# 加载环境变量
env_path = Path('/Users/jerry/PycharmProjects/Gravix') / '.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

from app.mcp.manager import MCPManager
import json

async def show_tool_params():
    print("=" * 80)
    print("📋 DataWorks工具参数要求详情")
    print("=" * 80)
    print()

    manager = MCPManager()
    await manager.initialize()

    # 获取所有工具
    tools = await manager.list_tools("dataworks")

    # 重点关注的工具
    focus_tools = [
        "ListProjects",
        "ListWorkflows", 
        "ListTasks",
        "GetTable",
        "GetRemind"
    ]

    print("重点工具的参数要求:")
    print()

    for tool in tools:
        tool_name = tool.get('name')
        if tool_name in focus_tools:
            print(f"🔧 {tool_name}")
            print(f"   描述: {tool.get('description', 'N/A')}")
            print(f"   必需参数:")

            schema = tool.get('inputSchema', {})
            properties = schema.get('properties', {})
            required = schema.get('required', [])

            if required:
                for param in required:
                    if param in properties:
                        prop = properties[param]
                        print(f"     - {param}:")
                        print(f"       {prop.get('description', 'N/A')}")
            else:
                print("     (无必需参数)")

            print()

    await manager.shutdown()

asyncio.run(show_tool_params())
