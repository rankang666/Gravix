#!/usr/bin/env python
# encoding: utf-8
"""
调试403错误 - 检查所有可能的API调用来源
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# 加载环境变量
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    print(f"✅ 找到.env文件: {env_path}")
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()
else:
    print("❌ 未找到.env文件")

print()
print("=" * 80)
print("环境变量检查")
print("=" * 80)
print()

# 检查所有可能的环境变量
all_vars = os.environ.copy()

api_keys = {k: v for k, v in all_vars.items() if 'API' in k or 'KEY' in k.upper()}

print("所有API相关环境变量:")
for key, value in sorted(api_keys.items()):
    if 'SECRET' in key or 'KEY' in key:
        print(f"  {key}: {value[:10]}...{value[-4:]}")
    else:
        print(f"  {key}: {value}")

print()
print("=" * 80)
print("测试API调用")
print("=" * 80)
print()

from anthropic import Anthropic

api_key = os.getenv('ANTHROPIC_API_KEY')
print(f"使用API密钥: {api_key[:10]}...{api_key[-4:]}")
print()

# 测试不同的调用方式
client = Anthropic(api_key=api_key)

tests = [
    ("简单文本", "Hi", "claude-3-5-haiku-20241022"),
    ("中文文本", "你好", "claude-3-5-sonnet-20241022"),
    ("较长文本", "请详细介绍一下你自己", "claude-3-5-sonnet-20241022"),
]

for name, prompt, model in tests:
    print(f"测试: {name}")
    print(f"  模型: {model}")
    print(f"  提示: {prompt}")

    try:
        response = client.messages.create(
            model=model,
            max_tokens=50,
            messages=[{"role": "user", "content": prompt}]
        )
        print(f"  ✅ 成功")
        print(f"  响应: {response.content[0].text[:50]}...")

    except Exception as e:
        error_str = str(e)
        if '403' in error_str or 'forbidden' in error_str.lower():
            print(f"  ❌ 403 Forbidden")
            print(f"  详情: {error_str[:200]}")
        else:
            print(f"  ❌ 错误: {error_str[:100]}")

    print()

print("=" * 80)
print("诊断建议")
print("=" * 80)
print()

print("如果所有测试都通过，但Web UI仍然报403错误，可能的原因:")
print()
print("1. Web UI使用了不同的API密钥")
print("2. Web UI直接调用了Anthropic API而不是通过服务器")
print("3. 浏览器缓存了旧的配置")
print("4. 存在多个.env文件，Web UI使用了错误的那个")
print()
print("建议:")
print("1. 清除浏览器缓存")
print("2. 检查Web UI的API配置")
print("3. 确保Web UI通过WebSocket连接到服务器，而不是直接调用API")
