#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/7
@Project: Gravix
@File: demo_plan_confirmation.py
@Author: Jerry
@Software: PyCharm
@Desc: Demo: Plan-First Mode with User Confirmation
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def demo_plan_first_mode():
    """Demonstrate plan-first mode with user confirmation"""
    print("=" * 70)
    print("🎯 Plan-First Mode Demo: Human-in-the-Loop Execution")
    print("=" * 70)
    print()

    print("📌 核心理念：先规划，后执行，用户掌控全局")
    print()

    print("📝 Example 1: 简单问题（无需工具）")
    print("-" * 70)
    print("""
User: 你好
AI:   你好！我是 Gravix，有什么可以帮助你的吗？

[✅ 直接回答，无需确认]
    """.strip())

    print("\n")

    print("📝 Example 2: 需要工具调用的问题")
    print("-" * 70)
    print("""
User: gcc_002项目空间下有多少张表？

AI:   📋 **执行计划**

      我需要查询 DataWorks 系统来获取 gcc_002 项目中的表信息。

      **步骤：**

      1. 列出 gcc_002 项目中的所有表
         - 工具: ::dataworks.ListTables{"projectName":"gcc_002"}
         - 目的: 获取完整的表列表

      **预期结果：** 您将知道该项目中确切的表数量和名称。

      ---

      ⚠️ **需要您的确认：**

      回复 `yes` 或 `确认` 开始执行此计划
      回复 `no` 或 `取消` 取消执行

      💡 提示：你也可以修改问题后重新发送

User: yes

AI:   **步骤 1:** 执行 `dataworks.ListTables`
      ```
      {
        "Tables": [
          "users",
          "orders",
          "products",
          ... (共23张表)
        ]
      }
      ```

      ---

      **最终答案：**

      gcc_002 项目空间下共有 **23 张表**，包括：
      - users（用户表）
      - orders（订单表）
      - products（产品表）
      ... 等 23 张表。
    """.strip())

    print("\n")

    print("📝 Example 3: 多步骤任务")
    print("-" * 70)
    print("""
User: 告诉我关于 gcc_002 项目的信息及其表结构

AI:   📋 **执行计划**

      我需要先确认项目存在，然后获取项目信息和表列表。

      **步骤：**

      1. 列出所有项目以确认 gcc_002 存在
         - 工具: ::dataworks.ListProjects{}
         - 目的: 确认项目存在并获取基本信息

      2. 获取 gcc_002 项目的表列表
         - 工具: ::dataworks.ListTables{"projectName":"gcc_002"}
         - 目的: 获取所有表的详细信息

      **预期结果：** 您将获得项目的完整信息和表结构概览。

      ---

      ⚠️ **需要您的确认：**

      回复 `yes` 或 `确认` 开始执行此计划
      回复 `no` 或 `取消` 取消执行

User: yes

AI:   **步骤 1:** 执行 `dataworks.ListProjects`
      ```
      {
        "Projects": [
          {
            "Name": "gcc_002",
            "Status": "Available",
            ...
          }
        ]
      }
      ```

      **步骤 2:** 执行 `dataworks.ListTables`
      ```
      {
        "Tables": [
          "users", "orders", "products", ...
        ]
      }
      ```

      ---

      **最终答案：**

      **gcc_002 项目信息：**

      📊 项目状态: 运行正常 (Available)

      📋 表结构 (共 23 张表)：

      **用户数据表：**
      - users - 用户基本信息
      - user_profiles - 用户详细资料
      - user_activity - 用户活动记录

      **订单表：**
      - orders - 订单主表
      - order_items - 订单明细
      - order_status - 订单状态

      **产品表：**
      - products - 产品信息
      - categories - 产品分类
      - inventory - 库存信息

      ... 共 23 张表。
    """.strip())

    print("\n")

    print("=" * 70)
    print("✨ 核心优势")
    print("=" * 70)
    print("""
1. 🔒 **安全性** - 用户看到每一步操作，避免意外执行
2. 🎯 **透明性** - 完全了解系统将要做什么
3. 🎮 **控制权** - 用户决定是否执行，随时可以取消
4. 🧠 **智能化** - LLM 自动规划最优执行路径
5. 📊 **可视化** - 清晰展示执行计划和结果

    """.strip())

    print("\n")

    print("=" * 70)
    print("🎮 交互命令")
    print("=" * 70)
    print("""
确认执行：
  - yes / y / 确认 / 执行

取消执行：
  - no / n / 取消 / 否

切换模式：
  - /plan_mode - 启用计划确认模式（默认）
  - /auto_mode - 启用自动执行模式（无需确认）
  - /confirm_mode - 查看当前模式状态

💡 提示：在自动模式下，工具会直接执行，不会请求确认
    """.strip())

    print("\n")


def demo_comparison():
    """Compare old vs new approach"""
    print("\n\n")
    print("=" * 70)
    print("📊 方案对比")
    print("=" * 70)
    print()

    print("❌ 方案1: 固定迭代次数限制")
    print("-" * 70)
    print("""
问题：
  - 用户不知道系统会执行多少步骤
  - 无法控制执行过程
  - 可能浪费资源在不必要的步骤上
  - 用户体验差，不知道系统在做什么
    """.strip())

    print("\n")

    print("✅ 方案2: 计划确认模式（当前实现）")
    print("-" * 70)
    print("""
优势：
  - 用户在执行前看到完整计划
  - 可以拒绝或修改计划
  - 清晰的执行步骤展示
  - 完全的用户控制权
  - 符合"人在回路"设计理念

流程：
  1. 用户提问
  2. LLM 生成执行计划
  3. 展示计划给用户
  4. 用户确认
  5. 执行计划
  6. 返回结果
    """.strip())

    print("\n")
    print("=" * 70)


if __name__ == "__main__":
    print()
    demo_plan_first_mode()
    demo_comparison()
    print()
