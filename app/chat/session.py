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

    def __init__(self, session_id: str):
        """
        Initialize chat session

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
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

    def __repr__(self) -> str:
        return (
            f"<ChatSession(id='{self.session_id}', "
            f"messages={len(self.messages)}, "
            f"duration={self.get_duration():.0f}s)>"
        )
