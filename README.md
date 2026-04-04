# Gravix - AI Agent Platform with Skills, MCP & LLM

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个功能强大的**AI Agent平台**，集成**Skills系统**、**MCP协议**、**LLM对话**和**任务队列**，支持快速构建智能应用。

## ✨ 核心特性

### 🎯 Skills系统
- **可配置的技能调用** - 类似Claude的Function Calling
- **4个内置技能** - calculate, echo, system_info, funboost_task
- **自定义技能** - 支持扩展和配置
- **异步执行** - 基于Funboost的高性能任务队列

### 🔄 MCP协议集成
- **DataWorks集成** - 186个阿里云DataWorks工具
- **双向支持** - 既可作为Server也可作为Client
- **stdio/SSE传输** - 灵活的通信方式
- **多服务器管理** - 支持连接多个MCP服务器

### 💬 智能对话
- **WebSocket实时聊天** - 低延迟的双向通信
- **LLM集成** - 支持Claude和OpenAI
- **工具调用** - 对话中直接调用Skills和MCP工具
- **会话管理** - 完整的对话历史和上下文

### 🚀 REST API
- **FastAPI框架** - 高性能异步API
- **Swagger文档** - 自动生成的API文档
- **认证支持** - 安全的API访问
- **健康检查** - 服务状态监控

### ⚡ 高性能
- **异步架构** - 基于asyncio的异步处理
- **任务队列** - Funboost分布式任务队列
- **连接池** - 优化的数据库和API连接
- **缓存机制** - 智能的结果缓存

## 🚀 快速开始

### 方式1：使用Docker（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
nano .env  # 编辑配置，填入API密钥

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 访问应用
# Web UI: 打开 web/static/index.html
# WebSocket: ws://localhost:8765
# API文档: http://localhost:8000/docs
```

**Docker优势：**
- ✅ 开箱即用，无需Python环境
- ✅ 环境隔离，不会影响系统
- ✅ 一键启动和停止
- ✅ 易于部署和维护

**详细文档：** 查看 [DOCKER.md](DOCKER.md)

### 方式2：本地安装

### 1. 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env  # 或使用你喜欢的编辑器
```

**必需配置：**

```bash
# LLM配置（至少配置一个）
LLM_PROVIDER=claude  # 或 openai
ANTHROPIC_API_KEY=your_anthropic_api_key  # Claude
# OPENAI_API_KEY=your_openai_api_key  # OpenAI

# DataWorks配置（可选，用于MCP功能）
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
ALIBABA_CLOUD_REGION_ID=cn-hangzhou
```

### 3. 启动服务

```bash
# 启动所有服务（推荐）
python run_all.py

# 或仅启动API服务
python start_api.py
```

### 4. 访问应用

- **Web UI**: 打开浏览器访问 `file:///path/to/web/static/index.html`
  或直接双击 `web/static/index.html` 文件
- **API文档**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8765

## 📖 使用指南

### Web界面使用

1. **打开Web UI**
   ```bash
   # 在浏览器中打开
   open web/static/index.html  # Mac
   # 或双击文件
   ```

2. **使用快捷按钮**
   - 📖 **Help** - 查看帮助信息
   - 🔧 **Skills** - 列出可用技能
   - ⚡ **MCP列表** - 显示MCP工具
   - 📁 **项目** - 查看DataWorks项目
   - 🕐 **时间转换** - 时间戳转换示例
   - 📊 **History** - 对话历史
   - 🗑️ **Clear** - 清空对话

3. **对话中使用工具**
   ```
   你好                    # 普通对话
   /skills                # 查看技能列表
   2+2等于多少            # 自动调用calculate技能
   dataworks有多少项目     # 自动调用MCP工具
   ::system_info{}        # 直接调用工具
   ```

### 命令行使用

```bash
# 测试Skills
python -c "
from app.skills.executor import SkillExecutor
executor = SkillExecutor()
result = executor.execute('calculate', {'expression': '2+2'})
print(result)
"

# 测试MCP
python -c "
import asyncio
from app.mcp.manager import MCPManager

async def test():
    manager = MCPManager()
    await manager.initialize()
    result = await manager.call_tool('dataworks', 'ListProjects', {})
    print(result)

asyncio.run(test())
"
```

## 📁 项目结构

```
Gravix/
├── app/                      # 应用主目录
│   ├── skills/              # Skills模块
│   │   ├── base.py          # 基础类
│   │   ├── registry.py      # 技能注册表
│   │   ├── executor.py      # 执行器
│   │   └── builtin/         # 内置技能
│   │
│   ├── mcp/                 # MCP协议模块
│   │   ├── protocol.py      # 协议定义
│   │   ├── client.py        # MCP客户端
│   │   ├── manager.py       # MCP服务器管理
│   │   └── adapters/        # 传输适配器
│   │
│   ├── chat/                # 聊天模块
│   │   ├── server.py        # WebSocket服务器
│   │   ├── tool_calling.py  # 工具调用
│   │   └── integration/     # 集成桥接
│   │
│   ├── llm/                 # LLM集成
│   │   ├── claude.py        # Claude提供商
│   │   ├── openai.py        # OpenAI提供商
│   │   └── service.py       # LLM服务
│   │
│   ├── api/                 # REST API
│   │   ├── app.py           # FastAPI应用
│   │   └── routes/          # API路由
│   │
│   ├── config/              # 配置
│   ├── schemas/             # 数据模型
│   └── utils/               # 工具函数
│
├── skills/                  # 技能脚本
│   ├── calculate/           # 计算器
│   ├── echo/                # 回显
│   ├── system_info/         # 系统信息
│   └── funboost_task/       # Funboost任务
│
├── web/                     # Web前端
│   └── static/
│       └── index.html       # 聊天界面
│
├── tests/                   # 测试文件
├── archive/                 # 归档文件
├── run_all.py              # 启动脚本
├── requirements.txt        # 依赖列表
├── .env.example            # 配置模板
└── README.md               # 本文件
```

## 🎯 核心功能详解

### 1. Skills系统

Skills是可执行的函数，可通过对话或API调用：

**内置技能：**
- `calculate` - 数学计算
- `echo` - 文本回显
- `system_info` - 系统信息查询
- `funboost_task` - Funboost任务执行

**调用格式：**
```
::skill_name{param1=value1}
::calculate{expression=2+2*3}
::system_info{info_type=all}
```

### 2. MCP工具调用

支持186个DataWorks工具：

**调用格式：**
```
::server.tool_name{}
::dataworks.ListProjects{}
::dataworks.ConvertTimestamps{Timestamps=[1714567890]}
```

**命令方式：**
```
/mcp_call dataworks.ListProjects {}
/mcp_call dataworks.ConvertTimestamps {"Timestamps": [1714567890]}
```

### 3. LLM对话

集成Claude和OpenAI，支持：
- 上下文感知对话
- 自动工具调用
- 流式响应
- 错误处理

## 🔧 配置说明

### LLM配置

**Claude:**
```bash
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxx
LLM_MODEL=claude-3-5-sonnet-20241022
```

**OpenAI:**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
LLM_MODEL=gpt-4o
```

### DataWorks配置

```bash
ALIBABA_CLOUD_ACCESS_KEY_ID=your_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret
ALIBABA_CLOUD_REGION_ID=cn-hangzhou
```

支持的Region：
- `cn-hangzhou` (华东1)
- `cn-beijing` (华北2)
- `cn-shenzhen` (华南1)
- `cn-shanghai` (华东2)

### 服务端口配置

编辑 `run_all.py`:
```python
# WebSocket服务
WS_HOST = "0.0.0.0"
WS_PORT = 8765

# REST API服务
API_HOST = "0.0.0.0"
API_PORT = 8000
```

## 📚 相关文档

- [GRAVIX_GUIDE.md](GRAVIX_GUIDE.md) - 完整使用指南
- [LLM_SETUP_GUIDE.md](LLM_SETUP_GUIDE.md) - LLM配置指南
- [DATAWORKS_MCP_INTEGRATION.md](DATAWORKS_MCP_INTEGRATION.md) - DataWorks集成文档
- [CREATING_SKILLS.md](CREATING_SKILLS.md) - 创建自定义技能
- [CHANGELOG.md](CHANGELOG.md) - 版本更新记录

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Funboost](https://github.com/yhyzhyz/funboost) - 分布式任务队列框架
- [Anthropic](https://www.anthropic.com) - Claude API
- [OpenAI](https://openai.com) - GPT API
- [Model Context Protocol](https://modelcontextprotocol.io) - MCP协议

---

**Made with ❤️ by the Gravix Team**
