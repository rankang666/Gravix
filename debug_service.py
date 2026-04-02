#!/usr/bin/env python
# encoding: utf-8
"""
检查服务启动时的实际环境变量
"""

import os
import sys
from pathlib import Path

# 模拟run_all.py的加载过程
def load_env():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded environment variables from {env_path}")

load_env()

print("=" * 80)
print("环境变量检查")
print("=" * 80)
print()

# 检查关键环境变量
vars_to_check = [
    'LLM_PROVIDER',
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY'
]

for var in vars_to_check:
    value = os.getenv(var)
    if value:
        if 'KEY' in var:
            # 只显示前后几位
            print(f"✅ {var}: {value[:10]}...{value[-4:]}")
        else:
            print(f"✅ {var}: {value}")
    else:
        print(f"❌ {var}: 未设置")

print()

# 检查是否有冲突的环境变量
print("检查可能的环境变量冲突:")
print()

# 检查python-dotenv是否设置了不同的值
for var in vars_to_check:
    env_value = os.getenv(var)
    if env_value:
        print(f"{var} = {env_value[:20] if 'KEY' in var else env_value}...")

print()
print("=" * 80)
