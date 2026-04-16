#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/7
@Project: Gravix
@File: maxcompute_tools.py
@Author: Jerry
@Software: PyCharm
@Desc: MaxCompute/ODPS tools for SQL execution and table operations
"""

import os
from typing import List, Dict, Any, Optional
from odps import ODPS
from app.utils.logger import logger


class MaxComputeClient:
    """
    MaxCompute/ODPS client for executing SQL queries and managing tables

    This is a native Gravix integration that doesn't require the MCP SDK,
    making it compatible with Python 3.9+.
    """

    def __init__(
        self,
        access_key_id: str = None,
        access_key_secret: str = None,
        project: str = None,
        endpoint: str = None
    ):
        """
        Initialize MaxCompute client

        Args:
            access_key_id: Alibaba Cloud Access Key ID
            access_key_secret: Alibaba Cloud Access Key Secret
            project: MaxCompute project name
            endpoint: MaxCompute endpoint URL
        """
        # Use environment variables if not provided
        self.access_key_id = access_key_id or os.getenv('ALIBABA_CLOUD_ACCESS_KEY_ID')
        self.access_key_secret = access_key_secret or os.getenv('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        self.project = project or os.getenv('ALIBABA_CLOUD_MAXCOMPUTE_PROJECT')
        self.endpoint = endpoint or os.getenv('ALIBABA_CLOUD_MAXCOMPUTE_ENDPOINT')

        if not all([self.access_key_id, self.access_key_secret, self.project, self.endpoint]):
            raise ValueError(
                "Missing required ODPS configuration. Please provide:\n"
                "- ALIBABA_CLOUD_ACCESS_KEY_ID\n"
                "- ALIBABA_CLOUD_ACCESS_KEY_SECRET\n"
                "- ALIBABA_CLOUD_MAXCOMPUTE_PROJECT\n"
                "- ALIBABA_CLOUD_MAXCOMPUTE_ENDPOINT\n"
                "Either as parameters or environment variables."
            )

        self.odps = ODPS(
            self.access_key_id,
            self.access_key_secret,
            self.project,
            self.endpoint
        )

        logger.info(f"MaxCompute client initialized for project: {self.project}")

    def list_tables(self) -> List[Dict[str, str]]:
        """
        List all tables in the MaxCompute project

        Returns:
            List of table objects with name and comment
        """
        try:
            logger.info(f"Listing tables in project: {self.project}")
            tables = []

            for table in self.odps.list_tables():
                tables.append({
                    'name': table.name,
                    'comment': getattr(table, 'comment', '')
                })

            logger.info(f"Found {len(tables)} tables")
            return tables

        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise

    def describe_table(self, table_name: str) -> str:
        """
        Get the schema information for a specific table

        Args:
            table_name: Name of the table

        Returns:
            Raw output of DESC command
        """
        try:
            logger.info(f"Describing table: {table_name}")

            # Get table object
            table = self.odps.get_table(table_name)

            # Build schema description
            schema_desc = f"Table: {table_name}\n"
            schema_desc += f"Comment: {getattr(table, 'comment', 'N/A')}\n"
            schema_desc += f"Columns:\n"

            for column in table.table_schema.columns:
                schema_desc += f"  - {column.name}: {column.type}"
                if column.comment:
                    schema_desc += f" ({column.comment})"
                schema_desc += "\n"

            # Add partition info if exists
            if table.table_schema.partitions:
                schema_desc += f"Partitions:\n"
                for partition in table.table_schema.partitions:
                    schema_desc += f"  - {partition.name}: {partition.type}\n"

            logger.info(f"Table description generated for: {table_name}")
            return schema_desc

        except Exception as e:
            logger.error(f"Error describing table {table_name}: {e}")
            raise

    def get_latest_partition(self, table_name: str) -> Optional[str]:
        """
        Get the latest partition name for a specific table

        Args:
            table_name: Name of the table

        Returns:
            The latest partition name or None if not partitioned
        """
        try:
            logger.info(f"Getting latest partition for table: {table_name}")

            table = self.odps.get_table(table_name)

            if not table.table_schema.partitions:
                logger.info(f"Table {table_name} is not partitioned")
                return None

            # Get partitions
            partitions = list(table.partitions)
            if not partitions:
                logger.info(f"No partitions found for table {table_name}")
                return None

            # Sort by creation time (if available) or get last
            latest_partition = partitions[-1].spec
            logger.info(f"Latest partition for {table_name}: {latest_partition}")
            return latest_partition

        except Exception as e:
            logger.error(f"Error getting latest partition for {table_name}: {e}")
            raise

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a SQL query on the MaxCompute project

        Args:
            query: The SQL query (only SELECT queries allowed)

        Returns:
            Query results as array of objects
        """
        try:
            query_upper = query.strip().upper()

            # Security check: only allow SELECT queries
            if not query_upper.startswith('SELECT') and not query_upper.startswith('DESC') and not query_upper.startswith('SHOW'):
                raise ValueError(
                    "Only SELECT, DESC, and SHOW queries are allowed for security reasons. "
                    "Query must start with SELECT, DESC, or SHOW."
                )

            logger.info(f"Executing query: {query[:100]}...")

            with self.odps.execute_sql(query).open_reader() as reader:
                if query_upper.startswith('DESC'):
                    # For DESC queries, return raw output
                    return [{'raw': reader.raw}]

                # For SELECT queries, return as list of dictionaries
                results = [dict(row) for row in reader]
                logger.info(f"Query returned {len(results)} rows")
                return results

        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise


# Singleton instance
_maxcompute_client: Optional[MaxComputeClient] = None


def get_maxcompute_client() -> MaxComputeClient:
    """
    Get or create the MaxCompute client singleton

    Returns:
        MaxComputeClient instance
    """
    global _maxcompute_client

    if _maxcompute_client is None:
        _maxcompute_client = MaxComputeClient()

    return _maxcompute_client


def reset_maxcompute_client():
    """Reset the MaxCompute client singleton (useful for testing)"""
    global _maxcompute_client
    _maxcompute_client = None
