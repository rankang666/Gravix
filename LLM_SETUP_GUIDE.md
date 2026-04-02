# LLM配置指南

## 问题说明

如果页面返回的是发送的内容而不是大模型的结果，这说明**LLM服务未配置**。

## 解决方案

### 方式1: 使用自动配置脚本（推荐）

```bash
./setup_llm.sh
```

按照提示选择LLM提供商和输入API密钥。

### 方式2: 手动配置

#### 步骤1: 创建 `.env` 文件

在项目根目录创建 `.env` 文件：

```bash
# Claude (Anthropic)
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=your_api_key_here
LLM_MODEL=claude-3-5-sonnet-20241022

# 或使用 OpenAI
# LLM_PROVIDER=openai
# OPENAI_API_KEY=your_api_key_here
# LLM_MODEL=gpt-4o
```

#### 步骤2: 获取API密钥

**Claude (Anthropic):**
- 访问: https://console.anthropic.com/
- 创建API密钥

**OpenAI:**
- 访问: https://platform.openai.com/api-keys
- 创建API密钥

#### 步骤3: 启动服务

```bash
# 加载环境变量
source .env

# 启动服务
/opt/miniconda3/envs/owner/bin/python run_all.py
```

## 验证配置

启动服务后，查看日志：

```
✅ LLM service ready
LLM Model: claude-3-5-sonnet-20241022
```

然后在Web UI中发送消息，应该能收到AI的回复。

## 快速测试

### 使用Python脚本测试

```python
import asyncio
from app.llm.service import LLMService
from app.llm.base import Message

async def test_llm():
    service = LLMService(provider='claude')
    response = await service.chat([
        Message(role='user', content='Hello!')
    ])
    print(response.content)

asyncio.run(test_llm())
```

### 在聊天界面测试

发送消息: "你好"
应该收到: "你好！有什么可以帮助您的吗？"

## 常见问题

### Q: 如何切换LLM提供商？
A: 修改 `.env` 文件中的 `LLM_PROVIDER` 为 `claude` 或 `openai`

### Q: 支持哪些模型？
A:
- Claude: claude-3-5-sonnet, claude-3-5-haiku, claude-3-opus
- OpenAI: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo

### Q: API密钥存储在哪里？
A: 存储在项目根目录的 `.env` 文件中（建议不要提交到Git）

### Q: 如何在没有LLM的情况下使用？
A: 不配置LLM时，系统会回显消息并提示使用命令。可以用 `/help` 查看可用命令。

## 相关文件

- `app/llm/service.py` - LLM服务管理
- `app/llm/claude.py` - Claude提供商
- `app/llm/openai.py` - OpenAI提供商
- `run_all.py` - 服务启动脚本
