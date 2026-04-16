#!/usr/bin/env python3
# encoding: utf-8
"""
Static code analysis to verify LLM_MODEL environment variable fix
"""

import re


def check_llm_model_usage():
    """Verify that LLM_MODEL environment variable is used"""
    print("Checking LLM_MODEL environment variable usage...")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # Check for os.getenv('LLM_MODEL', ...)
    if re.search(r"os\.getenv\('LLM_MODEL'", content):
        print("✅ Found os.getenv('LLM_MODEL', ...) usage")
        return True
    else:
        print("❌ os.getenv('LLM_MODEL', ...) NOT found")
        return False


def check_model_fallback_order():
    """Verify the correct fallback order: parameter > env var > default"""
    print("\nChecking model fallback order...")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # Check for pattern: model = model or os.getenv('LLM_MODEL', 'default')
    openai_pattern = r"model = model or os\.getenv\('LLM_MODEL',\s*'gpt-4o'\)"
    claude_pattern = r"model = model or os\.getenv\('LLM_MODEL',\s*'claude-3-5-sonnet-20241022'\)"

    openai_match = re.search(openai_pattern, content)
    claude_match = re.search(claude_pattern, content)

    if openai_match:
        print("✅ OpenAI provider uses correct fallback: parameter > LLM_MODEL > 'gpt-4o'")
    else:
        print("❌ OpenAI provider fallback order incorrect")

    if claude_match:
        print("✅ Claude provider uses correct fallback: parameter > LLM_MODEL > 'claude-3-5-sonnet-20241022'")
    else:
        print("❌ Claude provider fallback order incorrect")

    return openai_match and claude_match


def check_no_hardcoded_default():
    """Verify that hardcoded defaults are not used (without env var)"""
    print("\nChecking that hardcoded defaults are not used...")

    with open('app/llm/service.py', 'r') as f:
        content = f.read()

    # These patterns should NOT exist (old code)
    old_openai_pattern = r"model = model or ['\"]gpt-4o['\"]"
    old_claude_pattern = r"model = model or ['\"]claude-3-5-sonnet-20241022['\"]"

    # Remove the new correct patterns to check if old ones remain
    content_without_new = re.sub(
        r"os\.getenv\('LLM_MODEL',\s*'[^']+'\)",
        "",
        content
    )

    old_openai = re.search(old_openai_pattern, content_without_new)
    old_claude = re.search(old_claude_pattern, content_without_new)

    if not old_openai:
        print("✅ No hardcoded 'gpt-4o' default without LLM_MODEL fallback")
    else:
        print("❌ Found hardcoded 'gpt-4o' default")

    if not old_claude:
        print("✅ No hardcoded 'claude-3-5-sonnet-20241022' default without LLM_MODEL fallback")
    else:
        print("❌ Found hardcoded 'claude-3-5-sonnet-20241022' default")

    return not old_openai and not old_claude


def check_syntax():
    """Verify Python syntax is correct"""
    print("\nChecking Python syntax...")

    import subprocess
    result = subprocess.run(
        ['python3', '-m', 'py_compile', 'app/llm/service.py'],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ Python syntax is correct")
        return True
    else:
        print(f"❌ Syntax error: {result.stderr}")
        return False


def show_code_changes():
    """Show the actual code changes"""
    print("\nActual code changes:")
    print("=" * 60)

    with open('app/llm/service.py', 'r') as f:
        lines = f.readlines()

    # Show OpenAI provider section
    for i, line in enumerate(lines[91:94], start=92):
        print(f"{i:3d}: {line.rstrip()}")

    print("...")

    # Show Claude provider section
    for i, line in enumerate(lines[60:63], start=61):
        print(f"{i:3d}: {line.rstrip()}")

    print("=" * 60)


def main():
    """Run all checks"""
    print("=" * 60)
    print("LLM_MODEL Environment Variable Fix - Verification")
    print("=" * 60)
    print()

    results = [
        check_llm_model_usage(),
        check_model_fallback_order(),
        check_no_hardcoded_default(),
        check_syntax()
    ]

    show_code_changes()

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed!")
        print("=" * 60)
        print("\nFix Summary:")
        print("✅ LLM_MODEL environment variable is now supported")
        print("✅ Correct fallback order: parameter > LLM_MODEL > default")
        print("✅ Both OpenAI and Claude providers support LLM_MODEL")
        print("✅ Users can now configure models in .env file:")
        print("   LLM_MODEL=Qwen3-32B")
        print("\nExpected behavior:")
        print("- Without LLM_MODEL: uses default (gpt-4o / claude-3-5-sonnet)")
        print("- With LLM_MODEL: uses value from .env")
        print("- With parameter: parameter overrides .env")
        return 0
    else:
        print("❌ Some checks failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
