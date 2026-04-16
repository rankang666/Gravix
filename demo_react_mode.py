#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/7
@Project: Gravix
@File: demo_react_mode.py
@Author: Jerry
@Software: PyCharm
@Desc: Demo: ReAct mode for multi-step tool calling
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def demo_react_parser():
    """Demonstrate ReAct response parsing"""
    print("=" * 60)
    print("🎭 ReAct Mode Demo: Multi-Step Tool Calling")
    print("=" * 60)
    print()

    from app.chat.tool_calling import ReActParser

    # Example 1: Simple tool call
    print("📝 Example 1: Direct Tool Call")
    print("-" * 40)
    response1 = "::dataworks.ListTables{\"projectName\":\"gcc_002\"}"
    print(f"Input:  {response1}")

    parsed1 = ReActParser.parse(response1)
    print(f"Parsed:")
    print(f"  - Thought: {parsed1.thought}")
    print(f"  - Action:  {parsed1.action}")
    print(f"  - Has Action: {parsed1.has_action()}")
    print()

    # Example 2: Thought + Action
    print("📝 Example 2: Thought + Action (ReAct Format)")
    print("-" * 40)
    response2 = """Thought: I need to query the DataWorks system to get table information.
Action: ::dataworks.ListTables{"projectName":"gcc_002"}"""

    print(f"Input:\n{response2}\n")

    parsed2 = ReActParser.parse(response2)
    print(f"Parsed:")
    print(f"  - Thought: {parsed2.thought}")
    print(f"  - Action:  {parsed2.action}")
    print(f"  - Has Action: {parsed2.has_action()}")
    print()

    # Example 3: Thought + Answer
    print("📝 Example 3: Thought + Answer (Complete)")
    print("-" * 40)
    response3 = """Thought: I have received the table list. Now I can count them.
Answer: The gcc_002 project contains 23 tables."""

    print(f"Input:\n{response3}\n")

    parsed3 = ReActParser.parse(response3)
    print(f"Parsed:")
    print(f"  - Thought: {parsed3.thought}")
    print(f"  - Answer:  {parsed3.answer}")
    print(f"  - Has Answer: {parsed3.has_answer()}")
    print()

    # Example 4: Complete multi-step scenario
    print("📝 Example 4: Complete Multi-Step Scenario")
    print("-" * 40)

    user_query = "How many tables are in project gcc_002?"
    print(f"User Query: {user_query}\n")

    steps = [
        {
            "round": 1,
            "response": """Thought: I need to query the DataWorks system to get table information.
Action: ::dataworks.ListTables{"projectName":"gcc_002"}""",
            "observation": '{"Tables": ["table1", "table2", "table3", "... 20 more tables"]}'
        },
        {
            "round": 2,
            "response": """Thought: I have received the table list. I can see there are 23 tables in total.
Answer: The gcc_002 project contains **23 tables** including table1, table2, table3, and 20 others.""",
            "observation": None
        }
    ]

    for step in steps:
        print(f"🔄 Round {step['round']}:")
        parsed = ReActParser.parse(step['response'])

        if parsed.thought:
            print(f"  💭 Thought: {parsed.thought}")

        if parsed.has_action():
            print(f"  🔧 Action:  {parsed.action}")
            print(f"  👁️ Observation: {step['observation'][:60]}...")

        if parsed.has_answer():
            print(f"  ✅ Answer:   {parsed.answer[:80]}...")

        print()

    print("=" * 60)
    print("✅ ReAct mode successfully parses multi-step reasoning!")
    print("=" * 60)


def demo_comparison():
    """Compare old vs new approach"""
    print("\n\n")
    print("=" * 60)
    print("📊 Comparison: Old vs New Approach")
    print("=" * 60)
    print()

    print("❌ Old Approach (Single-Step):")
    print("-" * 40)
    print("""
User: "How many tables in project gcc_002?"

LLM: ::dataworks.ListTables{"projectName":"gcc_002"}

System: Execute tool → Get results

LLM: [Forced to give answer immediately]

Problem: LLM cannot decide to call more tools!
    """.strip())

    print()
    print("✅ New Approach (ReAct Loop):")
    print("-" * 40)
    print("""
User: "How many tables in project gcc_002?"

Round 1:
  LLM: Thought + Action → Call ListTables
  System: Execute tool → Return results

Round 2:
  LLM: [Sees results] → Thought + Answer
  System: Return final answer

Benefit: LLM can decide to call more tools if needed!
    """.strip())

    print()
    print("=" * 60)


if __name__ == "__main__":
    print()
    demo_react_parser()
    demo_comparison()
    print()
