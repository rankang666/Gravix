#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: session.py
@Author: Claude
@Software: PyCharm
@Desc: Chat session management
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import json


@dataclass
class ChatMessage:
    """
    Chat message

    Attributes:
        role: Message role ('user', 'assistant', 'system')
        content: Message content
        timestamp: Message timestamp
        metadata: Optional metadata (tool calls, etc.)
    """
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


class ChatSession:
    """
    Chat session manager

    Manages conversation history, context, and metadata for a chat session.
    """

    def __init__(self, session_id: str, title: str = None):
        """
        Initialize chat session

        Args:
            session_id: Unique session identifier
            title: Optional session title
        """
        self.session_id = session_id
        self.title = title or f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.messages: List[ChatMessage] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ):
        """
        Add a message to the session

        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            metadata: Optional metadata
        """
        message = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)
        self.last_activity = datetime.utcnow()

    def get_history(
        self,
        limit: Optional[int] = None,
        roles: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get message history

        Args:
            limit: Maximum number of messages to return (None for all)
            roles: Filter by roles (None for all)

        Returns:
            List of message dictionaries
        """
        history = [
            msg.to_dict()
            for msg in self.messages
            if roles is None or msg.role in roles
        ]

        if limit:
            return history[-limit:]

        return history

    def set_metadata(self, key: str, value: Any):
        """
        Set session metadata

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get session metadata

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.metadata.get(key, default)

    def clear_history(self):
        """Clear message history"""
        self.messages.clear()
        self.last_activity = datetime.utcnow()

    def get_message_count(self) -> int:
        """Get number of messages in session"""
        return len(self.messages)

    def get_duration(self) -> float:
        """
        Get session duration in seconds

        Returns:
            Duration in seconds
        """
        return (datetime.utcnow() - self.created_at).total_seconds()

    def is_inactive(self, timeout_seconds: int = 600) -> bool:
        """
        Check if session is inactive

        Args:
            timeout_seconds: Timeout threshold in seconds (default: 10 minutes)

        Returns:
            True if session is inactive
        """
        inactive_time = (
            datetime.utcnow() - self.last_activity
        ).total_seconds()
        return inactive_time > timeout_seconds

    def get_preview(self, max_length: int = 50) -> str:
        """
        Get session preview text (last user message)

        Args:
            max_length: Maximum length of preview text

        Returns:
            Preview text string
        """
        user_messages = [m for m in self.messages if m.role == 'user']
        if user_messages:
            content = user_messages[-1].content
            if len(content) > max_length:
                return content[:max_length] + '...'
            return content
        return "新会话"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert session to dictionary for serialization

        Returns:
            Dictionary representation of session
        """
        return {
            'session_id': self.session_id,
            'title': self.title,
            'messages': [m.to_dict() for m in self.messages],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """
        Create session from dictionary

        Args:
            data: Dictionary containing session data

        Returns:
            ChatSession instance
        """
        session = cls(data['session_id'], data['title'])

        # Load messages
        session.messages = [
            ChatMessage(
                role=m['role'],
                content=m['content'],
                timestamp=datetime.fromisoformat(m['timestamp']),
                metadata=m.get('metadata', {})
            )
            for m in data.get('messages', [])
        ]

        # Load metadata
        session.metadata = data.get('metadata', {})

        # Load timestamps
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.last_activity = datetime.fromisoformat(data['last_activity'])

        return session

    def __repr__(self) -> str:
        return (
            f"<ChatSession(id='{self.session_id}', "
            f"title='{self.title}', "
            f"messages={len(self.messages)}, "
            f"duration={self.get_duration():.0f}s)>"
        )
