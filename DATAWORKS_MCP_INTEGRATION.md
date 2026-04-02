# DataWorks MCP 集成文档

## ✅ 集成状态

DataWorks MCP已成功集成到Gravix项目中！

## 📊 测试结果

- **连接状态**: ✅ 成功连接
- **服务器**: dataworks-agent v0.0.2
- **可用工具**: 186个

## 🔧 配置文件

### 1. MCP配置 (`app/config/mcp_config.py`)

```python
MCP_SERVERS = {
    "dataworks": MCPServerConfig(
        name="alibabacloud-dataworks-mcp-server",
        enabled=True,
        transport_type="stdio",
        command="npx",
        args=["-y", "alibabacloud-dataworks-mcp-server"],
        env={}
    ),
}
```

### 2. 添加更多MCP服务器

在 `app/config/mcp_config.py` 中添加：

```python
MCP_SERVERS = {
    "dataworks": MCPServerConfig(...),

    # 添加新的MCP服务器
    "filesystem": MCPServerConfig(
        name="filesystem",
        enabled=True,
        transport_type="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
    ),

    "fastapi": MCPServerConfig(
        name="fastapi-mcp",
        enabled=True,
        transport_type="sse",
        url="http://localhost:8000/mcp"
    ),
}
```

## 🚀 使用方法

### 启动Gravix服务

```bash
/opt/miniconda3/envs/owner/bin/python run_all.py
```

### 通过WebSocket调用DataWorks工具

连接到 `ws://localhost:8765` 并发送消息：

```json
{
  "type": "mcp_call",
  "server": "dataworks",
  "tool": "ListTables",
  "arguments": {
    "projectName": "your_project"
  }
}
```

### 在Python代码中使用

```python
from app.mcp.manager import MCPManager

async def use_dataworks():
    manager = MCPManager()
    await manager.initialize()

    # 调用DataWorks工具
    result = await manager.call_tool(
        "dataworks",
        "ListTables",
        {"projectName": "your_project"}
    )

    print(result)

    await manager.shutdown()
```

## 📦 部分DataWorks工具列表

### 项目管理
- `ListProjects` - 列出所有项目
- `GetProject` - 获取项目详情
- `ListProjectMembers` - 列出项目成员

### 数据库与表
- `ListDatabases` - 列出数据库
- `ListTables` - 列出表
- `GetTable` - 获取表详情
- `ListColumns` - 列出字段

### 任务管理
- `ListTasks` - 列出任务
- `GetTask` - 获取任务详情
- `ListTaskInstances` - 列出任务实例
- `RerunTaskInstances` - 重跑任务实例

### 工作流
- `ListWorkflows` - 列出工作流
- `CreateWorkflowDefinition` - 创建工作流定义
- `StartWorkflowInstances` - 启动工作流实例

### 数据质量
- `ListDataQualityRules` - 列出数据质量规则
- `CreateDataQualityRule` - 创建数据质量规则

... 以及更多工具（共186个）

## 🔍 测试连接

运行测试脚本：

```bash
/opt/miniconda3/envs/owner/bin/python test_mcp.py
```

## 📝 注意事项

1. **网络延迟**: 首次启动DataWorks MCP可能需要10-20秒
2. **数据量**: 某些工具可能返回大量数据，建议合理使用分页参数
3. **权限**: 确保运行Gravix的用户有足够的DataWorks访问权限
4. **环境变量**: 如果需要认证，可在 `mcp_config.py` 的 `env` 字段中添加环境变量

## 🛠️ 故障排查

### 连接失败
- 检查npx是否安装: `which npx`
- 检查网络连接
- 查看日志输出

### 工具调用失败
- 确认参数格式正确
- 检查DataWorks权限设置
- 查看详细错误日志

## 📚 相关文档

- [Gravix使用指南](./GRAVIX_GUIDE.md)
- [LLM配置说明](./LLM_SETUP.md)
- [创建Skill指南](./CREATING_SKILLS.md)
