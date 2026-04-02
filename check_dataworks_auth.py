#!/usr/bin/env python
# 检查DataWorks认证配置

import os
from pathlib import Path

print("=" * 80)
print("DataWorks 认证配置检查")
print("=" * 80)
print()

# 检查阿里云凭证
aliyun_vars = {
    'ALIBABA_CLOUD_ACCESS_KEY_ID': 'Access Key ID',
    'ALIBABA_CLOUD_ACCESS_KEY_SECRET': 'Access Key Secret',
    'ALIBABA_CLOUD_REGION_ID': 'Region ID',
}

print("阿里云凭证状态:")
all_set = True
for var, desc in aliyun_vars.items():
    value = os.getenv(var)
    if value:
        print(f"  ✅ {desc}: 已设置")
    else:
        print(f"  ❌ {desc}: 未设置")
        all_set = False

print()

if not all_set:
    print("⚠️  缺少阿里云凭证")
    print()
    print("DataWorks MCP需要阿里云凭证才能调用API。")
    print()
    print("设置方法:")
    print("1. 访问阿里云控制台创建AccessKey")
    print("2. 设置环境变量:")
    print("   export ALIBABA_CLOUD_ACCESS_KEY_ID='your-key-id'")
    print("   export ALIBABA_CLOUD_ACCESS_KEY_SECRET='your-key-secret'")
    print()
    print("3. 或在 ~/.aliyun/config.json 中配置凭证")
    print()
    print("获取AccessKey:")
    print("https://usercenter.console.aliyun.com/#/manage/ak")
else:
    print("✅ 阿里云凭证已配置")
    print()
    print("您现在可以调用DataWorks API了")
    print()
    print("示例调用:")
    print("  /mcp_call ListProjects")
    print("  /mcp_call ListTables")

print()
print("=" * 80)
