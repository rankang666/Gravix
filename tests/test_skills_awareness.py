#!/usr/bin/env python
# encoding: utf-8
"""
测试LLM是否感知到Skills
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_skills():
    """测试Skills感知"""

    uri = "ws://localhost:8765"

    print("=" * 80)
    print("测试LLM对Skills的感知")
    print("=" * 80)
    print()

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到服务器")
            print()

            # 接收欢迎消息
            welcome = await websocket.recv()
            print(f"服务器: {welcome}")
            print()

            # 测试问题
            test_questions = [
                "你有哪些技能可以用？",
                "帮我计算 2 + 2 * 3",
                "查看系统信息",
                "echo hello"
            ]

            for question in test_questions:
                print(f"发送: {question}")
                print()

                await websocket.send(json.dumps({
                    'type': 'chat',
                    'content': question,
                    'timestamp': datetime.utcnow().isoformat()
                }))

                response = await websocket.recv()
                data = json.loads(response)

                print(f"接收: {data.get('content', 'No content')}")
                print("-" * 80)
                print()

            print("=" * 80)
            print("测试完成")
            print("=" * 80)

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == '__main__':
    try:
        asyncio.run(test_skills())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
