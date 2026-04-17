#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/17
@Project: Gravix
@File: base.py
@Author: Claude
@Software: PyCharm
@Desc: Database adapter base interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseAdapter(ABC):
    """
    Database adapter interface

    All database adapters must implement this interface
    """

    @abstractmethod
    def connect(self):
        """Establish database connection"""
        pass

    @abstractmethod
    def disconnect(self):
        """Close database connection"""
        pass

    @abstractmethod
    def initialize_schema(self):
        """Create database tables and indexes"""
        pass

    # ==================== Session Operations ====================

    @abstractmethod
    def create_session(self, session_id: str, title: str, metadata: Dict[str, Any] = None) -> bool:
        """Create a new session"""
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        pass

    @abstractmethod
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        pass

    @abstractmethod
    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session fields"""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        pass

    @abstractmethod
    def update_last_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp"""
        pass

    # ==================== Message Operations ====================

    @abstractmethod
    def add_message(self, session_id: str, role: str, content: str,
                    metadata: Dict[str, Any] = None, timestamp: datetime = None) -> bool:
        """Add a message to a session"""
        pass

    @abstractmethod
    def get_messages(self, session_id: str, limit: Optional[int] = None,
                     roles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get messages from a session"""
        pass

    @abstractmethod
    def delete_messages(self, session_id: str) -> bool:
        """Delete all messages from a session"""
        pass

    def count_messages(self, session_id: str) -> int:
        """Count messages in a session"""
        messages = self.get_messages(session_id)
        return len(messages)

    # ==================== Search Operations ====================

    @abstractmethod
    def search_sessions(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for sessions containing keyword"""
        pass

    @abstractmethod
    def get_recent_sessions(self, limit: int = 5, exclude_session_id: str = None) -> List[Dict[str, Any]]:
        """Get recent sessions"""
        pass

    # ==================== Utility Methods ====================

    @abstractmethod
    def begin_transaction(self):
        """Begin a transaction"""
        pass

    @abstractmethod
    def commit(self):
        """Commit transaction"""
        pass

    @abstractmethod
    def rollback(self):
        """Rollback transaction"""
        pass

    @abstractmethod
    def execute_raw(self, sql: str, params: tuple = None) -> Any:
        """Execute raw SQL query"""
        pass
