#!/usr/bin/env python
# encoding: utf-8
"""
测试真正的工具调用
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_tool_calling():
    """测试工具调用"""

    uri = "ws://localhost:8765"

    print("=" * 80)
    print("测试真正的工具调用")
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

            # 测试工具调用
            test_messages = [
                "帮我计算 15 + 27 * 3",
                "查看系统CPU使用率",
                "echo 这是测试消息"
            ]

            for msg in test_messages:
                print(f"发送: {msg}")
                print()

                await websocket.send(json.dumps({
                    'type': 'chat',
                    'content': msg,
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
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(test_tool_calling())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
