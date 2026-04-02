#!/usr/bin/env python
# 测试环境变量名称

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, '/Users/jerry/PycharmProjects/Gravix')

# 加载.env
env_path = Path('/Users/jerry/PycharmProjects/Gravix') / '.env'
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            os.environ[key.strip()] = value.strip()

print("=" * 80)
print("🔍 检查环境变量传递")
print("=" * 80)
print()

print("期望的环境变量（从您的配置）:")
print("  REGION")
print("  ALIBABA_CLOUD_ACCESS_KEY_ID")
print("  ALIBABA_CLOUD_ACCESS_KEY_SECRET")
print()

print("当前.env文件中的变量:")
aliyun_vars = {k: v for k, v in os.environ.items() if 'ALIBABA' in k or 'REGION' in k.upper()}
for key, value in aliyun_vars.items():
    if 'SECRET' in key:
        print(f"  {key}: {value[:10]}...{value[-4:]}")
    else:
        print(f"  {key}: {value}")
print()

print("=" * 80)
print("测试不同的环境变量组合")
print("=" * 80)
print()

# 测试不同的变量名组合
test_configs = [
    {
        "name": "当前配置",
        "env": {
            "ALIBABA_CLOUD_REGION_ID": os.getenv('ALIBABA_CLOUD_REGION_ID'),
            "ALIBABA_CLOUD_ACCESS_KEY_ID": os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET": os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        }
    },
    {
        "name": "标准配置",
        "env": {
            "REGION": os.getenv('ALIBABA_CLOUD_REGION_ID'),
            "ALIBABA_CLOUD_ACCESS_KEY_ID": os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET": os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        }
    },
    {
        "name": "深圳Region",
        "env": {
            "REGION": "cn-shenzhen",
            "ALIBABA_CLOUD_ACCESS_KEY_ID": os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID'),
            "ALIBABA_CLOUD_ACCESS_KEY_SECRET": os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET'),
        }
    },
]

for i, config in enumerate(test_configs, 1):
    print(f"测试 {i}: {config['name']}")
    print(f"  REGION: {config['env'].get('REGION') or config['env'].get('ALIBABA_CLOUD_REGION_ID')}")
    print(f"  AK: {config['env'].get('ALIBABA_CLOUD_ACCESS_KEY_ID', '')[:10]}...")
    print()

print("=" * 80)
