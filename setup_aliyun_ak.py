#!/usr/bin/env python
# 配置阿里云AK的向导

import os
from pathlib import Path

print("=" * 80)
print("🔑 阿里云AK配置向导")
print("=" * 80)
print()

print("请按照以下步骤配置您的阿里云凭证:")
print()

print("步骤1: 打开 .env 文件")
print(f"  文件位置: {Path(__file__).parent / '.env'}")
print()

print("步骤2: 找到以下3行:")
print("  ALIBABA_CLOUD_ACCESS_KEY_ID=your-access-key-id-here")
print("  ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-access-key-secret-here")
print("  ALIBABA_CLOUD_REGION_ID=cn-hangzhou")
print()

print("步骤3: 替换为您的真实凭证:")
print()
print("  示例:")
print("  ALIBABA_CLOUD_ACCESS_KEY_ID=LTAI5tQxxxxxxxxxx")
print("  ALIBABA_CLOUD_ACCESS_KEY_SECRET=3xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print("  ALIBABA_CLOUD_REGION_ID=cn-hangzhou")
print()

print("常用Region ID:")
regions = {
    'cn-hangzhou': '华东1（杭州）',
    'cn-shanghai': '华东2（上海）',
    'cn-qingdao': '华北1（青岛）',
    'cn-beijing': '华北2（北京）',
    'cn-zhangjiakou': '华北3（张家口）',
    'cn-shenzhen': '华南1（深圳）',
    'cn-heyuan': '华南2（河源）',
    'cn-guangzhou': '华南3（广州）',
    'cn-chengdu': '西南1（成都）',
}

for code, name in regions.items():
    print(f"  {code}: {name}")

print()
print("=" * 80)
print("步骤4: 保存文件后重启服务")
print()

# 检查是否已经配置
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        content = f.read()
        if 'your-access-key-id-here' in content:
            print("⚠️  检测到您还没有填写真实的AK")
        else:
            if 'ALIBABA_CLOUD_ACCESS_KEY_ID=' in content:
                print("✅ 检测到阿里云AK已配置")
                # 检查值是否为空
                lines = content.split('\n')
                for line in lines:
                    if 'ALIBABA_CLOUD_ACCESS_KEY_ID=' in line and line.strip() and not line.endswith('here'):
                        key_id = line.split('=')[1].strip()
                        if key_id:
                            print(f"   Access Key ID: {key_id[:8]}...")
            else:
                print("⚠️  未检测到阿里云AK配置")

print()
print("=" * 80)
print("配置完成后，使用以下命令重启服务:")
print()
print("  pkill -9 -f 'python.*run_all'")
print("  /opt/miniconda3/envs/owner/bin/python run_all.py")
print()
print("=" * 80)
