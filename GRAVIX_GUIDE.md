# Gravix - Skills, MCP & Chat Platform

Gravix是一个支持Skills配置、MCP协议对接和Web对话界面的综合任务处理平台。

## ✨ 功能特性

### 1. Skills System (技能系统)
- 📦 可配置的技能定义（JSON配置）
- 🔌 插件式架构，易于扩展
- ⚡ 异步执行，支持批量处理
- 🛡️ 参数验证和错误处理
- 📊 执行统计和监控

### 2. MCP Support (MCP协议支持)
- 🔄 **MCP Server**: 对外暴露工具和资源
- 🔌 **MCP Client**: 调用外部MCP服务
- 📡 支持多种传输方式（STDIO、HTTP/SSE）
- 🎯 完全兼容Model Context Protocol规范

### 3. Chat Interface (对话界面)
- 💬 WebSocket实时通信
- 🎨 现代化Web界面
- 🔗 集成Skills和MCP功能
- 📝 会话历史管理

### 4. REST API
- 🚀 FastAPI高性能框架
- 📚 自动生成API文档
- 🔒 CORS中间件支持
- 🎯 Skills、MCP、Chat管理接口

## 📁 项目结构

```
Gravix/
├── app/
│   ├── skills/              # Skills模块
│   │   ├── base.py          # 基础类
│   │   ├── registry.py      # 技能注册表
│   │   ├── executor.py      # 技能执行器
│   │   └── builtin/         # 内置技能
│   │       ├── echo.py
│   │       ├── calculate.py
│   │       ├── system_info.py
│   │       └── funboost_task.py
│   │
│   ├── mcp/                 # MCP模块
│   │   ├── protocol.py      # MCP协议定义
│   │   ├── server.py        # MCP服务器
│   │   ├── client.py        # MCP客户端
│   │   └── adapters/        # 传输适配器
│   │
│   ├── chat/                # Chat模块
│   │   ├── server.py        # WebSocket服务器
│   │   ├── session.py       # 会话管理
│   │   └── integration/     # 集成桥接器
│   │
│   ├── api/                 # REST API
│   │   ├── app.py           # FastAPI应用
│   │   └── routes/          # API路由
│   │
│   ├── schemas/             # 数据模型
│   ├── consumers/           # Funboost消费者
│   └── publisher/           # Funboost发布者
│
├── skills_configs/          # Skills配置
│   ├── builtin_skills.json  # 内置技能配置
│   └── custom_skills/       # 自定义技能
│
├── web/                     # Web前端
│   └── static/
│       └── index.html       # Chat界面
│
├── run_all.py              # 启动所有服务
├── start_api.py            # 启动REST API
├── test_skills.py          # Skills测试脚本
└── requirements.txt        # 依赖列表
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 测试Skills系统

```bash
python3 test_skills.py
```

### 3. 启动服务

#### 方式一：启动完整服务（推荐）

```bash
python3 run_all.py
```

这将启动：
- Skills系统
- WebSocket聊天服务器 (ws://localhost:8765)
- 访问 web/static/index.html 使用聊天界面

#### 方式二：仅启动REST API

```bash
python3 start_api.py
```

API服务将在 http://localhost:8000 启动
- API文档: http://localhost:8000/docs
- Web界面: http://localhost:8000/ui

## 📖 使用指南

### Skills系统使用

#### 1. 列出所有Skills

```python
from app.skills.registry import SkillRegistry

registry = SkillRegistry()
skills = registry.list_skills()
print(skills)
```

#### 2. 执行一个Skill

```python
from app.skills.executor import SkillExecutor

executor = SkillExecutor(registry)
result = await executor.execute(
    skill_id='echo',
    parameters={'message': 'Hello Gravix!'}
)
print(result.data)
```

#### 3. 创建自定义Skill

**步骤1**: 创建Skill类

```python
# app/skills/builtin/my_skill.py
from app.skills.base import BaseSkill, SkillResult

class MySkill(BaseSkill):
    async def execute(self, **kwargs) -> SkillResult:
        # 你的逻辑
        return SkillResult(success=True, data="Result")
```

**步骤2**: 添加配置

```json
// skills_configs/custom_skills/my_skill.json
{
  "skill_id": "my_skill",
  "name": "My Custom Skill",
  "version": "1.0.0",
  "description": "Does something amazing",
  "category": "custom",
  "enabled": true,
  "parameters": {
    "type": "object",
    "properties": {
      "param1": {"type": "string"}
    }
  },
  "implementation": {
    "type": "python_class",
    "class_path": "app.skills.builtin.my_skill.MySkill"
  }
}
```

### REST API使用

#### 1. 列出所有Skills

```bash
curl http://localhost:8000/api/skills/
```

#### 2. 执行Skill

```bash
curl -X POST http://localhost:8000/api/skills/execute \
  -H "Content-Type: application/json" \
  -d '{
    "skill_id": "echo",
    "parameters": {"message": "Hello!"}
  }'
```

#### 3. 获取Skill信息

```bash
curl http://localhost:8000/api/skills/echo
```

### WebSocket Chat使用

打开 `web/static/index.html` 或在浏览器中访问：

```
file:///path/to/Gravix/web/static/index.html
```

**可用命令**：
- `/help` - 显示帮助
- `/skills` - 列出所有Skills
- `/history` - 显示对话历史
- `/clear` - 清除历史

## 🔧 内置Skills

### 1. echo
简单的回显技能

```python
await executor.execute('echo', {'message': 'Hello'})
# Returns: {'echo': 'Hello', 'timestamp': '...'}
```

### 2. calculate
数学计算器

```python
await executor.execute('calculate', {'expression': '2 + 2'})
# Returns: {'result': 4}
```

### 3. system_info
获取系统信息

```python
await executor.execute('system_info', {'info_type': 'cpu'})
# Returns: CPU使用率、核心数等信息
```

### 4. funboost_task
执行Funboost任务

```python
await executor.execute(
    'funboost_task',
    {
        'queue_name': 'hello_queue',
        'task_params': {'name': 'Gravix'}
    }
)
```

## 🔌 MCP集成

### MCP Server示例

```python
from app.mcp.server import MCPServer

server = MCPServer("my-server", "1.0.0")

async def my_tool(arg: str):
    return f"Result: {arg}"

server.register_tool(
    name="my_tool",
    description="My tool",
    input_schema={"type": "object"},
    handler=my_tool
)

# Handle MCP messages
response = await server.handle_message(message_json)
```

### MCP Client示例

```python
from app.mcp.client import MCPClient
from app.mcp.adapters.sse import SSETransport

transport = SSETransport("http://localhost:8080")
client = MCPClient(transport)

await client.connect()
tools = await client.list_tools()
result = await client.call_tool("tool_name", {"param": "value"})
```

## 📊 监控和统计

### 获取执行统计

```python
stats = executor.get_stats()
print(stats)
```

### 查看特定Skill统计

```python
stats = executor.get_stats('echo')
print(stats)
# {
#     'total_executions': 10,
#     'successful_executions': 9,
#     'failed_executions': 1,
#     'avg_execution_time': 0.05
# }
```

## 🛠️ 开发指南

### 添加新的传输适配器

1. 在 `app/mcp/adapters/` 创建新文件
2. 实现 `connect()`, `send_and_receive()`, `disconnect()` 方法
3. 在MCPClient中使用

### 扩展Chat功能

1. 修改 `app/chat/server.py`
2. 添加新的消息类型处理
3. 更新前端 `web/static/index.html`

## 📝 API文档

启动API服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Funboost](https://github.com/yuzhen666666/funboost) - 任务队列框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代Web框架
- [Model Context Protocol](https://modelcontextprotocol.io/) - AI协议标准

---

**Made with ❤️ by Gravix Team**
