#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/1
@Project: Gravix
@File: chat.py
@Author: Claude
@Software: PyCharm
@Desc: Chat-related data schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatHistoryResponse(BaseModel):
    """Chat history response model"""
    session_id: str
    messages: List[ChatMessage]
    message_count: int
    duration_seconds: float
