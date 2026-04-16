#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/7
@Project: Gravix
@File: maxcompute_executor.py
@Author: Jerry
@Software: PyCharm
@Desc: MaxCompute tool executor for Gravix
"""

import json
from typing import Dict, Any, Optional
from app.tools.maxcompute_tools import get_maxcompute_client, MaxComputeClient
from app.utils.logger import logger


class MaxComputeToolExecutor:
    """
    Executor for MaxCompute/ODPS tools in Gravix

    Provides SQL execution and table management capabilities for MaxCompute/ODPS.
    """

    def __init__(self, client: MaxComputeClient = None):
        """
        Initialize executor with MaxCompute client

        Args:
            client: MaxComputeClient instance (uses singleton if not provided)
        """
        self.client = client or get_maxcompute_client()

    async def execute_list_tables(self, arguments: Dict[str, Any]) -> str:
        """
        List all tables in the MaxCompute project

        Args:
            arguments: Empty dict

        Returns:
            JSON string with table list
        """
        try:
            tables = self.client.list_tables()

            result = {
                "success": True,
                "count": len(tables),
                "tables": tables
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error in list_tables: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    async def execute_describe_table(self, arguments: Dict[str, Any]) -> str:
        """
        Get the schema information for a specific table

        Args:
            arguments: Dict with 'table_name' key

        Returns:
            Table schema description
        """
        try:
            table_name = arguments.get('table_name')
            if not table_name:
                raise ValueError("Missing required parameter: table_name")

            schema = self.client.describe_table(table_name)

            result = {
                "success": True,
                "table_name": table_name,
                "schema": schema
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error in describe_table: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    async def execute_get_latest_partition(self, arguments: Dict[str, Any]) -> str:
        """
        Get the latest partition name for a specific table

        Args:
            arguments: Dict with 'table_name' key

        Returns:
            Latest partition name or message if not partitioned
        """
        try:
            table_name = arguments.get('table_name')
            if not table_name:
                raise ValueError("Missing required parameter: table_name")

            partition = self.client.get_latest_partition(table_name)

            result = {
                "success": True,
                "table_name": table_name,
                "latest_partition": partition,
                "is_partitioned": partition is not None
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error in get_latest_partition: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)

    async def execute_read_query(self, arguments: Dict[str, Any]) -> str:
        """
        Execute a SELECT query on the MaxCompute project

        Args:
            arguments: Dict with 'query' key

        Returns:
            Query results as JSON
        """
        try:
            query = arguments.get('query')
            if not query:
                raise ValueError("Missing required parameter: query")

            results = self.client.execute_query(query)

            result = {
                "success": True,
                "query": query,
                "row_count": len(results),
                "rows": results
            }

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"Error in read_query: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False, indent=2)


# Singleton executor instance
_executor: Optional[MaxComputeToolExecutor] = None


def get_maxcompute_executor() -> MaxComputeToolExecutor:
    """
    Get or create the MaxCompute tool executor singleton

    Returns:
        MaxComputeToolExecutor instance
    """
    global _executor

    if _executor is None:
        _executor = MaxComputeToolExecutor()

    return _executor


async def execute_maxcompute_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    """
    Execute a MaxCompute tool

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        Tool execution result as JSON string
    """
    executor = get_maxcompute_executor()

    tool_map = {
        'maxcompute.list_tables': executor.execute_list_tables,
        'maxcompute.describe_table': executor.execute_describe_table,
        'maxcompute.get_latest_partition': executor.execute_get_latest_partition,
        'maxcompute.read_query': executor.execute_read_query,
    }

    executor_func = tool_map.get(tool_name)
    if not executor_func:
        return json.dumps({
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }, ensure_ascii=False, indent=2)

    return await executor_func(arguments)


def reset_maxcompute_executor():
    """Reset the MaxCompute executor singleton (useful for testing)"""
    global _executor
    _executor = None
