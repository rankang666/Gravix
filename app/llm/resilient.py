#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/4
@Project: Gravix
@File: resilient.py
@Author: Jerry
@Software: PyCharm
@Desc: Resilient LLM provider with retry, fallback and rate limiting
"""

import asyncio
import time
from typing import List, AsyncIterator, Optional
from app.llm.base import BaseLLMProvider, Message, LLMResponse
from app.llm.claude import ClaudeProvider
from app.llm.openai import OpenAIProvider
from app.utils.logger import logger


class ResilientLLMProvider(BaseLLMProvider):
    """
    Resilient LLM provider with retry, fallback and rate limiting

    Features:
    - Automatic retry with exponential backoff
    - Multi-provider fallback
    - Rate limiting
    - Graceful degradation
    """

    def __init__(
        self,
        providers: List[BaseLLMProvider],
        max_retries: int = 3,
        retry_delay: float = 1.0,
        rate_limit: float = 0.5,  # seconds between requests
    ):
        """
        Initialize resilient provider

        Args:
            providers: List of LLM providers (will try in order)
            max_retries: Maximum retry attempts per provider
            retry_delay: Initial delay between retries (exponential backoff)
            rate_limit: Minimum time between requests
        """
        # Use first provider for config
        primary_provider = providers[0]
        super().__init__(
            primary_provider.api_key,
            primary_provider.model,
            primary_provider.temperature,
            primary_provider.max_tokens
        )

        self.providers = providers
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self._request_lock = asyncio.Lock()

    async def _acquire_rate_limit(self):
        """Acquire rate limit slot"""
        async with self._request_lock:
            now = time.time()
            time_since_last = now - self.last_request_time

            if time_since_last < self.rate_limit:
                wait_time = self.rate_limit - time_since_last
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s")
                await asyncio.sleep(wait_time)

            self.last_request_time = time.time()

    async def _try_generate(
        self,
        provider: BaseLLMProvider,
        messages: List[Message],
        **kwargs
    ) -> Optional[LLMResponse]:
        """
        Try to generate response with a specific provider

        Args:
            provider: LLM provider to use
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse or None if failed
        """
        provider_name = provider.__class__.__name__
        try:
            logger.info(f"Attempting {provider_name}...")
            response = await provider.generate(messages, **kwargs)
            logger.info(f"✅ {provider_name} succeeded")
            return response
        except Exception as e:
            logger.warning(f"❌ {provider_name} failed: {e}")
            return None

    async def generate(
        self,
        messages: List[Message],
        **kwargs
    ) -> LLMResponse:
        """
        Generate response with retry and fallback

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            LLMResponse
        """
        await self._acquire_rate_limit()

        last_error = None

        # Try each provider with retry
        for provider_index, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__

            for retry in range(self.max_retries):
                if retry > 0:
                    delay = self.retry_delay * (2 ** (retry - 1))  # Exponential backoff
                    logger.info(f"Retry {retry}/{self.max_retries} for {provider_name} after {delay:.1f}s")
                    await asyncio.sleep(delay)

                response = await self._try_generate(provider, messages, **kwargs)

                if response:
                    return response

                last_error = f"All {self.max_retries} retries failed for {provider_name}"

            logger.warning(f"Provider {provider_name} exhausted, trying next...")

        # All providers failed
        error_msg = f"All providers failed. Last error: {last_error}"
        logger.error(error_msg)

        # Return error response
        return LLMResponse(
            content="抱歉，AI服务暂时不可用。请稍后再试，或使用 /help 查看可用命令。",
            model=self.model,
            usage={},
            metadata={'error': error_msg}
        )

    async def generate_stream(
        self,
        messages: List[Message],
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate streaming response with fallback to first available provider

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Yields:
            Response chunks
        """
        await self._acquire_rate_limit()

        for provider in self.providers:
            provider_name = provider.__class__.__name__
            try:
                logger.info(f"Streaming with {provider_name}...")
                async for chunk in provider.generate_stream(messages, **kwargs):
                    yield chunk
                return
            except Exception as e:
                logger.warning(f"❌ {provider_name} streaming failed: {e}")
                continue

        # All providers failed
        yield "抱歉，AI服务暂时不可用。请稍后再试。"


def create_resilient_provider(config: dict) -> ResilientLLMProvider:
    """
    Create resilient LLM provider from configuration

    Args:
        config: Configuration dict with providers list

    Returns:
        ResilientLLMProvider instance

    Example:
        config = {
            'providers': [
                {
                    'type': 'claude',
                    'api_key': 'sk-ant-xxx',
                    'model': 'claude-3-5-sonnet-20241022'
                },
                {
                    'type': 'openai',
                    'api_key': 'sk-xxx',
                    'model': 'gpt-4o'
                }
            ],
            'max_retries': 3,
            'rate_limit': 0.5
        }
        provider = create_resilient_provider(config)
    """
    providers = []

    for provider_config in config.get('providers', []):
        provider_type = provider_config.get('type')
        api_key = provider_config.get('api_key')
        model = provider_config.get('model')
        temperature = provider_config.get('temperature', 0.7)
        max_tokens = provider_config.get('max_tokens', 4096)

        if provider_type == 'claude':
            providers.append(ClaudeProvider(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            ))
        elif provider_type == 'openai':
            providers.append(OpenAIProvider(
                api_key=api_key,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                base_url=provider_config.get('base_url'),
                timeout=provider_config.get('timeout', 300.0)
            ))
        else:
            logger.warning(f"Unknown provider type: {provider_type}")

    if not providers:
        raise ValueError("No valid providers configured")

    return ResilientLLMProvider(
        providers=providers,
        max_retries=config.get('max_retries', 3),
        retry_delay=config.get('retry_delay', 1.0),
        rate_limit=config.get('rate_limit', 0.5)
    )
