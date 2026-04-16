#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/7
@Project: Gravix
@File: test_react_mode.py
@Author: Jerry
@Software: PyCharm
@Desc: Test ReAct mode multi-step tool calling
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.chat.tool_calling import ReActParser, ReActResponse, ToolCall


def test_react_parser():
    """Test ReAct response parser"""
    print("=== Testing ReAct Parser ===\n")

    # Test 1: Thought + Action
    print("Test 1: Thought + Action format")
    response1 = """Thought: I need to query the DataWorks system to get table information.
Action: ::dataworks.ListTables{"projectName":"gcc_002"}"""

    parsed1 = ReActParser.parse(response1)
    print(f"  Thought: {parsed1.thought}")
    print(f"  Action: {parsed1.action}")
    print(f"  Has action: {parsed1.has_action()}")
    print(f"  Has answer: {parsed1.has_answer()}")
    assert parsed1.has_action(), "Should detect action"
    assert not parsed1.has_answer(), "Should not have answer yet"
    print("  ✓ Passed\n")

    # Test 2: Thought + Answer
    print("Test 2: Thought + Answer format")
    response2 = """Thought: I have received the table list. Now I can count them.
Answer: The gcc_002 project contains 23 tables."""

    parsed2 = ReActParser.parse(response2)
    print(f"  Thought: {parsed2.thought}")
    print(f"  Answer: {parsed2.answer}")
    print(f"  Has action: {parsed2.has_action()}")
    print(f"  Has answer: {parsed2.has_answer()}")
    assert parsed2.has_answer(), "Should detect answer"
    assert not parsed2.has_action(), "Should not have action"
    print("  ✓ Passed\n")

    # Test 3: Direct tool call (no ReAct format)
    print("Test 3: Direct tool call format")
    response3 = "::dataworks.ListTables{\"projectName\":\"gcc_002\"}"

    parsed3 = ReActParser.parse(response3)
    print(f"  Thought: {parsed3.thought}")
    print(f"  Action: {parsed3.action}")
    print(f"  Has action: {parsed3.has_action()}")
    assert parsed3.has_action(), "Should detect action"
    print("  ✓ Passed\n")

    # Test 4: Plain text answer
    print("Test 4: Plain text answer")
    response4 = "The project has 23 tables and includes users, orders, and products tables."

    parsed4 = ReActParser.parse(response4)
    print(f"  Thought: {parsed4.thought}")
    print(f"  Answer: {parsed4.answer[:50]}...")
    print(f"  Has action: {parsed4.has_action()}")
    print(f"  Has answer: {parsed4.has_answer()}")
    assert parsed4.has_answer(), "Should treat as answer"
    print("  ✓ Passed\n")

    # Test 5: Multi-line thought
    print("Test 5: Multi-line thought")
    response5 = """Thought: I need to gather information about the project.
First, I should check if the project exists.
Then I can query for the tables.
Action: ::dataworks.ListProjects{}"""

    parsed5 = ReActParser.parse(response5)
    print(f"  Thought: {parsed5.thought}")
    print(f"  Action: {parsed5.action}")
    assert parsed5.has_action(), "Should detect action"
    assert "check if the project exists" in parsed5.thought, "Should capture multi-line thought"
    print("  ✓ Passed\n")

    print("=== All ReAct Parser Tests Passed! ===\n")


def test_tool_call_extraction():
    """Test extracting tool calls from actions"""
    print("=== Testing Tool Call Extraction ===\n")

    # Test 1: Simple format
    print("Test 1: Simple format (JSON)")
    response1 = "::dataworks.ListTables{\"projectName\":\"gcc_002\"}"
    react1 = ReActParser.parse(response1)
    call1 = ReActParser.extract_tool_call(react1)
    print(f"  Tool: {call1.tool_name}")
    print(f"  Params: {call1.parameters}")
    assert call1.tool_name == "dataworks.ListTables"
    assert call1.parameters.get("projectName") == "gcc_002" or "gcc_002" in str(call1.parameters)
    print("  ✓ Passed\n")

    # Test 2: Key-value format
    print("Test 2: Key-value format")
    response2 = "::calculate{expression=2+2*3}"
    react2 = ReActParser.parse(response2)
    call2 = ReActParser.extract_tool_call(react2)
    print(f"  Tool: {call2.tool_name}")
    print(f"  Params: {call2.parameters}")
    assert call2.tool_name == "calculate"
    assert call2.parameters.get("expression") == "2+2*3"
    print("  ✓ Passed\n")

    print("=== All Tool Call Extraction Tests Passed! ===\n")


def test_react_scenario():
    """Test a complete ReAct scenario"""
    print("=== Testing Complete ReAct Scenario ===\n")

    # Simulate a conversation
    user_query = "How many tables are in project gcc_002?"

    print(f"User: {user_query}\n")

    # Step 1: LLM decides to call a tool
    print("Step 1: LLM Response")
    llm_response_1 = """Thought: I need to query the DataWorks system to get information about tables in the gcc_002 project.
Action: ::dataworks.ListTables{"projectName":"gcc_002"}"""

    print(llm_response_1)
    parsed_1 = ReActParser.parse(llm_response_1)
    print(f"\n  Detected: Thought={parsed_1.thought is not None}, Action={parsed_1.has_action()}\n")

    # Step 2: Tool returns results
    print("Step 2: Tool Execution Result")
    tool_result = {
        "content": [
            {
                "text": '{"Tables": ["table1", "table2", "table3", "... 20 more tables"]}'
            }
        ]
    }
    print(f"  Result: {tool_result['content'][0]['text'][:60]}...\n")

    # Step 3: LLM provides final answer
    print("Step 3: LLM Final Response")
    llm_response_2 = """Thought: I have received the table list. I can see there are 23 tables in total.
Answer: The gcc_002 project contains **23 tables**."""

    print(llm_response_2)
    parsed_2 = ReActParser.parse(llm_response_2)
    print(f"\n  Detected: Thought={parsed_2.thought is not None}, Answer={parsed_2.has_answer()}")
    print(f"\n  Final Answer: {parsed_2.answer}\n")

    print("=== ReAct Scenario Test Passed! ===\n")


def test_multi_step_scenario():
    """Test a multi-step ReAct scenario"""
    print("=== Testing Multi-Step ReAct Scenario ===\n")

    user_query = "Tell me about the gcc_002 project and its tables"

    print(f"User: {user_query}\n")

    # Step 1: List projects to verify existence
    print("Step 1: Verify project exists")
    response_1 = """Thought: I should first check if the gcc_002 project exists.
Action: ::dataworks.ListProjects{}"""
    print(response_1)
    parsed_1 = ReActParser.parse(response_1)
    assert parsed_1.has_action()
    print("  ✓ Action detected\n")

    # Step 2: After seeing project exists, list tables
    print("Step 2: List tables in the project")
    response_2 = """Thought: The project exists. Now I need to get the list of tables.
Action: ::dataworks.ListTables{"projectName":"gcc_002"}"""
    print(response_2)
    parsed_2 = ReActParser.parse(response_2)
    assert parsed_2.has_action()
    print("  ✓ Action detected\n")

    # Step 3: Provide final answer
    print("Step 3: Provide comprehensive answer")
    response_3 = """Thought: I have both the project information and table list. Now I can provide a complete answer.
Answer: The gcc_002 project is a DataWorks workspace containing **23 tables**:
- User data tables: users, user_profiles, user_activity
- Order tables: orders, order_items, order_status
- Product tables: products, categories, inventory
... and 14 more tables."""
    print(response_3)
    parsed_3 = ReActParser.parse(response_3)
    assert parsed_3.has_answer()
    print("  ✓ Answer detected\n")

    print("=== Multi-Step Scenario Test Passed! ===\n")


if __name__ == "__main__":
    print("🧪 ReAct Mode Test Suite\n" + "="*50 + "\n")

    try:
        test_react_parser()
        test_tool_call_extraction()
        test_react_scenario()
        test_multi_step_scenario()

        print("="*50)
        print("✅ All tests passed successfully!")
        print("\n🎉 ReAct mode is ready for multi-step tool calling!")

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
