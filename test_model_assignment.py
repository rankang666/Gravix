#!/usr/bin/env python3
# encoding: utf-8
"""
Test to verify model assignment in LLM Service
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_model_assignment_openai():
    """Test that OpenAI model is correctly assigned"""
    print("Test 1: OpenAI model assignment")

    # Mock environment variables
    os.environ['OPENAI_API_KEY'] = 'test-openai-key'
    os.environ['ANTHROPIC_API_KEY'] = 'test-claude-key'
    os.environ['OPENAI_API_TIMEOUT'] = '300'

    from app.llm.service import LLMService

    # Test with custom base_url
    service = LLMService(
        provider='openai',
        base_url='http://192.168.2.85:8003/v1'
    )

    # The primary provider should be a ResilientLLMProvider
    assert service.provider is not None, "Provider should be initialized"

    # Check that providers list contains OpenAIProvider with correct model
    from app.llm.resilient import ResilientLLMProvider
    assert isinstance(service.provider, ResilientLLMProvider), \
        f"Expected ResilientLLMProvider, got {type(service.provider)}"

    # Check first provider (primary) is OpenAIProvider
    from app.llm.openai import OpenAIProvider
    primary_provider = service.provider.providers[0]
    assert isinstance(primary_provider, OpenAIProvider), \
        f"Expected OpenAIProvider, got {type(primary_provider)}"

    # Verify model is gpt-4o (default)
    assert primary_provider.model == 'gpt-4o', \
        f"Expected model 'gpt-4o', got '{primary_provider.model}'"

    # Verify base_url is set correctly
    assert primary_provider.base_url == 'http://192.168.2.85:8003/v1', \
        f"Expected base_url 'http://192.168.2.85:8003/v1', got '{primary_provider.base_url}'"

    print(f"✅ Primary provider model: {primary_provider.model}")
    print(f"✅ Primary provider base_url: {primary_provider.base_url}")

    # Check fallback provider (Claude)
    from app.llm.claude import ClaudeProvider
    fallback_provider = service.provider.providers[1]
    assert isinstance(fallback_provider, ClaudeProvider), \
        f"Expected ClaudeProvider, got {type(fallback_provider)}"

    assert fallback_provider.model == 'claude-3-5-sonnet-20241022', \
        f"Expected model 'claude-3-5-sonnet-20241022', got '{fallback_provider.model}'"

    print(f"✅ Fallback provider model: {fallback_provider.model}")


def test_model_assignment_with_custom_model():
    """Test that custom model is correctly assigned"""
    print("\nTest 2: Custom model assignment")

    os.environ['OPENAI_API_KEY'] = 'test-openai-key'
    os.environ['ANTHROPIC_API_KEY'] = 'test-claude-key'

    from app.llm.service import LLMService

    # Test with custom model
    service = LLMService(
        provider='openai',
        model='gpt-4o-mini'
    )

    from app.llm.openai import OpenAIProvider
    primary_provider = service.provider.providers[0]

    # Verify model is gpt-4o-mini (custom)
    assert primary_provider.model == 'gpt-4o-mini', \
        f"Expected model 'gpt-4o-mini', got '{primary_provider.model}'"

    print(f"✅ Custom model correctly assigned: {primary_provider.model}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("LLM Service Model Assignment Test Suite")
    print("=" * 60)
    print()

    try:
        test_model_assignment_openai()
        test_model_assignment_with_custom_model()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
