#!/usr/bin/env python3
# encoding: utf-8
"""
Test script to verify LLM_MODEL environment variable support
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_default_model_without_env():
    """Test default model when LLM_MODEL is not set"""
    print("Test 1: Default model without LLM_MODEL env var")

    # Ensure LLM_MODEL is not set
    if 'LLM_MODEL' in os.environ:
        del os.environ['LLM_MODEL']

    # Mock required env vars
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['ANTHROPIC_API_KEY'] = 'test-claude-key'

    from app.llm.service import LLMService

    # Test OpenAI provider
    service = LLMService(provider='openai')
    actual_model = service.provider.providers[0].model
    assert actual_model == 'gpt-4o', f"Expected 'gpt-4o', got '{actual_model}'"
    print(f"✅ OpenAI default model: {actual_model}")

    # Test Claude provider
    service2 = LLMService(provider='claude')
    actual_model2 = service2.provider.providers[0].model
    assert actual_model2 == 'claude-3-5-sonnet-20241022', f"Expected 'claude-3-5-sonnet-20241022', got '{actual_model2}'"
    print(f"✅ Claude default model: {actual_model2}")


def test_custom_model_with_env():
    """Test custom model when LLM_MODEL is set"""
    print("\nTest 2: Custom model with LLM_MODEL env var")

    # Set LLM_MODEL
    os.environ['LLM_MODEL'] = 'Qwen3-32B'
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['ANTHROPIC_API_KEY'] = 'test-claude-key'

    from app.llm.service import LLMService

    # Test OpenAI provider
    service = LLMService(provider='openai')
    actual_model = service.provider.providers[0].model
    assert actual_model == 'Qwen3-32B', f"Expected 'Qwen3-32B', got '{actual_model}'"
    print(f"✅ OpenAI custom model from env: {actual_model}")

    # Test Claude provider - should also use LLM_MODEL
    service2 = LLMService(provider='claude')
    actual_model2 = service2.provider.providers[0].model
    assert actual_model2 == 'Qwen3-32B', f"Expected 'Qwen3-32B', got '{actual_model2}'"
    print(f"✅ Claude custom model from env: {actual_model2}")


def test_parameter_override():
    """Test that parameter overrides env var"""
    print("\nTest 3: Parameter overrides env var")

    os.environ['LLM_MODEL'] = 'Qwen3-32B'
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['ANTHROPIC_API_KEY'] = 'test-claude-key'

    from app.llm.service import LLMService

    # Pass model parameter - should override env var
    service = LLMService(provider='openai', model='gpt-4o-mini')
    actual_model = service.provider.providers[0].model
    assert actual_model == 'gpt-4o-mini', f"Expected 'gpt-4o-mini', got '{actual_model}'"
    print(f"✅ Parameter override works: {actual_model}")


def test_different_models_per_provider():
    """Test that different providers can use different models"""
    print("\nTest 4: Different models per provider")

    os.environ['LLM_MODEL'] = 'Qwen3-32B'
    os.environ['OPENAI_API_KEY'] = 'test-key'
    os.environ['ANTHROPIC_API_KEY'] = 'test-claude-key'

    from app.llm.service import LLMService

    # Create OpenAI service
    openai_service = LLMService(provider='openai')
    openai_model = openai_service.provider.providers[0].model

    # Create Claude service with different model
    claude_service = LLMService(provider='claude', model='claude-3-opus-20240229')
    claude_model = claude_service.provider.providers[0].model

    assert openai_model == 'Qwen3-32B', f"OpenAI model should be from env"
    assert claude_model == 'claude-3-opus-20240229', f"Claude model should be from parameter"

    print(f"✅ OpenAI model: {openai_model}")
    print(f"✅ Claude model: {claude_model}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("LLM_MODEL Environment Variable Test Suite")
    print("=" * 60)
    print()

    try:
        test_default_model_without_env()
        test_custom_model_with_env()
        test_parameter_override()
        test_different_models_per_provider()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        print("\nSummary:")
        print("- Default models work without LLM_MODEL env var")
        print("- Custom models are loaded from LLM_MODEL env var")
        print("- Parameters override env vars")
        print("- Different providers can use different models")
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
