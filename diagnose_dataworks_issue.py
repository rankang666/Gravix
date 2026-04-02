#!/usr/bin/env python
# DataWorks问题诊断

print("=" * 80)
print("🔍 DataWorks MCP 问题诊断")
print("=" * 80)
print()

print("可能的原因:")
print()

print("1. ✅ AK配置正确")
print("   - AK已成功连接到DataWorks API")
print("   - 错误400说明请求到达了服务器，但参数有问题")
print()

print("2. ❌ RegionId传递问题")
print("   - DataWorks MCP可能没有正确读取环境变量中的RegionId")
print("   - 需要检查MCP服务器的配置方式")
print()

print("3. ❌ 项目权限问题")
print("   - 该AK可能没有访问cn-hangzhou区域的任何DataWorks项目")
print("   - 或者该Region下没有项目")
print()

print("4. ❌ DataWorks MCP配置问题")
print("   - MCP服务器可能需要额外的配置文件")
print("   - 或者需要通过命令行参数传递RegionId")
print()

print("=" * 80)
print("解决方案")
print("=" * 80)
print()

print("方案1: 检查AK是否有DataWorks项目")
print("  - 登录阿里云控制台: https://dataworks.console.aliyun.com/")
print("  - 检查cn-hangzhou区域是否有项目")
print("  - 确认AK是否有这些项目的访问权限")
print()

print("方案2: 尝试其他Region")
print("  编辑.env文件，尝试不同的Region:")
print("  ALIBABA_CLOUD_REGION_ID=cn-beijing")
print("  ALIBABA_CLOUD_REGION_ID=cn-shanghai")
print("  ALIBABA_CLOUD_REGION_ID=cn-shenzhen")
print()

print("方案3: 使用不需要项目的工具")
print("  某些DataWorks API可能不需要项目上下文")
print("  - /mcp_call ConvertTimestamps")
print("  - /mcp_call ToTimestamps")
print()

print("方案4: 检查DataWorks MCP文档")
print("  https://github.com/aliyun/alibabacloud-dataworks-mcp-server")
print("  查看是否需要额外的配置")
print()

print("方案5: 使用内置Skills（推荐，立即可用）")
print("  - /skills")
print("  - /skill calculate 2+2*3")
print("  - /skill system_info all")
print()

print("=" * 80)
print("建议的下一步")
print("=" * 80)
print()

print("1. 访问DataWorks控制台，确认:")
print("   - AK是否有项目访问权限")
print("   - cn-hangzhou区域是否有项目")
print()

print("2. 如果没有项目，可以先:")
print("   - 创建一个DataWorks项目")
print("   - 或者尝试其他Region")
print()

print("3. 暂时使用内置的4个Skills:")
print("   - calculate: 数学计算")
print("   - system_info: 系统信息")
print("   - echo: 消息回显")
print("   - funboost_task: 任务队列")
print()

print("=" * 80)
