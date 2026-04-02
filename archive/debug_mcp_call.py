#!/usr/bin/env python
# 调试MCP工具调用

import asyncio
import sys
sys.path.insert(0, '/Users/jerry/PycharmProjects/Gravix')

from app.mcp.manager import MCPManager
import os
from pathlib import Path

# 加载环境变量
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

async def debug_mcp_call():
    print("=" * 80)
    print("调试MCP工具调用")
    print("=" * 80)
    print()

    manager = MCPManager()

    try:
        await manager.initialize()
        print("✅ MCP Manager initialized")
        print()

        # 测试不同的调用方式
        test_calls = [
            ("无参数", "ListProjects", {}),
            ("空字典", "ListProjects", {}),
            ("明确指定空参数", "ListProjects", None),
        ]

        for desc, tool_name, params in test_calls:
            print(f"测试: {desc}")
            print(f"  工具: {tool_name}")
            print(f"  参数: {params}")

            try:
                if params is None:
                    result = await manager.call_tool("dataworks", tool_name, {})
                else:
                    result = await manager.call_tool("dataworks", tool_name, params)

                print(f"  ✅ 成功")
                print(f"  结果: {str(result)[:200]}...")
            except Exception as e:
                print(f"  ❌ 错误: {e}")

            print()

    except Exception as e:
        print(f"❌ 初始化失败: {e}")
    finally:
        await manager.shutdown()

asyncio.run(debug_mcp_call())
