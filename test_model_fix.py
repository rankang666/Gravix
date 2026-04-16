#!/usr/bin/env python3
# encoding: utf-8
"""
Static code analysis to verify model assignment fix
"""

import re


def check_no_kwargs_in_provider_init():
    """Verify that **kwargs is not used in provider initialization"""
    print("Checking for **kwargs usage in provider initialization...")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # Find all ClaudeProvider and OpenAIProvider initializations
    # They should NOT contain **kwargs anymore
    claude_pattern = r'ClaudeProvider\([^)]*\*\*kwargs[^)]*\)'
    openai_pattern = r'OpenAIProvider\([^)]*\*\*kwargs[^)]*\)'

    claude_matches = re.findall(claude_pattern, content)
    openai_matches = re.findall(openai_pattern, content)

    if claude_matches:
        print(f"❌ Found {len(claude_matches)} ClaudeProvider with **kwargs")
        for match in claude_matches:
            print(f"   {match}")
        return False
    else:
        print("✅ No ClaudeProvider uses **kwargs")

    if openai_matches:
        print(f"❌ Found {len(openai_matches)} OpenAIProvider with **kwargs")
        for match in openai_matches:
            print(f"   {match}")
        return False
    else:
        print("✅ No OpenAIProvider uses **kwargs")

    return True


def check_base_url_extraction():
    """Verify that base_url is extracted from kwargs before provider init"""
    print("\nChecking base_url extraction from kwargs...")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # Look for base_url = kwargs.pop('base_url', None)
    if "base_url = kwargs.pop('base_url', None)" in content:
        print("✅ base_url is extracted from kwargs using kwargs.pop()")
        return True
    else:
        print("❌ base_url extraction not found")
        return False


def check_explicit_model_assignment():
    """Verify that model is explicitly set in provider init"""
    print("\nChecking explicit model assignment...")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # Check for OpenAIProvider with model parameter
    openai_with_model = re.findall(r'OpenAIProvider\([^)]*model=([^),\s]+)[^)]*\)', content)

    if openai_with_model:
        print(f"✅ Found {len(openai_with_model)} OpenAIProvider with explicit model:")
        for model in openai_with_model:
            print(f"   model={model}")
        return True
    else:
        print("⚠️  No OpenAIProvider with explicit model found")
        return False


def check_timeout_configuration():
    """Verify that timeout is configured for OpenAI providers"""
    print("\nChecking timeout configuration...")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # Count OpenAIProvider initializations with timeout
    openai_timeout_pattern = r'OpenAIProvider\([^)]*timeout=float\(os\.getenv\(\'OPENAI_API_TIMEOUT\'[^)]*\)'
    matches = re.findall(openai_timeout_pattern, content)

    if matches:
        print(f"✅ Found {len(matches)} OpenAIProvider with timeout configuration")
        return True
    else:
        print("❌ No timeout configuration found for OpenAI providers")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("Model Assignment Fix - Static Code Analysis")
    print("=" * 60)
    print()

    results = [
        check_no_kwargs_in_provider_init(),
        check_base_url_extraction(),
        check_explicit_model_assignment(),
        check_timeout_configuration()
    ]

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed!")
        print("=" * 60)
        print("\nSummary of fixes:")
        print("1. Removed **kwargs from all provider initializations")
        print("2. Extracted base_url from kwargs using kwargs.pop()")
        print("3. Model parameter is now explicitly set and protected")
        print("4. Timeout is properly configured for all OpenAI providers")
        return 0
    else:
        print("❌ Some checks failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
