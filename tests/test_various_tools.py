#!/usr/bin/env python
# 测试不同的DataWorks工具

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

async def test_various_tools():
    print("=" * 80)
    print("测试各种DataWorks工具")
    print("=" * 80)
    print()

    manager = MCPManager()
    await manager.initialize()

    # 测试不同的工具
    tools_to_test = [
        ("ListProjects", "列出项目（可能需要RegionId）", {}),
        ("GetRemind", "获取提醒信息", {}),
        ("ListProjectRoles", "列出项目角色", {}),
        ("ListDataSources", "列出数据源", {}),
    ]

    for tool_name, desc, params in tools_to_test:
        print(f"工具: {tool_name}")
        print(f"描述: {desc}")

        try:
            result = await manager.call_tool("dataworks", tool_name, params)
            content = result['content'][0].get('text', '')

            # 检查结果
            import json
            try:
                data = json.loads(content)
                if 'ErrorCode' in str(data) or 'Failed' in str(data):
                    print(f"  ❌ 错误: {str(data)[:150]}...")
                elif 'data' in data or 'Data' in str(data):
                    print(f"  ✅ 成功!")
                    print(f"  结果: {str(data)[:200]}...")
                else:
                    print(f"  结果: {str(data)[:200]}...")
            except json.JSONDecodeError:
                print(f"  结果: {content[:200]}...")

        except Exception as e:
            print(f"  ❌ 异常: {str(e)[:100]}")

        print("-" * 80)
        print()

    await manager.shutdown()

asyncio.run(test_various_tools())
