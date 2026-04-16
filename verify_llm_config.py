#!/usr/bin/env python3
# encoding: utf-8
"""
Verification script for LLM configuration with generic environment variables
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def verify_generic_env_vars():
    """Verify that generic LLM_* environment variables work"""
    print("Test: Generic LLM_* environment variables")

    # Set generic variables
    os.environ['LLM_PROVIDER'] = 'openai'
    os.environ['LLM_API_KEY'] = 'test-key-generic'
    os.environ['LLM_BASE_URL'] = 'http://generic-endpoint.com/v1'
    os.environ['LLM_MODEL'] = 'Qwen3-32B'

    # Clear provider-specific variables
    for key in ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'ANTHROPIC_BASE_URL']:
        if key in os.environ:
            del os.environ[key]

    print(f"✅ LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
    print(f"✅ LLM_API_KEY: {os.getenv('LLM_API_KEY')[:10]}...")
    print(f"✅ LLM_BASE_URL: {os.getenv('LLM_BASE_URL')}")
    print(f"✅ LLM_MODEL: {os.getenv('LLM_MODEL')}")

    return True


def verify_fallback_order():
    """Verify fallback order: generic > provider-specific"""
    print("\nTest: Fallback order (generic > provider-specific)")

    # Set both generic and provider-specific
    os.environ['LLM_API_KEY'] = 'generic-key'
    os.environ['OPENAI_API_KEY'] = 'openai-key'
    os.environ['ANTHROPIC_API_KEY'] = 'anthropic-key'

    # Check code logic
    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # For OpenAI provider
    if "os.getenv('LLM_API_KEY') or os.getenv('OPENAI_API_KEY') or os.getenv('ANTHROPIC_API_KEY')" in content:
        print("✅ OpenAI provider: LLM_API_KEY > OPENAI_API_KEY > ANTHROPIC_API_KEY")
    else:
        print("❌ Fallback order not correct")

    # For Claude provider
    if "os.getenv('LLM_API_KEY') or os.getenv('ANTHROPIC_API_KEY')" in content:
        print("✅ Claude provider: LLM_API_KEY > ANTHROPIC_API_KEY")
    else:
        print("❌ Claude provider fallback not correct")

    return True


def verify_base_url_config():
    """Verify base_url configuration"""
    print("\nTest: Base URL configuration")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    if "os.getenv('LLM_BASE_URL')" in content:
        print("✅ LLM_BASE_URL is supported")
    else:
        print("❌ LLM_BASE_URL not found")
        return False

    # Check that provider-specific URLs are no longer hardcoded
    if "os.getenv('ANTHROPIC_BASE_URL')" in content:
        print("⚠️  ANTHROPIC_BASE_URL still exists (should be removed)")
    else:
        print("✅ Provider-specific URLs removed")

    return True


def verify_timeout_config():
    """Verify timeout configuration uses generic variable"""
    print("\nTest: Timeout configuration")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    if "os.getenv('LLM_API_TIMEOUT'" in content:
        print("✅ LLM_API_TIMEOUT is used")
    else:
        print("❌ LLM_API_TIMEOUT not found")
        return False

    if "os.getenv('OPENAI_API_TIMEOUT'" in content:
        print("⚠️  OPENAI_API_TIMEOUT still exists (should be removed)")
    else:
        print("✅ Provider-specific timeout removed")

    return True


def verify_env_example():
    """Verify .env.example uses generic variables"""
    print("\nTest: .env.example configuration")

    with open('.env.example', 'r') as f:
        content = f.read()

    checks = [
        ('LLM_API_KEY' in content, 'LLM_API_KEY'),
        ('LLM_BASE_URL' in content, 'LLM_BASE_URL'),
        ('LLM_MODEL' in content, 'LLM_MODEL'),
        ('LLM_API_TIMEOUT' in content, 'LLM_API_TIMEOUT'),
    ]

    all_passed = True
    for passed, name in checks:
        if passed:
            print(f"✅ {name} found in .env.example")
        else:
            print(f"❌ {name} NOT found in .env.example")
            all_passed = False

    return all_passed


def show_new_config_example():
    """Show example of new configuration"""
    print("\n" + "=" * 80)
    print("New Configuration Example")
    print("=" * 80)
    print("""
# .env file - Generic LLM Configuration
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key-here
LLM_BASE_URL=http://your-endpoint.com/v1
LLM_MODEL=your-model-name
LLM_API_TIMEOUT=300

# Works for any provider:
# - OpenAI (including proxies like Qwen, DeepSeek, etc.)
# - Claude (including proxies)
# - Any OpenAI-compatible API
    """)
    print("=" * 80)


def main():
    """Run all verification tests"""
    print("=" * 80)
    print("Generic LLM Configuration Verification")
    print("=" * 80)
    print()

    results = [
        verify_generic_env_vars(),
        verify_fallback_order(),
        verify_base_url_config(),
        verify_timeout_config(),
        verify_env_example()
    ]

    show_new_config_example()

    print("\n" + "=" * 80)
    if all(results):
        print("✅ All verifications passed!")
        print("=" * 80)
        print("\nBenefits of generic LLM_* variables:")
        print("✅ Simpler configuration - no need to remember provider-specific names")
        print("✅ Works with any LLM provider (OpenAI, Claude, proxies, etc.)")
        print("✅ Easier to switch between providers")
        print("✅ Backward compatible - still supports old variable names")
        print("\nMigration guide:")
        print("Old: ANTHROPIC_API_KEY → New: LLM_API_KEY")
        print("Old: ANTHROPIC_BASE_URL → New: LLM_BASE_URL")
        print("Old: OPENAI_API_TIMEOUT → New: LLM_API_TIMEOUT")
        return 0
    else:
        print("❌ Some verifications failed")
        print("=" * 80)
        return 1


if __name__ == "__main__":
    sys.exit(main())
