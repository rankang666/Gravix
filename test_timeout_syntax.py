#!/usr/bin/env python3
# encoding: utf-8
"""
Simple test to verify timeout parameter is correctly defined
"""

import ast
import sys


def check_timeout_parameter():
    """Check if timeout parameter is in __init__ signature"""
    print("Checking OpenAIProvider.__init__ signature...")

    with open('app/llm/openai.py', 'r') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'OpenAIProvider':
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    args = [arg.arg for arg in item.args.args]
                    defaults = item.args.defaults

                    # Check if timeout is in parameters
                    if 'timeout' in args:
                        print("✅ 'timeout' parameter found in __init__")

                        # Find the index of timeout parameter
                        timeout_idx = args.index('timeout')

                        # Check if it has a default value
                        num_required = len(args) - len(defaults)
                        if timeout_idx >= num_required:
                            print("✅ 'timeout' has default value")
                            return True
                        else:
                            print("⚠️  'timeout' missing default value")
                            return False
                    else:
                        print("❌ 'timeout' parameter NOT found in __init__")
                        return False

    print("❌ Could not find OpenAIProvider class")
    return False


def check_httpx_import():
    """Check if httpx is imported in _init_client"""
    print("\nChecking httpx import in _init_client...")

    with open('app/llm/openai.py', 'r') as f:
        content = f.read()

    if 'import httpx' in content:
        print("✅ httpx import found")
        return True
    else:
        print("❌ httpx import NOT found")
        return False


def check_timeout_assignment():
    """Check if timeout is assigned to self.timeout"""
    print("\nChecking timeout assignment...")

    with open('app/llm/openai.py', 'r') as f:
        content = f.read()

    if 'self.timeout = timeout' in content:
        print("✅ self.timeout assignment found")
        return True
    else:
        print("❌ self.timeout assignment NOT found")
        return False


def check_httpx_timeout_usage():
    """Check if httpx.Timeout is used"""
    print("\nChecking httpx.Timeout usage...")

    with open('app/llm/openai.py', 'r') as f:
        content = f.read()

    if 'httpx.Timeout(' in content:
        print("✅ httpx.Timeout usage found")
        return True
    else:
        print("❌ httpx.Timeout usage NOT found")
        return False


def check_env_example():
    """Check if .env.example has OPENAI_API_TIMEOUT"""
    print("\nChecking .env.example for OPENAI_API_TIMEOUT...")

    with open('.env.example', 'r') as f:
        content = f.read()

    if 'OPENAI_API_TIMEOUT' in content:
        print("✅ OPENAI_API_TIMEOUT found in .env.example")
        return True
    else:
        print("❌ OPENAI_API_TIMEOUT NOT found in .env.example")
        return False


def main():
    """Run all checks"""
    print("=" * 60)
    print("OpenAI Timeout Fix - Code Verification")
    print("=" * 60)
    print()

    results = [
        check_timeout_parameter(),
        check_httpx_import(),
        check_timeout_assignment(),
        check_httpx_timeout_usage(),
        check_env_example()
    ]

    print("\n" + "=" * 60)
    if all(results):
        print("✅ All checks passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some checks failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
