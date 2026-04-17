#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/17
@Project: Gravix
@File: sqlite_adapter.py
@Author: Claude
@Software: PyCharm
@Desc: SQLite database adapter implementation
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.database.base import DatabaseAdapter
from app.database.schema import FULL_SCHEMA
from app.utils.logger import logger


class SQLiteAdapter(DatabaseAdapter):
    """
    SQLite database adapter

    Implements DatabaseAdapter interface for SQLite database
    """

    def __init__(self, db_path: str = 'data/gravix.db'):
        """
        Initialize SQLite adapter

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None

        # Ensure directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def connect(self):
        """Establish database connection"""
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None  # Autocommit mode
            )
            self.connection.row_factory = sqlite3.Row  # Return dict-like rows
            logger.info(f"✅ SQLite database connected: {self.db_path}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to SQLite database: {e}")
            raise

    def disconnect(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("✅ SQLite database disconnected")

    def initialize_schema(self):
        """Create database tables and indexes"""
        try:
            cursor = self.connection.cursor()
            cursor.executescript(FULL_SCHEMA)
            self.connection.commit()
            logger.info("✅ Database schema initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize schema: {e}")
            raise

    # ==================== Session Operations ====================

    def create_session(self, session_id: str, title: str, metadata: Dict[str, Any] = None) -> bool:
        """Create a new session"""
        try:
            cursor = self.connection.cursor()
            metadata_json = json.dumps(metadata) if metadata else None

            cursor.execute("""
                INSERT INTO sessions (session_id, title, metadata, created_at, last_activity)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                title,
                metadata_json,
                datetime.utcnow().isoformat(),
                datetime.utcnow().isoformat()
            ))

            self.connection.commit()
            logger.debug(f"Created session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT session_id, title, metadata, created_at, last_activity
                FROM sessions
                WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if row:
                return {
                    'session_id': row['session_id'],
                    'title': row['title'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': datetime.fromisoformat(row['created_at']),
                    'last_activity': datetime.fromisoformat(row['last_activity'])
                }
            return None
        except Exception as e:
            logger.error(f"Failed to get session: {e}")
            return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT session_id, title, metadata, created_at, last_activity
                FROM sessions
                ORDER BY last_activity DESC
            """)

            sessions = []
            for row in cursor.fetchall():
                # Get message count and preview
                messages = self.get_messages(row['session_id'], limit=1)
                preview = "新会话"
                if messages:
                    user_msgs = [m for m in messages if m['role'] == 'user']
                    if user_msgs:
                        content = user_msgs[-1]['content']
                        preview = content[:50] + '...' if len(content) > 50 else content

                sessions.append({
                    'session_id': row['session_id'],
                    'title': row['title'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': datetime.fromisoformat(row['created_at']),
                    'last_activity': datetime.fromisoformat(row['last_activity']),
                    'message_count': self.count_messages(row['session_id']),
                    'preview': preview
                })

            return sessions
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return []

    def update_session(self, session_id: str, **kwargs) -> bool:
        """Update session fields"""
        try:
            if not kwargs:
                return False

            # Build UPDATE query dynamically
            set_clauses = []
            values = []

            for key, value in kwargs.items():
                if key == 'metadata':
                    value = json.dumps(value) if value else None
                elif key in ['created_at', 'last_activity']:
                    if isinstance(value, datetime):
                        value = value.isoformat()

                set_clauses.append(f"{key} = ?")
                values.append(value)

            if not set_clauses:
                return False

            values.append(session_id)

            cursor = self.connection.cursor()
            cursor.execute(f"""
                UPDATE sessions
                SET {', '.join(set_clauses)}
                WHERE session_id = ?
            """, values)

            self.connection.commit()
            logger.debug(f"Updated session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update session: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session (cascade deletes messages)"""
        try:
            cursor = self.connection.cursor()

            # Delete messages first (foreign key will handle this automatically)
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

            # Delete session
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

            self.connection.commit()
            logger.info(f"Deleted session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete session: {e}")
            return False

    def update_last_activity(self, session_id: str) -> bool:
        """Update session last activity timestamp"""
        return self.update_session(session_id, last_activity=datetime.utcnow())

    # ==================== Message Operations ====================

    def add_message(self, session_id: str, role: str, content: str,
                    metadata: Dict[str, Any] = None, timestamp: datetime = None) -> bool:
        """Add a message to a session"""
        try:
            cursor = self.connection.cursor()
            metadata_json = json.dumps(metadata) if metadata else None
            timestamp_iso = (timestamp or datetime.utcnow()).isoformat()

            cursor.execute("""
                INSERT INTO messages (session_id, role, content, metadata, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, role, content, metadata_json, timestamp_iso))

            self.connection.commit()

            # Update session last activity
            self.update_last_activity(session_id)

            logger.debug(f"Added message to session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add message: {e}")
            return False

    def get_messages(self, session_id: str, limit: Optional[int] = None,
                     roles: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get messages from a session"""
        try:
            cursor = self.connection.cursor()

            query = """
                SELECT id, session_id, role, content, metadata, timestamp
                FROM messages
                WHERE session_id = ?
            """
            params = [session_id]

            if roles:
                placeholders = ','.join(['?' for _ in roles])
                query += f" AND role IN ({placeholders})"
                params.extend(roles)

            query += " ORDER BY timestamp ASC"

            if limit:
                query += f" LIMIT {limit}"

            cursor.execute(query, params)

            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row['id'],
                    'session_id': row['session_id'],
                    'role': row['role'],
                    'content': row['content'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'timestamp': datetime.fromisoformat(row['timestamp'])
                })

            return messages
        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    def delete_messages(self, session_id: str) -> bool:
        """Delete all messages from a session"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            self.connection.commit()
            logger.info(f"Deleted messages from session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete messages: {e}")
            return False

    # ==================== Search Operations ====================

    def search_sessions(self, keyword: str) -> List[Dict[str, Any]]:
        """Search for sessions containing keyword"""
        try:
            cursor = self.connection.cursor()
            keyword_pattern = f"%{keyword}%"

            cursor.execute("""
                SELECT DISTINCT s.session_id, s.title, s.metadata, s.created_at, s.last_activity
                FROM sessions s
                LEFT JOIN messages m ON s.session_id = m.session_id
                WHERE s.title LIKE ?
                   OR m.content LIKE ?
                ORDER BY s.last_activity DESC
            """, (keyword_pattern, keyword_pattern))

            sessions = []
            for row in cursor.fetchall():
                # Get message count and preview
                messages = self.get_messages(row['session_id'], limit=1)
                preview = "新会话"
                if messages:
                    user_msgs = [m for m in messages if m['role'] == 'user']
                    if user_msgs:
                        content = user_msgs[-1]['content']
                        preview = content[:50] + '...' if len(content) > 50 else content

                sessions.append({
                    'session_id': row['session_id'],
                    'title': row['title'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': datetime.fromisoformat(row['created_at']),
                    'last_activity': datetime.fromisoformat(row['last_activity']),
                    'message_count': self.count_messages(row['session_id']),
                    'preview': preview
                })

            return sessions
        except Exception as e:
            logger.error(f"Failed to search sessions: {e}")
            return []

    def get_recent_sessions(self, limit: int = 5, exclude_session_id: str = None) -> List[Dict[str, Any]]:
        """Get recent sessions"""
        try:
            cursor = self.connection.cursor()

            query = """
                SELECT session_id, title, metadata, created_at, last_activity
                FROM sessions
            """
            params = []

            if exclude_session_id:
                query += " WHERE session_id != ?"
                params.append(exclude_session_id)

            query += " ORDER BY last_activity DESC LIMIT ?"
            params.append(limit)

            cursor.execute(query, params)

            sessions = []
            for row in cursor.fetchall():
                # Get message count and preview
                messages = self.get_messages(row['session_id'], limit=1)
                preview = "新会话"
                if messages:
                    user_msgs = [m for m in messages if m['role'] == 'user']
                    if user_msgs:
                        content = user_msgs[-1]['content']
                        preview = content[:50] + '...' if len(content) > 50 else content

                sessions.append({
                    'session_id': row['session_id'],
                    'title': row['title'],
                    'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                    'created_at': datetime.fromisoformat(row['created_at']),
                    'last_activity': datetime.fromisoformat(row['last_activity']),
                    'message_count': self.count_messages(row['session_id']),
                    'preview': preview
                })

            return sessions
        except Exception as e:
            logger.error(f"Failed to get recent sessions: {e}")
            return []

    # ==================== Utility Methods ====================

    def begin_transaction(self):
        """Begin a transaction"""
        self.connection.execute("BEGIN")

    def commit(self):
        """Commit transaction"""
        self.connection.commit()

    def rollback(self):
        """Rollback transaction"""
        self.connection.rollback()

    def execute_raw(self, sql: str, params: tuple = None) -> Any:
        """Execute raw SQL query"""
        cursor = self.connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)

        # For SELECT queries, return all rows
        if sql.strip().upper().startswith('SELECT'):
            return cursor.fetchall()

        # For other queries, commit
        self.connection.commit()
        return cursor.lastrowid
