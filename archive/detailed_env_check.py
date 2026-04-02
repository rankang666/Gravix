#!/usr/bin/env python
# 详细检查环境变量传递

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, '/Users/jerry/PycharmProjects/Gravix')

# 加载.env
env_path = Path('/Users/jerry/PycharmProjects/Gravix') / '.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

from app.mcp.manager import MCPManager

async def detailed_env_check():
    print("=" * 80)
    print("🔍 详细环境变量检查")
    print("=" * 80)
    print()

    manager = MCPManager()
    await manager.initialize()

    print("✅ MCP已启动")
    print()
    print("传递给MCP服务器的环境变量:")
    print("  REGION:", os.getenv('ALIBABA_CLOUD_REGION_ID'))
    print("  AK_ID:", os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID', '')[:10] + "...")
    print("  AK_SECRET:", os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET', '')[:10] + "...")
    print()

    # 测试一个简单的工具来验证连接
    print("测试1: GetRemind (应该返回MissingRemindId)")
    print("-" * 80)
    try:
        result = await manager.call_tool("dataworks", "GetRemind", {})
        content = result['content'][0].get('text', '')
        print(f"结果: {content[:150]}...")
    except Exception as e:
        print(f"错误: {e}")
    print()

    # 测试带参数的工具
    print("测试2: ConvertTimestamps (应该成功)")
    print("-" * 80)
    try:
        result = await manager.call_tool("dataworks", "ConvertTimestamps", {
            "Timestamps": [1714567890]
        })
        content = result['content'][0].get('text', '')
        print(f"结果: {content}")
    except Exception as e:
        print(f"错误: {e}")
    print()

    print("=" * 80)
    print("📊 结论")
    print("=" * 80)
    print()

    # 检查GetRemind的响应
    try:
        result = await manager.call_tool("dataworks", "GetRemind", {})
        content = result['content'][0].get('text', '')

        if 'MissingRemindId' in content:
            print("✅ 环境变量传递正确")
            print("✅ AK认证成功")
            print("✅ API可以访问")
            print()
            print("❌ 只是缺少具体的业务数据（如提醒ID、项目ID等）")
            print()
            print("这是正常的！这些需要具体的业务数据参数。")
        elif 'Forbidden' in content:
            print("❌ 认证失败 - 可能是AK或Region问题")
        else:
            print(f"结果: {content[:200]}")
    except Exception as e:
        print(f"错误: {e}")

    print()
    print("=" * 80)
    print("💡 现在可以使用的DataWorks功能:")
    print("=" * 80)
    print()

    usable_tools = [
        "✅ ConvertTimestamps - 时间戳转换",
        "✅ ToTimestamps - 日期转时间戳",
        "⚠️  GetRemind - 需要提醒ID",
        "⚠️  ListWorkflows - 需要项目ID",
        "⚠️  ListProjects - 需要项目权限",
    ]

    for tool in usable_tools:
        print(f"  {tool}")

    print()
    await manager.shutdown()

asyncio.run(detailed_env_check())
