#!/usr/bin/env python
# 测试指定ProjectId的工具调用

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

async def test_with_project_id():
    print("=" * 80)
    print("🔍 测试 ProjectId=9335")
    print("=" * 80)
    print()

    manager = MCPManager()
    await manager.initialize()

    project_id = "9335"

    # 测试ListWorkflows
    print(f"测试1: ListWorkflows with ProjectId={project_id}")
    print("-" * 80)

    try:
        result = await manager.call_tool("dataworks", "ListWorkflows", {
            "ProjectId": project_id,
            "PageNumber": 1,
            "PageSize": 10
        })

        content = result['content'][0].get('text', '')

        # 尝试解析结果
        try:
            data = json.loads(content)
            if 'ErrorCode' in str(data) or 'Failed' in str(data):
                print(f"❌ 调用失败")
                print(f"错误: {str(data)[:300]}...")
            else:
                print(f"✅ 调用成功!")
                # 美化输出
                if 'Data' in data and isinstance(data['Data'], list):
                    workflows = data['Data']
                    print(f"   找到 {len(workflows)} 个工作流:")
                    for wf in workflows[:5]:
                        print(f"   - {wf.get('Name', 'N/A')}: {wf.get('Status', 'N/A')}")
                    if len(workflows) > 5:
                        print(f"   ... 还有 {len(workflows) - 5} 个")
                else:
                    print(f"   结果: {str(data)[:300]}...")
        except json.JSONDecodeError:
            print(f"结果: {content[:300]}...")

    except Exception as e:
        print(f"❌ 异常: {str(e)[:200]}...")

    print()

    # 测试ListTasks
    print(f"测试2: ListTasks with ProjectId={project_id}")
    print("-" * 80)

    try:
        result = await manager.call_tool("dataworks", "ListTasks", {
            "ProjectId": project_id,
            "PageNumber": 1,
            "PageSize": 5
        })

        content = result['content'][0].get('text', '')

        try:
            data = json.loads(content)
            if 'ErrorCode' in str(data) or 'Failed' in str(data):
                print(f"❌ 调用失败")
                print(f"错误: {str(data)[:300]}...")
            else:
                print(f"✅ 调用成功!")
                if 'Data' in data and isinstance(data['Data'], list):
                    tasks = data['Data']
                    print(f"   找到 {len(tasks)} 个任务:")
                    for task in tasks[:5]:
                        print(f"   - {task.get('Name', 'N/A')}: {task.get('Status', 'N/A')}")
                    if len(tasks) > 5:
                        print(f"   ... 还有 {len(tasks) - 5} 个")
                else:
                    print(f"   结果: {str(data)[:300]}...")
        except json.JSONDecodeError:
            print(f"结果: {content[:300]}...")

    except Exception as e:
        print(f"❌ 异常: {str(e)[:200]}...")

    print()
    await manager.shutdown()

asyncio.run(test_with_project_id())
