#!/usrerry/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: openai.py
@Author: Claude
@Software: PyCharm
@Desc: OpenAI API integration
"""

import asyncio
from typing import List, AsyncIterator
from app.llm.base import BaseLLMProvider, Message, LLMResponse
from app.utils.logger import logger


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI API provider

    Compatible with OpenAI and Azure OpenAI
    Requires: openai package
    Install: pip install openai
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        base_url: str = None
    ):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o)
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            base_url: Optional custom base URL (for Azure/custom endpoints)
        """
        super().__init__(api_key, model, temperature, max_tokens)
        self.base_url = base_url
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI client"""
        try:
            from openai import AsyncOpenAI
            client_kwargs = {'api_key': self.api_key}
            if self.base_url:
                client_kwargs['base_url'] = self.base_url

            self._client = AsyncOpenAI(**client_kwargs)
            logger.info(f"OpenAI provider initialized with model: {self.model}")
        except ImportError:
            logger.error("Failed to import openai. Install with: pip install openai")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def generate(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """
        Generate response from OpenAI

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse
        """
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        try:
            # Call OpenAI API
            response = await self._client.chat.completions.create(
                model=self.model,
                messages=self.format_messages(messages),
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens)
            )

            # Extract response
            choice = response.choices[0]
            content = choice.message.content

            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    'input_tokens': response.usage.prompt_tokens,
                    'output_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            )

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(
                content=f"Error: {str(e)}",
                model=self.model
            )

    async def generate_stream(
        self,
        messages: List[Message],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response from OpenAI

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        if not self._client:
            raise RuntimeError("OpenAI client not initialized")

        try:
            # Stream response
            stream = await self._client.chat.completions.create(
                model=self.model,
                messages=self.format_messages(messages),
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                stream=True
            )

            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield f"Error: {str(e)}"
