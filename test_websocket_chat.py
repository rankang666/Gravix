#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: test_websocket_chat.py
@Author: Jerry
@Software: PyCharm
@Desc: 测试WebSocket聊天功能
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_chat():
    """测试WebSocket聊天"""

    uri = "ws://localhost:8765"

    print("=" * 80)
    print("Gravix WebSocket 聊天测试")
    print("=" * 80)
    print()
    print(f"连接到: {uri}")
    print()

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 已连接到服务器")
            print()

            # 接收欢迎消息
            welcome = await websocket.recv()
            print(f"服务器: {welcome}")
            print()

            # 测试对话
            test_messages = [
                "你好",
                "1+1等于几？",
                "介绍一下DataWorks"
            ]

            for msg in test_messages:
                print(f"发送: {msg}")

                # 发送消息
                await websocket.send(json.dumps({
                    'type': 'chat',
                    'content': msg,
                    'timestamp': datetime.utcnow().isoformat()
                }))

                # 接收响应
                response = await websocket.recv()
                data = json.loads(response)

                print(f"接收: {data.get('content', 'No content')}")
                print("-" * 40)
                print()

            print("=" * 80)
            print("✅ 聊天测试完成！")
            print("=" * 80)

    except websockets.exceptions.ConnectionRefused:
        print("❌ 无法连接到服务器")
        print("请确保Gravix服务正在运行: python run_all.py")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(test_chat())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
