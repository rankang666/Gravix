#!/usr/bin/env python
# 测试DataWorks完整工作流

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

async def test_workflow():
    print("=" * 80)
    print("🔍 DataWorks 工作流完整测试")
    print("=" * 80)
    print()

    manager = MCPManager()
    await manager.initialize()

    # 第1步：列出所有项目（如果有的话）
    print("第1步：列出可用的DataWorks项目")
    print("-" * 80)

    try:
        result = await manager.call_tool("dataworks", "ListProjects", {
            "PageNumber": 1,
            "PageSize": 10
        })
        content = result['content'][0].get('text', '')
        print(f"结果: {content[:300]}...")
        print()

        # 检查是否有项目
        import json
        try:
            data = json.loads(content)
            if 'ErrorCode' in str(data):
                print("⚠️  无法列出项目")
                print("可能原因：")
                print("1. 该Region下没有DataWorks项目")
                print("2. AK没有列出项目的权限")
                print()
                print("建议：")
                print("- 访问 https://dataworks.console.aliyun.com/")
                print("- 创建一个DataWorks项目")
                print("- 或使用有项目权限的AK")
                print()
                return
        except:
            pass

    except Exception as e:
        print(f"❌ 列出项目失败: {e}")
        print()
        return

    # 第2步：列出工作流（假设有项目）
    print("第2步：列出工作流")
    print("-" * 80)
    print("注意：ListWorkflows需要指定项目参数")
    print()

    # 显示工具的参数要求
    tools = await manager.list_tools("dataworks")
    list_workflows = next((t for t in tools if t.get('name') == 'ListWorkflows'), None)

    if list_workflows:
        print("ListWorkflows 工具参数要求:")
        print(json.dumps(list_workflows.get('inputSchema', {}), indent=2, ensure_ascii=False))
        print()

    print("常见参数:")
    print("- ProjectName: 项目名称")
    print("- PageNumber: 页码")
    print("- PageSize: 每页数量")
    print()

    # 第3步：演示其他可用工具
    print("第3步：测试其他无需项目的工具")
    print("-" * 80)

    other_tools = [
        ("ConvertTimestamps", {"Timestamps": [1714567890, 1714567891]}),
        ("GetRemind", {}),
    ]

    for tool_name, params in other_tools:
        print(f"工具: {tool_name}")
        try:
            result = await manager.call_tool("dataworks", tool_name, params)
            content = result['content'][0].get('text', '')
            print(f"  ✅ 成功: {content[:100]}...")
        except Exception as e:
            print(f"  ❌ 失败: {str(e)[:100]}...")
        print()

    await manager.shutdown()

asyncio.run(test_workflow())
