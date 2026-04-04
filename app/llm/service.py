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
from app.llm.resilient import ResilientLLMProvider, create_resilient_provider
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
        resilient: bool = True,
        **kwargs
    ):
        """
        Initialize LLM service

        Args:
            provider: Provider name ('claude', 'openai')
            api_key: API key (if None, reads from environment)
            model: Model name
            resilient: Enable resilient mode with retry and fallback
            **kwargs: Additional provider parameters
        """
        self.provider_name = provider
        self.provider: Optional[BaseLLMProvider] = None
        self.resilient_enabled = resilient

        # Initialize provider
        self._init_provider(api_key, model, **kwargs)

    def _init_provider(self, api_key: str, model: str, **kwargs):
        """Initialize the LLM provider"""
        provider_lower = self.provider_name.lower()

        # Collect available providers for resilient mode
        providers = []

        if provider_lower == 'claude':
            model = model or "claude-3-5-sonnet-20241022"
            api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")

            # Add primary provider
            providers.append(ClaudeProvider(
                api_key=api_key,
                model=model,
                **kwargs
            ))

            # Add fallback provider if available
            fallback_key = os.getenv('ANTHROPIC_API_KEY_FALLBACK')
            if fallback_key and fallback_key != api_key:
                logger.info("Fallback Claude API key found, enabling resilient mode")
                providers.append(ClaudeProvider(
                    api_key=fallback_key,
                    model=model,
                    **kwargs
                ))

            # Check if OpenAI is available as fallback
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                logger.info("OpenAI API key found, adding as fallback")
                providers.append(OpenAIProvider(
                    api_key=openai_key,
                    model="gpt-4o",
                    **kwargs
                ))

        elif provider_lower == 'openai':
            model = model or "gpt-4o"
            api_key = api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")

            # Add primary provider
            providers.append(OpenAIProvider(
                api_key=api_key,
                model=model,
                **kwargs
            ))

            # Check if Claude is available as fallback
            claude_key = os.getenv('ANTHROPIC_API_KEY')
            if claude_key:
                logger.info("Claude API key found, adding as fallback")
                providers.append(ClaudeProvider(
                    api_key=claude_key,
                    model="claude-3-5-sonnet-20241022",
                    **kwargs
                ))

        else:
            raise ValueError(f"Unknown provider: {self.provider_name}")

        # Use resilient provider if multiple providers available and enabled
        if self.resilient_enabled and len(providers) > 1:
            logger.info(f"Using resilient mode with {len(providers)} providers")
            self.provider = ResilientLLMProvider(
                providers=providers,
                max_retries=kwargs.get('max_retries', 3),
                retry_delay=kwargs.get('retry_delay', 1.0),
                rate_limit=kwargs.get('rate_limit', 0.5)
            )
            logger.info(f"LLM service initialized with resilient {self.provider_name} ({model})")
        else:
            # Use single provider
            self.provider = providers[0]
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
