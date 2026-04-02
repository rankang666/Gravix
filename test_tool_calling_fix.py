#!/usr/bin/env python
# 测试工具调用修复

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

from app.chat.tool_calling import ToolCallParser, ToolExecutor, ToolCall
from app.mcp.manager import MCPManager
from app.chat.integration.mcp_bridge import MCPBridge

async def test_tool_calling():
    print("=" * 80)
    print("🔍 测试工具调用")
    print("=" * 80)
    print()

    # 初始化 MCP
    manager = MCPManager()
    await manager.initialize()
    mcp_bridge = MCPBridge(manager)

    # 创建执行器
    executor = ToolExecutor(None, mcp_bridge)

    # 测试1: 解析工具调用格式
    print("测试1: 解析工具调用格式")
    print("-" * 80)

    test_cases = [
        "::dataworks.ListProjects{}",
        "::dataworks.ListProjects{ProjectId=9335}",
        "::dataworks.ConvertTimestamps{Timestamps=[1714567890]}",
    ]

    for test_input in test_cases:
        print(f"输入: {test_input}")
        calls = ToolCallParser.parse(test_input)
        for call in calls:
            print(f"  工具: {call.tool_name}")
            print(f"  参数: {call.parameters}")
        print()

    # 测试2: 执行工具调用
    print("测试2: 执行工具调用")
    print("-" * 80)

    test_calls = [
        ToolCall("ConvertTimestamps", {"Timestamps": [1714567890]}),
        ToolCall("dataworks.ListProjects", {}),
    ]

    for call in test_calls:
        print(f"调用: {call.tool_name}")
        try:
            result = await executor.execute(call)
            print(f"  ✅ 成功")
            if isinstance(result, dict):
                if 'content' in result and len(result['content']) > 0:
                    content = result['content'][0].get('text', '')[:200]
                    print(f"  结果: {content}...")
                else:
                    print(f"  结果: {str(result)[:200]}...")
            else:
                print(f"  结果: {str(result)[:200]}...")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:200]}")
        print()

    # 测试3: MCPBridge 直接调用
    print("测试3: MCPBridge 直接调用")
    print("-" * 80)

    try:
        print("调用: ConvertTimestamps")
        result = await mcp_bridge.call_tool("ConvertTimestamps", {"Timestamps": [1714567890]}, "dataworks")
        print(f"  ✅ 成功: {result}")
    except Exception as e:
        print(f"  ❌ 错误: {e}")
    print()

    try:
        print("调用: dataworks.ListProjects (通过manager)")
        result = await manager.call_tool("dataworks", "ListProjects", {})
        print(f"  ✅ 成功: {str(result)[:300]}...")
    except Exception as e:
        print(f"  ❌ 错误: {str(e)[:200]}")
    print()

    await manager.shutdown()

asyncio.run(test_tool_calling())
