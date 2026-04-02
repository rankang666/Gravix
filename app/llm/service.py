#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: service.py
@Author: Claude
@Software: PyCharm
@Desc: LLM service manager
"""

import os
from typing import List, Dict, Any, Optional, AsyncIterator
from app.llm.base import BaseLLMProvider, Message, LLMResponse
from app.llm.claude import ClaudeProvider
from app.llm.openai import OpenAIProvider
from app.utils.logger import logger


class LLMService:
    """
    LLM service manager

    Manages LLM provider initialization and request handling.
    Supports multiple providers (Claude, OpenAI, etc.)
    """

    def __init__(
        self,
        provider: str = "claude",
        api_key: str = None,
        model: str = None,
        **kwargs
    ):
        """
        Initialize LLM service

        Args:
            provider: Provider name ('claude', 'openai')
            api_key: API key (if None, reads from environment)
            model: Model name
            **kwargs: Additional provider parameters
        """
        self.provider_name = provider
        self.provider: Optional[BaseLLMProvider] = None

        # Initialize provider
        self._init_provider(api_key, model, **kwargs)

    def _init_provider(self, api_key: str, model: str, **kwargs):
        """Initialize the LLM provider"""
        provider_lower = self.provider_name.lower()

        if provider_lower == 'claude':
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            model = model or "claude-3-5-sonnet-20241022"
            self.provider = ClaudeProvider(
                api_key=api_key,
                model=model,
                **kwargs
            )

        elif provider_lower == 'openai':
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            model = model or "gpt-4o"
            self.provider = OpenAIProvider(
                api_key=api_key,
                model=model,
                **kwargs
            )

        else:
            raise ValueError(f"Unknown provider: {self.provider_name}")

        logger.info(f"LLM service initialized with {self.provider_name} ({model})")

    async def chat(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """
        Generate chat response

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse
        """
        if not self.provider:
            raise RuntimeError("Provider not initialized")

        return await self.provider.generate(messages, **kwargs)

    async def chat_stream(
        self,
        messages: List[Message],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming chat response

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        if not self.provider:
            raise RuntimeError("Provider not initialized")

        async for chunk in self.provider.generate_stream(messages, **kwargs):
            yield chunk

    def create_system_message(self, content: str) -> Message:
        """Create a system message"""
        return Message(role='system', content=content)

    def create_user_message(self, content: str) -> Message:
        """Create a user message"""
        return Message(role='user', content=content)

    def create_assistant_message(self, content: str) -> Message:
        """Create an assistant message"""
        return Message(role='assistant', content=content)

    @staticmethod
    def create_messages_from_history(history: List[Dict[str, Any]]) -> List[Message]:
        """
        Create Message list from chat history

        Args:
            history: List of message dictionaries with 'role' and 'content'

        Returns:
            List of Message objects
        """
        return [
            Message(role=msg['role'], content=msg['content'])
            for msg in history
        ]

    def is_available(self) -> bool:
        """Check if service is available"""
        return self.provider is not None
