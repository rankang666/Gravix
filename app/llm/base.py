#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: base.py
@Author: Claude
@Software: PyCharm
@Desc: Base LLM provider interface
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """
    Chat message

    Attributes:
        role: Message role ('user', 'assistant', 'system')
        content: Message content
    """
    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format"""
        return {
            'role': self.role,
            'content': self.content
        }


@dataclass
class LLMResponse:
    """
    LLM response

    Attributes:
        content: Response content
        model: Model used
        usage: Token usage information
        metadata: Additional metadata
    """
    content: str
    model: str
    usage: Dict[str, int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.usage is None:
            self.usage = {}
        if self.metadata is None:
            self.metadata = {}


class BaseLLMProvider(ABC):
    """
    Base interface for LLM providers

    All LLM providers must implement this interface.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Initialize LLM provider

        Args:
            api_key: API key for the provider
            model: Model name/identifier
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """
        Generate a response from the LLM

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse object
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[Message],
        **kwargs
    ):
        """
        Generate a streaming response from the LLM

        Args:
            messages: List of conversation messages
            **kwargs: Additional parameters

        Yields:
            Chunks of the response
        """
        pass

    def format_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Format messages to API format

        Args:
            messages: List of Message objects

        Returns:
            List of message dictionaries
        """
        return [msg.to_dict() for msg in messages]
