#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/17
@Project: Gravix
@File: factory.py
@Author: Claude
@Software: PyCharm
@Desc: Database adapter factory
"""

from typing import Dict, Any
from app.database.base import DatabaseAdapter
from app.database.sqlite_adapter import SQLiteAdapter
from app.utils.logger import logger


class DatabaseAdapterFactory:
    """
    Factory for creating database adapters

    Supports:
    - sqlite
    - mysql (placeholder for future implementation)
    """

    @staticmethod
    def create_adapter(config: Dict[str, Any]) -> DatabaseAdapter:
        """
        Create database adapter based on configuration

        Args:
            config: Database configuration dict with keys:
                - type: Database type ('sqlite', 'mysql')
                - Additional type-specific config

        Returns:
            DatabaseAdapter instance

        Raises:
            ValueError: If database type is not supported
        """
        db_type = config.get('type', 'sqlite').lower()

        if db_type == 'sqlite':
            return DatabaseAdapterFactory._create_sqlite_adapter(config)
        elif db_type == 'mysql':
            return DatabaseAdapterFactory._create_mysql_adapter(config)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

    @staticmethod
    def _create_sqlite_adapter(config: Dict[str, Any]) -> SQLiteAdapter:
        """Create SQLite adapter"""
        db_path = config.get('path', 'data/gravix.db')
        logger.info(f"Creating SQLite adapter with path: {db_path}")
        return SQLiteAdapter(db_path=db_path)

    @staticmethod
    def _create_mysql_adapter(config: Dict[str, Any]) -> DatabaseAdapter:
        """Create MySQL adapter (placeholder)"""
        # TODO: Implement MySQL adapter
        logger.warning("MySQL adapter not yet implemented, using SQLite")
        raise NotImplementedError(
            "MySQL adapter is not yet implemented. "
            "Use SQLite or implement MySQLAdapter class."
        )

    @staticmethod
    def create_from_env() -> DatabaseAdapter:
        """
        Create database adapter from environment variables

        Environment variables:
        - DATABASE_TYPE: sqlite/mysql (default: sqlite)
        - SQLITE_PATH: Path to SQLite file (default: data/gravix.db)
        - MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

        Returns:
            DatabaseAdapter instance
        """
        import os

        db_type = os.getenv('DATABASE_TYPE', 'sqlite').lower()

        config = {'type': db_type}

        if db_type == 'sqlite':
            config['path'] = os.getenv('SQLITE_PATH', 'data/gravix.db')
        elif db_type == 'mysql':
            config.update({
                'host': os.getenv('MYSQL_HOST', 'localhost'),
                'port': int(os.getenv('MYSQL_PORT', '3306')),
                'user': os.getenv('MYSQL_USER', 'root'),
                'password': os.getenv('MYSQL_PASSWORD', ''),
                'database': os.getenv('MYSQL_DATABASE', 'gravix')
            })

        return DatabaseAdapterFactory.create_adapter(config)
