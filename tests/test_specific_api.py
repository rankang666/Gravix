#!/usr/bin/env python
# encoding: utf-8
"""
测试不同的API调用，找出哪个导致403错误
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Load env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

from anthropic import Anthropic
from app.utils.logger import logger


async def test_api_calls():
    """测试不同的API调用"""

    api_key = os.getenv('ANTHROPIC_API_KEY')
    print(f"使用API密钥: {api_key[:10]}...{api_key[-4:]}")
    print()

    client = Anthropic(api_key=api_key)

    tests = [
        {
            'name': '测试1: Haiku模型 (最便宜)',
            'model': 'claude-3-5-haiku-20241022',
            'prompt': 'Hi'
        },
        {
            'name': '测试2: Sonnet模型 (推荐)',
            'model': 'claude-3-5-sonnet-20241022',
            'prompt': 'Hi'
        },
        {
            'name': '测试3: Opus模型 (最强大)',
            'model': 'claude-3-opus-20240229',
            'prompt': 'Hi'
        },
        {
            'name': '测试4: Sonnet + 中文',
            'model': 'claude-3-5-sonnet-20241022',
            'prompt': '你好'
        },
        {
            'name': '测试5: Sonnet + 较长文本',
            'model': 'claude-3-5-sonnet-20241022',
            'prompt': '请详细介绍一下你自己'
        }
    ]

    for test in tests:
        print("=" * 80)
        print(test['name'])
        print("=" * 80)

        try:
            response = client.messages.create(
                model=test['model'],
                max_tokens=100,
                messages=[{"role": "user", "content": test['prompt']}]
            )

            print("✅ 成功")
            print(f"响应: {response.content[0].text[:100]}...")
            print()

        except Exception as e:
            error_str = str(e)

            if '403' in error_str or 'forbidden' in error_str.lower():
                print(f"❌ 403 Forbidden 错误")
                print(f"错误详情: {error_str}")
                print()
                print("这个配置导致了403错误，可能的原因:")
                print("1. API密钥对此模型/请求没有权限")
                print("2. 账户配额限制")
                print("3. 触发了安全策略")
                print()
            else:
                print(f"❌ 其他错误: {e}")
                print()

        await asyncio.sleep(0.5)  # 避免请求过快


if __name__ == '__main__':
    try:
        asyncio.run(test_api_calls())
    except KeyboardInterrupt:
        print("\n\n测试已中断")
