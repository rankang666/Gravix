#!/usr/bin/env python
# 测试不同的DataWorks调用方式

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

async def test_region_fix():
    print("=" * 80)
    print("测试DataWorks RegionId修复")
    print("=" * 80)
    print()

    manager = MCPManager()
    await manager.initialize()

    # 尝试不同的参数组合
    test_cases = [
        ("无参数", "ListProjects", {}),
        ("带RegionId", "ListProjects", {"RegionId": "cn-hangzhou"}),
        ("带空PageNumber", "ListProjects", {"PageNumber": 1, "PageSize": 10}),
        ("完整参数", "ListProjects", {"RegionId": "cn-hangzhou", "PageNumber": 1, "PageSize": 10}),
    ]

    for desc, tool, params in test_cases:
        print(f"测试: {desc}")
        print(f"  参数: {params}")

        try:
            result = await manager.call_tool("dataworks", tool, params)
            content = result['content'][0].get('text', '')

            # 检查是否成功
            if '"ErrorCode"' in content or 'Failed' in content:
                # 提取错误信息
                import json
                try:
                    error_data = json.loads(content)
                    print(f"  ❌ 失败: {error_data.get('body', 'Unknown error')[:100]}...")
                except:
                    print(f"  ❌ 失败: {content[:100]}...")
            else:
                print(f"  ✅ 成功!")
                print(f"  结果预览: {content[:100]}...")
        except Exception as e:
            print(f"  ❌ 错误: {str(e)[:100]}")

        print()

    await manager.shutdown()

asyncio.run(test_region_fix())
