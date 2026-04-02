# Gravix - Skills, MCP & Chat Platform

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个支持**Skills配置**、**MCP协议**和**Web对话**的综合任务处理平台，基于Funboost分布式任务队列框架。

## ✨ 特性

- 🎯 **Skills系统** - 可配置、可扩展的技能调用机制（类似Claude的Function Calling）
- 🔄 **MCP协议** - 双向支持，既作为Server也作为Client
- 💬 **Web对话** - WebSocket实时聊天界面
- ⚡ **高性能** - 基于Funboost异步任务队列
- 🚀 **REST API** - FastAPI构建的管理接口

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 测试Skills系统
python3 test_skills.py

# 启动完整服务（Chat + Skills）
python3 run_all.py

# 或仅启动REST API
python3 start_api.py
```

## 📖 详细文档

查看 [GRAVIX_GUIDE.md](GRAVIX_GUIDE.md) 获取完整的使用指南。

## 📁 项目结构

```
Gravix/
├── app/
│   ├── skills/              # Skills模块 (NEW)
│   │   ├── base.py          # 基础类
│   │   ├── registry.py      # 技能注册表
│   │   ├── executor.py      # 执行器
│   │   └── builtin/         # 内置技能
│   │
│   ├── mcp/                 # MCP协议模块 (NEW)
│   │   ├── protocol.py      # 协议定义
│   │   ├── server.py        # MCP服务器
│   │   ├── client.py        # MCP客户端
│   │   └── adapters/        # 传输适配器
│   │
│   ├── chat/                # Chat模块 (NEW)
│   │   ├── server.py        # WebSocket服务器
│   │   ├── session.py       # 会话管理
│   │   └── integration/     # Skills/MCP桥接
│   │
│   ├── api/                 # REST API (NEW)
│   │   ├── app.py           # FastAPI应用
│   │   └── routes/          # API路由
│   │
│   ├── config/              # 配置层
│   │   ├── __init__.py
│   │   └── funboost_config.py
│   │
│   ├── consumers/           # funboost 消费者
│   │   ├── __init__.py
│   │   └── hello.py
│   │
│   ├── publisher/           # 任务提交入口
│   │   ├── __init__.py
│   │   └── submit.py
│   │
│   ├── schemas/             # 数据模型 (NEW)
│   ├── services/            # 业务服务
│   ├── state/               # 状态管理
│   ├── trigger/             # 触发器
│   └── utils/               # 工具函数
│
├── skills_configs/          # Skills配置 (NEW)
│   ├── builtin_skills.json
│   └── custom_skills/
│
├── web/                     # Web前端 (NEW)
│   └── static/
│       └── index.html
│
├── main.py                  # 入口文件
├── run_all.py              # 启动所有服务 (NEW)
├── start_api.py            # 启动REST API (NEW)
├── test_skills.py          # Skills测试 (NEW)
├── requirements.txt        # 依赖列表
├── GRAVIX_GUIDE.md        # 详细指南 (NEW)
└── README.md               # 本文件
```

## 🎯 核心功能

### 1. Skills系统

通过JSON配置文件定义和管理可执行技能：

```json
{
  "skill_id": "echo",
  "name": "Echo Skill",
  "description": "Echo back the input",
  "parameters": {
    "type": "object",
    "properties": {
      "message": {"type": "string"}
    }
  },
  "implementation": {
    "type": "python_class",
    "class_path": "app.skills.builtin.echo.EchoSkill"
  }
}
```

**使用示例**：
```python
from app.skills.executor import SkillExecutor
from app.skills.registry import SkillRegistry

registry = SkillRegistry()
executor = SkillExecutor(registry)

result = await executor.execute('echo', {'message': 'Hello!'})
```

### 2. MCP协议支持

**作为MCP Server**：
```python
from app.mcp.server import MCPServer

server = MCPServer("gravix-server", "1.0.0")
server.register_tool("my_tool", "Description", schema, handler)
response = await server.handle_message(message_json)
```

**作为MCP Client**：
```python
from app.mcp.client import MCPClient

client = MCPClient()
await client.connect()
result = await client.call_tool("tool_name", {"param": "value"})
```

### 3. Web对话界面

- WebSocket实时通信
- 集成Skills和MCP
- 现代化UI设计

访问：`web/static/index.html`

### 4. REST API

```bash
# 启动API服务
python3 start_api.py

# 访问文档
open http://localhost:8000/docs
```

## 📊 内置Skills

| Skill ID | 名称 | 功能 |
|----------|------|------|
| `echo` | 回显技能 | 简单的消息回显 |
| `calculate` | 计算器 | 数学表达式计算 |
| `system_info` | 系统信息 | CPU、内存、磁盘使用情况 |
| `funboost_task` | Funboost任务 | 执行Funboost队列任务 |

## 🔧 配置

### Skills配置

编辑 `skills_configs/builtin_skills.json` 或在 `skills_configs/custom_skills/` 添加新配置。

### Funboost配置

编辑 `funboost_config.py` 配置消息队列（Redis、RabbitMQ等）。

## 📝 示例

### 创建自定义Skill

1. **定义Skill类**：
```python
# app/skills/builtin/my_skill.py
from app.skills.base import BaseSkill, SkillResult

class MySkill(BaseSkill):
    async def execute(self, param1: str, **kwargs) -> SkillResult:
        return SkillResult(success=True, data=f"Processed: {param1}")
```

2. **添加配置**：
```json
// skills_configs/custom_skills/my_skill.json
{
  "skill_id": "my_skill",
  "name": "My Custom Skill",
  "enabled": true,
  "implementation": {
    "class_path": "app.skills.builtin.my_skill.MySkill"
  }
}
```

3. **使用**：
```python
result = await executor.execute('my_skill', {'param1': 'test'})
```

## 🧪 测试

```bash
# 测试Skills系统
python3 test_skills.py

# 测试API
curl http://localhost:8000/api/skills/
curl -X POST http://localhost:8000/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{"skill_id": "echo", "parameters": {"message": "test"}}'
```

## 🛠️ 开发

### 添加新的传输适配器

在 `app/mcp/adapters/` 创建新文件并实现：
- `connect()`
- `send_and_receive()`
- `disconnect()`

### 扩展Chat功能

修改 `app/chat/server.py` 添加新的消息处理逻辑。

## 📄 许可证

MIT License

## 🙏 致谢

- [Funboost](https://github.com/yuzhen666666/funboost) - 分布式任务队列框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI协议标准

---

**查看 [GRAVIX_GUIDE.md](GRAVIX_GUIDE.md) 获取完整文档！**
