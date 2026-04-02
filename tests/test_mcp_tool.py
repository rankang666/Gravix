#!/usr/bin/env python
# encoding: utf-8
"""
测试MCP工具调用格式
"""

import asyncio
import sys
sys.path.insert(0, '/Users/jerry/PycharmProjects/Gravix')

from app.chat.tool_calling import ToolCallParser

print("=" * 80)
print("MCP工具调用格式说明")
print("=" * 80)
print()

print("❌ 错误格式（LLM现在输出的）:")
print("   ::dataworks.ListProjects{}")
print("   问题：这只是文本，不是真正的工具调用")
print()

print("✅ 正确格式（应该使用的）:")
print("   对于MCP工具，应该使用：server_name.tool_name")
print("   例如：::dataworks.ListProjects{}")
print()

print("但是，真正的问题是：")
print("   LLM只是输出了这个格式的文本")
print("   工具调用并没有被实际执行！")
print()

print("=" * 80)
print("测试场景")
print("=" * 80)
print()

scenarios = [
    ("描述需求", "列出DataWorks的所有项目", "LLM应该识别并调用工具"),
    ("直接命令", "/mcp_call ListProjects", "使用命令直接调用"),
    ("对话请求", "帮我看一下DataWorks有哪些项目", "自然语言触发工具调用")
]

for scenario, example, expected in scenarios:
    print(f"场景: {scenario}")
    print(f"示例: {example}")
    print(f"期望: {expected}")
    print()

print("=" * 80)
print("当前问题诊断")
print("=" * 80)
print()

print("问题1: LLM输出了工具调用格式，但:")
print("  - 这个格式只是文本")
print("  - 没有被实际解析和执行")
print("  - 用户看到的是原始格式文本")
print()

print("问题2: 可能的原因:")
print("  - 工具调用解析在响应生成之后")
print("  - LLM不知道要真正执行工具")
print("  - 系统提示词需要更明确的指令")
print()

print("解决方案:")
print("  1. 更新系统提示词，明确要求执行工具")
print("  2. 修改工具调用流程")
print("  3. 让用户使用命令直接调用MCP工具")
