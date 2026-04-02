# LLM集成指南

Gravix现在支持大模型(LLM)对话功能,可以通过Web界面与AI助手交互。

## 📋 目录

- [支持的大模型](#支持的大模型)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用示例](#使用示例)
- [功能特性](#功能特性)

## 🔧 支持的大模型

### Claude (Anthropic)

**模型支持:**
- `claude-3-5-sonnet-20241022` (默认)
- `claude-3-5-haiku-20241022`
- `claude-3-opus-20240229`

**安装依赖:**
```bash
pip install anthropic
```

### OpenAI

**模型支持:**
- `gpt-4o` (默认)
- `gpt-4-turbo`
- `gpt-3.5-turbo`

**安装依赖:**
```bash
pip install openai
```

## 🚀 快速开始

### 步骤1: 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装LLM依赖(根据需要选择)
pip install anthropic  # Claude
pip install openai     # OpenAI
```

### 步骤2: 配置API密钥

```bash
# Claude (Anthropic)
export ANTHROPIC_API_KEY="your_api_key_here"

# OpenAI
export OPENAI_API_KEY="your_api_key_here"
```

### 步骤3: 启动服务

```bash
# 使用Claude
LLM_PROVIDER=claude python run_all.py

# 使用OpenAI
LLM_PROVIDER=openai python run_all.py

# 不使用LLM(仅命令模式)
LLM_PROVIDER=none python run_all.py
```

### 步骤4: 打开Web界面

在浏览器中打开:
```
file:///path/to/gravix/web/static/index.html
```

或者直接双击 `web/static/index.html` 文件。

## ⚙️ 配置说明

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_PROVIDER` | LLM提供商 (claude/openai/none) | `claude` |
| `ANTHROPIC_API_KEY` | Claude API密钥 | - |
| `OPENAI_API_KEY` | OpenAI API密钥 | - |

### 自定义配置

可以修改 `run_all.py` 中的配置:

```python
# 自定义模型
llm_service = LLMService(
    provider='claude',
    model='claude-3-5-sonnet-20241022',
    temperature=0.7,
    max_tokens=4096
)
```

## 💡 使用示例

### 基本对话

```
User: 你好,请介绍一下Gravix
AI: 你好!我是Gravix,一个集成了技能系统、MCP协议和Funboost任务队列的AI助手...
```

### 执行技能

```
User: 帮我计算 2 + 2 * 3
AI: 我会使用计算技能来帮你...
[执行技能: calculate]
结果: 8
```

### 查看可用技能

```
User: /skills
AI: Available Skills:
- echoing-messages: Echo back messages with timestamps
- evaluating-expressions: Perform safe mathematical calculations
- monitoring-system-resources: Get system information
- submitting-funboost-tasks: Submit tasks to Funboost queues
```

### 查看系统信息

```
User: 查看当前CPU使用率
AI: [调用 system_info 技能]
CPU使用率: 45.2%
核心数: 8
```

## ✨ 功能特性

### 1. 智能对话

- 自然语言理解
- 上下文记忆
- 多轮对话支持

### 2. 技能集成

AI可以自动调用可用的技能:

```python
# Skills会自动加载到系统
skills/echoing-messages/
skills/evaluating-expressions/
skills/monitoring-system-resources/
skills/submitting-funboost-tasks/
```

### 3. 命令系统

支持的命令:

- `/help` - 显示帮助信息
- `/skills` - 列出可用技能
- `/skill_info <id>` - 查看技能详情
- `/skill <id> <params>` - 执行技能
- `/history` - 查看对话统计
- `/clear` - 清空对话历史

### 4. 实时通信

- WebSocket连接
- 自动重连
- 打字指示器

### 5. 美观界面

- 响应式设计
- Markdown支持
- 代码高亮
- 流畅动画

## 🔍 技术架构

```
┌─────────────┐
│   Web UI    │ (index.html)
└──────┬──────┘
       │ WebSocket
┌──────▼───────────┐
│  Chat Server     │
│  (server.py)     │
└──────┬───────────┘
       │
   ┌───┴────────────────────┐
   │                        │
┌──▼───┐              ┌─────▼──────┐
│ LLM  │              │   Skills   │
│Service│              │   Bridge   │
└──┬───┘              └─────┬──────┘
   │                        │
┌──▼─────────┐      ┌───────▼─────────┐
│Claude/OpenAI│      │ Skill Executor  │
└────────────┘      └─────────────────┘
```

## 🛠️ 故障排除

### 问题1: API密钥错误

```
ValueError: ANTHROPIC_API_KEY not found
```

**解决方法:** 设置正确的环境变量

### 问题2: 依赖缺失

```
ImportError: No module named 'anthropic'
```

**解决方法:** 安装对应的依赖包

```bash
pip install anthropic  # Claude
pip install openai     # OpenAI
```

### 问题3: WebSocket连接失败

**解决方法:**
1. 确认 `run_all.py` 正在运行
2. 检查端口8765是否被占用
3. 查看浏览器控制台错误信息

## 📚 API文档

### LLM服务

```python
from app.llm.service import LLMService
from app.llm.base import Message

# 初始化
llm_service = LLMService(provider='claude')

# 创建消息
messages = [
    Message(role='system', content='You are a helpful assistant'),
    Message(role='user', content='Hello!')
]

# 生成响应
response = await llm_service.chat(messages)
print(response.content)
```

### Chat服务器

```python
from app.chat.server import ChatServer
from app.llm.service import LLMService

# 初始化
llm_service = LLMService(provider='claude')
server = ChatServer(
    host="0.0.0.0",
    port=8765,
    llm_service=llm_service
)

# 启动
await server.start()
```

## 📝 示例对话

```
User: 你能帮我做什么?

AI: 我可以帮你:

1. **执行技能**
   - 数学计算: /skill calculate {"expression": "2+2"}
   - 系统监控: /skill system_info {"info_type": "cpu"}
   - 消息回显: /skill echo {"message": "test"}

2. **任务管理**
   - 提交Funboost任务到队列
   - 查询任务状态

3. **信息查询**
   - 查看可用技能: /skills
   - 查看对话历史: /history

4. **自然对话**
   - 回答问题
   - 提供建议
   - 技术支持

还有什么我可以帮助你的吗?

User: 帮我计算 (10 + 5) * 2

AI: 我来帮你计算 (10 + 5) * 2

[调用 evaluating-expressions 技能]

✅ **Skill 'evaluating-expressions' executed:**

```json
{
  "result": 30.0
}
```

答案是 30.0

User: 查看当前系统内存使用情况

AI: 让我查询一下系统内存使用情况...

[调用 monitoring-system-resources 技能]

✅ **Skill 'monitoring-system-resources' executed:**

```json
{
  "memory": {
    "total": 16.0,
    "available": 4.5,
    "percent": 72.0,
    "used": 11.5
  }
}
```

系统内存使用情况:
- 总内存: 16.0 GB
- 已使用: 11.5 GB (72.0%)
- 可用: 4.5 GB

内存使用率较高,建议清理一些不必要的程序。
```

## 🔗 相关文档

- [GRAVIX_GUIDE.md](GRAVIX_GUIDE.md) - 项目完整指南
- [CREATING_SKILLS.md](CREATING_SKILLS.md) - 创建技能指南
- [skills/README.md](skills/README.md) - Skills系统说明

## 📄 许可证

MIT License
