#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/17
@Project: Gravix
@File: database_session_manager.py
@Author: Claude
@Software: PyCharm
@Desc: Database-backed session manager
"""

import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.chat.session import ChatSession
from app.database.base import DatabaseAdapter
from app.utils.logger import logger


class DatabaseSessionManager:
    """
    Database-backed session manager

    Manages chat sessions using database storage instead of JSON files
    """

    def __init__(self, db_adapter: DatabaseAdapter):
        """
        Initialize database session manager

        Args:
            db_adapter: Database adapter instance
        """
        self.db = db_adapter
        self.current_session_id: Optional[str] = None

        # Initialize database connection and schema (if not already connected)
        if self.db.connection is None:
            self.db.connect()
            self.db.initialize_schema()
            logger.info("✅ Database connection and schema initialized")
        else:
            logger.info("✅ Database already connected, reusing existing connection")

        # Load/create default session
        self._initialize_default_session()

        logger.info(f"✅ Database Session Manager initialized")

    def _initialize_default_session(self):
        """Ensure there's at least one session"""
        sessions = self.list_sessions()
        if not sessions:
            logger.info("No existing sessions found, creating default session")
            self.create_session("默认会话")
        else:
            # Set current session to the most recent one
            self.current_session_id = sessions[0]['session_id'] if sessions else None

    def create_session(self, title: str = None) -> ChatSession:
        """
        Create a new session

        Args:
            title: Optional session title

        Returns:
            Created ChatSession instance
        """
        session_id = str(uuid.uuid4())
        title = title or f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # Create in database
        success = self.db.create_session(session_id, title)
        if not success:
            raise Exception("Failed to create session in database")

        # Set as current
        self.current_session_id = session_id

        # Return ChatSession object (in-memory)
        session = ChatSession(session_id, title)
        logger.info(f"Created new session: {session_id} - '{title}'")

        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        Get session by ID

        Args:
            session_id: Session ID

        Returns:
            ChatSession instance or None
        """
        session_data = self.db.get_session(session_id)
        if not session_data:
            return None

        # Create ChatSession from database data
        session = ChatSession(session_id, session_data['title'])

        # Load messages as ChatMessage objects
        messages = self.db.get_messages(session_id)
        for msg in messages:
            from app.chat.session import ChatMessage
            chat_msg = ChatMessage(
                role=msg['role'],
                content=msg['content'],
                timestamp=msg['timestamp'],
                metadata=msg.get('metadata', {})
            )
            session.messages.append(chat_msg)

        # Set metadata
        session.metadata = session_data.get('metadata', {})
        session.created_at = session_data['created_at']
        session.last_activity = session_data['last_activity']

        return session

    def get_session_dict(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session as JSON-serializable dictionary

        Args:
            session_id: Session ID

        Returns:
            Session dictionary or None
        """
        session = self.get_session(session_id)
        if session:
            return session.to_dict()
        return None

    def get_current_session(self) -> Optional[ChatSession]:
        """
        Get current active session

        Returns:
            Current ChatSession instance or None
        """
        if self.current_session_id:
            return self.get_session(self.current_session_id)
        return None

    def get_current_session_dict(self) -> Optional[Dict[str, Any]]:
        """
        Get current session as JSON-serializable dictionary

        Returns:
            Current session dictionary or None
        """
        session = self.get_current_session()
        if session:
            return session.to_dict()
        return None

    def switch_session(self, session_id: str) -> bool:
        """
        Switch to a different session

        Args:
            session_id: Target session ID

        Returns:
            True if successful, False otherwise
        """
        session_data = self.db.get_session(session_id)
        if session_data:
            self.current_session_id = session_id
            logger.info(f"Switched to session: {session_id}")
            return True

        logger.warning(f"Failed to switch to non-existent session: {session_id}")
        return False

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: Session ID to delete

        Returns:
            True if successful, False otherwise
        """
        session_data = self.db.get_session(session_id)
        if not session_data:
            logger.warning(f"Failed to delete non-existent session: {session_id}")
            return False

        # Delete from database (cascade deletes messages)
        success = self.db.delete_session(session_id)
        if not success:
            return False

        # If we deleted the current session, switch to another
        if self.current_session_id == session_id:
            sessions = self.list_sessions()
            if sessions:
                self.current_session_id = sessions[0]['session_id']
            else:
                # Create a new session if all were deleted
                self.create_session("默认会话")

        logger.info(f"Deleted session: {session_id}")
        return True

    def update_session_title(self, session_id: str, title: str) -> bool:
        """
        Update session title

        Args:
            session_id: Session ID
            title: New title

        Returns:
            True if successful, False otherwise
        """
        success = self.db.update_session(session_id, title=title)
        if success:
            logger.info(f"Updated session title: {session_id} -> '{title}'")
        return success

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions with metadata

        Returns:
            List of session dictionaries with JSON-serializable values
        """
        sessions = self.db.list_sessions()

        # Convert datetime objects to ISO format strings for JSON serialization
        for session in sessions:
            if 'created_at' in session and isinstance(session['created_at'], datetime):
                session['created_at'] = session['created_at'].isoformat()
            if 'last_activity' in session and isinstance(session['last_activity'], datetime):
                session['last_activity'] = session['last_activity'].isoformat()
            # Add is_current flag
            session['is_current'] = (session['session_id'] == self.current_session_id)

        return sessions

    def add_message_to_session(self, session_id: str, role: str, content: str,
                               metadata: Dict[str, Any] = None) -> bool:
        """
        Add a message to a session

        Args:
            session_id: Session ID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata

        Returns:
            True if successful, False otherwise
        """
        success = self.db.add_message(session_id, role, content, metadata)
        return success

    def get_session_context(self, session_id: str, max_messages: int = 10) -> Optional[str]:
        """
        Get session context as formatted text

        Args:
            session_id: Session ID
            max_messages: Maximum number of messages to include

        Returns:
            Formatted context string or None
        """
        session_data = self.db.get_session(session_id)
        if not session_data:
            return None

        messages = self.db.get_messages(session_id, limit=max_messages)
        if not messages:
            return None

        # Format context
        lines = [
            f"## 会话: {session_data['title']}",
            f"创建时间: {session_data['created_at'].strftime('%Y-%m-%d %H:%M')}",
            f"消息数: {self.db.count_messages(session_id)}",
            ""
        ]

        for msg in messages:
            role_name = "用户" if msg['role'] == 'user' else "助手"
            timestamp = msg['timestamp'].strftime('%H:%M')
            lines.append(f"[{timestamp}] **{role_name}**: {msg['content']}")

        return "\n".join(lines)

    def search_sessions(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search for sessions containing keyword

        Args:
            keyword: Search keyword

        Returns:
            List of matching sessions with context (JSON-serializable)
        """
        results = self.db.search_sessions(keyword)

        # Convert datetime objects to ISO format and add is_current flag
        for result in results:
            if 'created_at' in result and isinstance(result['created_at'], datetime):
                result['created_at'] = result['created_at'].isoformat()
            if 'last_activity' in result and isinstance(result['last_activity'], datetime):
                result['last_activity'] = result['last_activity'].isoformat()
            result['is_current'] = (result['session_id'] == self.current_session_id)

        return results

    def get_recent_sessions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent sessions excluding current

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of recent sessions
        """
        sessions = self.db.get_recent_sessions(
            limit=limit,
            exclude_session_id=self.current_session_id
        )

        # Convert datetime to isoformat for JSON serialization
        for session in sessions:
            session['created_at'] = session['created_at'].isoformat()
            session['last_activity'] = session['last_activity'].isoformat()

        return sessions

    def save_session(self, session: ChatSession) -> bool:
        """
        Save a ChatSession to database

        Args:
            session: ChatSession instance to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update session metadata
            self.db.update_session(
                session.session_id,
                title=session.title,
                metadata=session.metadata
            )

            # Save messages (delete old ones and insert new)
            self.db.delete_messages(session.session_id)
            for msg in session.messages:
                self.db.add_message(
                    session.session_id,
                    msg['role'],
                    msg['content'],
                    msg.get('metadata', {}),
                    msg.get('timestamp')
                )

            logger.debug(f"Saved session to database: {session.session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to save session: {e}")
            return False

    def __repr__(self) -> str:
        return (
            f"<DatabaseSessionManager(current='{self.current_session_id}')>"
        )
