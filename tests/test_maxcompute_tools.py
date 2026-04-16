#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/7
@Project: Gravix
@File: test_maxcompute_tools.py
@Author: Jerry
@Software: PyCharm
@Desc: Test MaxCompute tools integration
"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app.tools.maxcompute_tools import get_maxcompute_client
from app.tools.maxcompute_executor import execute_maxcompute_tool
from app.utils.logger import logger


async def test_maxcompute_tools():
    """Test MaxCompute tools with real connection"""

    print("=" * 70)
    print("🧪 MaxCompute Tools Test")
    print("=" * 70)
    print()

    # Check environment variables
    print("🔍 Checking environment variables...")
    required_vars = [
        'ALIBABA_CLOUD_ACCESS_KEY_ID',
        'ALIBABA_CLOUD_ACCESS_KEY_SECRET',
        'ALIBABA_CLOUD_MAXCOMPUTE_PROJECT',
        'ALIBABA_CLOUD_MAXCOMPUTE_ENDPOINT'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please set these environment variables before running the test:")
        print("export ALIBABA_CLOUD_ACCESS_KEY_ID=your_key")
        print("export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret")
        print("export ALIBABA_CLOUD_MAXCOMPUTE_PROJECT=your_project")
        print("export ALIBABA_CLOUD_MAXCOMPUTE_ENDPOINT=your_endpoint")
        return

    print("✅ All required environment variables are set")
    print()

    # Test 1: Initialize client
    print("📝 Test 1: Initialize MaxCompute Client")
    print("-" * 70)
    try:
        client = get_maxcompute_client()
        print(f"✅ Client initialized successfully")
        print(f"   Project: {client.project}")
        print()
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return

    # Test 2: List tables
    print("📝 Test 2: List Tables")
    print("-" * 70)
    try:
        result = await execute_maxcompute_tool('maxcompute.list_tables', {})
        print(f"✅ Tool executed successfully")
        print(f"   Result preview: {result[:200]}...")
        print()
    except Exception as e:
        print(f"❌ Failed to list tables: {e}")
        print()

    # Test 3: Describe a table (if tables exist)
    print("📝 Test 3: Describe First Table")
    print("-" * 70)
    try:
        # First get a table name
        list_result = await execute_maxcompute_tool('maxcompute.list_tables', {})
        import json
        tables_data = json.loads(list_result)

        if tables_data.get('success') and tables_data.get('tables'):
            first_table = tables_data['tables'][0]['name']
            print(f"   Describing table: {first_table}")

            result = await execute_maxcompute_tool(
                'maxcompute.describe_table',
                {'table_name': first_table}
            )
            print(f"✅ Tool executed successfully")
            print(f"   Result preview: {result[:300]}...")
        else:
            print("⚠️  No tables found to describe")
        print()
    except Exception as e:
        print(f"❌ Failed to describe table: {e}")
        print()

    # Test 4: Execute SELECT query
    print("📝 Test 4: Execute SELECT Query")
    print("-" * 70)
    try:
        # Simple query to show tables
        result = await execute_maxcompute_tool(
            'maxcompute.read_query',
            {'query': 'SELECT table_name FROM information_schema.tables LIMIT 5'}
        )
        print(f"✅ Tool executed successfully")
        print(f"   Result preview: {result[:300]}...")
        print()
    except Exception as e:
        print(f"❌ Failed to execute query: {e}")
        print()

    print("=" * 70)
    print("✅ MaxCompute Tools Test Completed")
    print("=" * 70)


if __name__ == "__main__":
    print()
    asyncio.run(test_maxcompute_tools())
    print()
