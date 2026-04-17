#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/17
@Project: Gravix
@File: session_manager.py
@Author: Claude
@Software: PyCharm
@Desc: Multi-session management for Gravix Chat
"""

import os
import json
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.chat.session import ChatSession
from app.utils.logger import logger


class SessionManager:
    """
    Multi-session manager for Gravix Chat

    Manages multiple chat sessions with persistence support.
    """

    def __init__(self, storage_path: str = None):
        """
        Initialize session manager

        Args:
            storage_path: Path to store session data (default: data/sessions.json)
        """
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None
        self.storage_path = storage_path or 'data/sessions.json'

        # Load existing sessions
        self._load_sessions()

        # Create default session if no sessions exist
        if not self.sessions:
            logger.info("No existing sessions found, creating default session")
            self.create_session("默认会话")

    def create_session(self, title: str = None) -> ChatSession:
        """
        Create a new session

        Args:
            title: Optional session title

        Returns:
            Created ChatSession instance
        """
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id, title)
        self.sessions[session_id] = session
        self.current_session_id = session_id
        self._save_sessions()
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
        return self.sessions.get(session_id)

    def get_current_session(self) -> Optional[ChatSession]:
        """
        Get current active session

        Returns:
            Current ChatSession instance or None
        """
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None

    def switch_session(self, session_id: str) -> bool:
        """
        Switch to a different session

        Args:
            session_id: Target session ID

        Returns:
            True if successful, False otherwise
        """
        if session_id in self.sessions:
            self.current_session_id = session_id
            self._save_sessions()
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
        if session_id in self.sessions:
            session_title = self.sessions[session_id].title
            del self.sessions[session_id]

            # Switch to another session if we deleted the current one
            if self.current_session_id == session_id:
                self.current_session_id = next(iter(self.sessions)) if self.sessions else None
                # Create a new session if all sessions were deleted
                if not self.current_session_id:
                    self.create_session("默认会话")

            self._save_sessions()
            logger.info(f"Deleted session: {session_id} - '{session_title}'")
            return True
        logger.warning(f"Failed to delete non-existent session: {session_id}")
        return False

    def update_session_title(self, session_id: str, title: str) -> bool:
        """
        Update session title

        Args:
            session_id: Session ID
            title: New title

        Returns:
            True if successful, False otherwise
        """
        if session_id in self.sessions:
            old_title = self.sessions[session_id].title
            self.sessions[session_id].title = title
            self._save_sessions()
            logger.info(f"Renamed session {session_id}: '{old_title}' -> '{title}'")
            return True
        logger.warning(f"Failed to rename non-existent session: {session_id}")
        return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all sessions with metadata

        Returns:
            List of session dictionaries
        """
        return [
            {
                'session_id': sid,
                'title': session.title,
                'preview': session.get_preview(),
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'message_count': session.get_message_count(),
                'is_current': sid == self.current_session_id
            }
            for sid, session in sorted(
                self.sessions.items(),
                key=lambda x: x[1].last_activity,
                reverse=True
            )
        ]

    def _load_sessions(self):
        """Load sessions from file"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Load sessions
                    for session_data in data.get('sessions', []):
                        try:
                            session = ChatSession.from_dict(session_data)
                            self.sessions[session.session_id] = session
                        except Exception as e:
                            logger.error(f"Failed to load session {session_data.get('session_id')}: {e}")

                    # Load current session ID
                    self.current_session_id = data.get('current_session_id')

                    # Validate current session ID
                    if self.current_session_id and self.current_session_id not in self.sessions:
                        logger.warning(f"Current session ID {self.current_session_id} not found, resetting")
                        self.current_session_id = None

                logger.info(f"Loaded {len(self.sessions)} sessions from {self.storage_path}")

            except Exception as e:
                logger.error(f"Failed to load sessions from {self.storage_path}: {e}")
                logger.info("Starting with empty session manager")
        else:
            logger.info(f"No session file found at {self.storage_path}, starting fresh")

    def _save_sessions(self):
        """Save sessions to file"""
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(self.storage_path)
            if directory:
                os.makedirs(directory, exist_ok=True)

            # Prepare data
            data = {
                'sessions': [s.to_dict() for s in self.sessions.values()],
                'current_session_id': self.current_session_id
            }

            # Write to file
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.debug(f"Saved {len(self.sessions)} sessions to {self.storage_path}")

        except Exception as e:
            logger.error(f"Failed to save sessions to {self.storage_path}: {e}")

    def get_session_context(self, session_id: str, max_messages: int = 10) -> Optional[str]:
        """
        Get session context as formatted text

        Args:
            session_id: Session ID
            max_messages: Maximum number of messages to include

        Returns:
            Formatted context string or None
        """
        session = self.get_session(session_id)
        if not session:
            return None

        history = session.get_history(limit=max_messages)
        if not history:
            return None

        # Format context
        lines = [
            f"## 会话: {session.title}",
            f"创建时间: {session.created_at.strftime('%Y-%m-%d %H:%M')}",
            f"消息数: {session.get_message_count()}",
            ""
        ]

        for msg in history:
            role_name = "用户" if msg['role'] == 'user' else "助手"
            lines.append(f"**{role_name}**: {msg['content']}")

        return "\n".join(lines)

    def search_sessions(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Search for sessions containing keyword

        Args:
            keyword: Search keyword

        Returns:
            List of matching sessions with context
        """
        results = []
        keyword_lower = keyword.lower()

        for session_id, session in self.sessions.items():
            # Search in title and messages
            found = False

            # Check title
            if keyword_lower in session.title.lower():
                found = True
            else:
                # Check messages
                for msg in session.messages:
                    if keyword_lower in msg.content.lower():
                        found = True
                        break

            if found:
                results.append({
                    'session_id': session_id,
                    'title': session.title,
                    'preview': session.get_preview(),
                    'created_at': session.created_at.isoformat(),
                    'message_count': session.get_message_count(),
                    'is_current': session_id == self.current_session_id
                })

        # Sort by last activity
        results.sort(key=lambda x: self.sessions[x['session_id']].last_activity, reverse=True)
        return results

    def get_recent_sessions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent sessions excluding current

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of recent sessions
        """
        sessions = [
            {
                'session_id': sid,
                'title': session.title,
                'preview': session.get_preview(),
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'message_count': session.get_message_count()
            }
            for sid, session in self.sessions.items()
            if sid != self.current_session_id
        ]

        # Sort by last activity and limit
        sessions.sort(key=lambda x: x['last_activity'], reverse=True)
        return sessions[:limit]

    def __repr__(self) -> str:
        return (
            f"<SessionManager(sessions={len(self.sessions)}, "
            f"current='{self.current_session_id}')>"
        )
