#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: test_llm_chat.py
@Author: Jerry
@Software: PyCharm
@Desc: 测试LLM聊天功能
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.llm.service import LLMService
from app.llm.base import Message
from app.utils.logger import logger


async def test_llm():
    """测试LLM服务"""

    print("=" * 80)
    print("Gravix LLM 聊天测试")
    print("=" * 80)
    print()

    # 加载环境变量
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        print(f"✅ 加载环境变量: {env_path}")
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print("⚠️  .env 文件不存在")
        return

    provider = os.getenv('LLM_PROVIDER', 'claude')
    print(f"✅ LLM提供商: {provider}")
    print()

    try:
        print("正在初始化LLM服务...")
        service = LLMService(provider=provider)

        print("✅ LLM服务初始化成功")
        print()

        # 测试对话
        print("发送测试消息: '你好，请介绍一下自己'")
        print()

        messages = [
            Message(role='user', content='你好，请介绍一下自己')
        ]

        response = await service.chat(messages)

        print("=" * 80)
        print("AI 回复:")
        print("=" * 80)
        print()
        print(response.content)
        print()
        print("=" * 80)
        print("✅ LLM服务工作正常！")
        print("=" * 80)

    except Exception as e:
        print()
        print("❌ LLM服务测试失败")
        print(f"错误: {e}")
        print()
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(test_llm())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
