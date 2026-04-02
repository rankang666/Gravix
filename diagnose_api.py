#!/usr/bin/env python
# encoding: utf-8
"""
@Time: 2026/4/2
@Project: Gravix
@File: diagnose_api.py
@Author: Jerry
@Software: PyCharm
@Desc: Claude API诊断工具
"""

import os
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from anthropic import Anthropic
from app.utils.logger import logger


def diagnose_api_key():
    """诊断Claude API密钥问题"""

    print("=" * 80)
    print("Claude API 密钥诊断工具")
    print("=" * 80)
    print()

    # 检查API密钥是否存在
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("❌ 错误: ANTHROPIC_API_KEY 环境变量未设置")
        print()
        print("请设置API密钥:")
        print("  export ANTHROPIC_API_KEY='your-api-key-here'")
        print()
        print("或者在 .env 文件中添加:")
        print("  ANTHROPIC_API_KEY=your-api-key-here")
        return False

    print(f"✅ API密钥已设置: {api_key[:10]}...{api_key[-4:]}")
    print()

    # 检查API密钥格式
    if not api_key.startswith('sk-ant-'):
        print("⚠️  警告: API密钥格式不正确")
        print("   Claude API密钥应该以 'sk-ant-' 开头")
        print()
        print("请确认您的API密钥是否正确")
        print()

    # 测试API连接
    print("正在测试API连接...")
    print()

    try:
        client = Anthropic(api_key=api_key)

        # 尝试列出可用模型（这个调用需要有效的API密钥）
        print("测试1: 获取账户信息...")
        try:
            # 使用一个简单的API调用测试
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )
            print("✅ API密钥有效！")
            print(f"   模型: claude-3-5-haiku-20241022")
            print(f"   响应: {response.content[0].text}")
            print()

        except Exception as e:
            error_str = str(e)

            if '403' in error_str or 'forbidden' in error_str.lower():
                print("❌ 403 Forbidden 错误")
                print()
                print("可能的原因:")
                print("1. API密钥无效或已过期")
                print("2. API密钥没有访问权限")
                print("3. 账户余额不足或配额已用尽")
                print("4. API密钥被禁用")
                print("5. 区域访问限制")
                print()

            elif '401' in error_str or 'unauthorized' in error_str.lower():
                print("❌ 401 Unauthorized 错误")
                print()
                print("API密钥无效或已过期")
                print()

            else:
                print(f"❌ API错误: {e}")
                print()

            print("建议的解决方案:")
            print()
            print("1. 访问 https://console.anthropic.com/")
            print("2. 检查API密钥是否有效")
            print("3. 检查账户余额和配额")
            print("4. 创建新的API密钥")
            print("5. 联系Anthropic支持: https://support.anthropic.com/")
            print()

            return False

    except ImportError:
        print("❌ 错误: anthropic 包未安装")
        print()
        print("请安装:")
        print("  pip install anthropic")
        return False

    except Exception as e:
        print(f"❌ 诊断过程中出错: {e}")
        return False

    # 测试不同的模型
    print()
    print("测试2: 检查可用模型...")
    models = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229"
    ]

    for model in models:
        try:
            response = client.messages.create(
                model=model,
                max_tokens=5,
                messages=[{"role": "user", "content": "OK"}]
            )
            print(f"   ✅ {model} - 可用")
        except Exception as e:
            if '403' in str(e):
                print(f"   ❌ {model} - 权限不足")
            else:
                print(f"   ⚠️  {model} - {str(e)[:50]}")

    print()
    print("=" * 80)
    print("诊断完成")
    print("=" * 80)
    print()

    return True


def show_workaround():
    """显示替代方案"""
    print()
    print("=" * 80)
    print("替代方案")
    print("=" * 80)
    print()

    print("如果您暂时无法解决Claude API问题，可以考虑:")
    print()
    print("方案1: 使用OpenAI")
    print("  export LLM_PROVIDER=openai")
    print("  export OPENAI_API_KEY='your-openai-key'")
    print()
    print("方案2: 使用命令模式（无需LLM）")
    print("  在聊天中使用 /help 查看可用命令")
    print("  可以使用Skills和MCP功能")
    print()
    print("方案3: 使用本地模型")
    print("  需要额外的配置，可以使用Ollama等本地模型服务")
    print()


if __name__ == '__main__':
    try:
        # 加载.env文件（如果存在）
        env_path = Path(__file__).parent / '.env'
        if env_path.exists():
            print(f"加载环境变量: {env_path}")
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
            print()

        success = diagnose_api_key()

        if not success:
            show_workaround()

    except KeyboardInterrupt:
        print("\n\n诊断已中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
