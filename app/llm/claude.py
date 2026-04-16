#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: claude.py
@Author: Claude
@Software: PyCharm
@Desc: Claude API integration (Anthropic)
"""

import asyncio
from typing import List, AsyncIterator
from app.llm.base import BaseLLMProvider, Message, LLMResponse
from app.utils.logger import logger


class ClaudeProvider(BaseLLMProvider):
    """
    Claude (Anthropic) API provider

    Requires: anthropic package
    Install: pip install anthropic
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 4096
    ):
        """
        Initialize Claude provider

        Args:
            api_key: Anthropic API key
            model: Model name (default: claude-3-5-sonnet-20241022)
            temperature: Sampling temperature
            max_tokens: Maximum tokens
        """
        super().__init__(api_key, model, temperature, max_tokens)
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize Anthropic client"""
        try:
            import os
            from anthropic import AsyncAnthropic

            # Support custom base_url (e.g., for proxy services like bigmodel.cn)
            client_kwargs = {'api_key': self.api_key}
            base_url = os.getenv('ANTHROPIC_BASE_URL')
            if base_url:
                client_kwargs['base_url'] = base_url
                logger.info(f"Using custom base_url: {base_url}")

            self._client = AsyncAnthropic(**client_kwargs)
            logger.info(f"Claude provider initialized with model: {self.model}")
        except ImportError:
            logger.error("Failed to import anthropic. Install with: pip install anthropic")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Claude client: {e}")
            raise

    async def generate(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from Claude

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse
        """
        if not self._client:
            raise RuntimeError("Claude client not initialized")

        try:
            # Separate system message from user/assistant messages
            system_message = None
            api_messages = []

            for msg in messages:
                if msg.role == 'system':
                    system_message = msg.content
                else:
                    api_messages.append(msg.to_dict())

            # Call Claude API
            response = await self._client.messages.create(
                model=self.model,
                system=system_message,
                messages=api_messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )

            # Extract response
            content = response.content[0].text

            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                }
            )

        except Exception as e:
            # Re-raise to allow fallback mechanism to work
            raise RuntimeError(f"Claude API error: {e}") from e

    async def generate_stream(
        self,
        messages: List[Message],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response from Claude

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        if not self._client:
            raise RuntimeError("Claude client not initialized")

        try:
            # Separate system message
            system_message = None
            api_messages = []

            for msg in messages:
                if msg.role == 'system':
                    system_message = msg.content
                else:
                    api_messages.append(msg.to_dict())

            # Stream response
            async with self._client.messages.stream(
                model=self.model,
                system=system_message,
                messages=api_messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Claude streaming error: {e}")
            yield f"Error: {str(e)}"
