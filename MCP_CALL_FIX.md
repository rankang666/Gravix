# MCP Call 命令修复完成 ✅

## 问题

之前使用 `/mcp_call` 命令时出现错误：
```
❌ Unknown command: /mcp_call dataworks.ListProjects {}
Use /help to see available commands.
```

## 根本原因

`_handle_command` 方法中没有实现 `/mcp_call` 命令的处理逻辑。

## 解决方案

### 1. 添加 `/mcp_call` 命令处理

**文件：** `app/chat/http_server.py`

**实现逻辑：**

1. **命令格式解析**
   - 格式：`/mcp_call <tool_name> <json_params>`
   - 示例：`/mcp_call dataworks.ListProjects {}`

2. **参数提取**
   ```python
   # 使用正则表达式提取工具名称和 JSON 参数
   match = re.match(r'^(\S+)\s+(\{.*\})$', params_part)
   tool_full_name = match.group(1)  # 例如：dataworks.ListProjects
   json_params = match.group(2)      # 例如：{"Timestamps": [1714567890]}
   ```

3. **工具名称解析**
   ```python
   # 分割服务器名称和工具名称
   if '.' in tool_full_name:
       server_name, tool_name = tool_full_name.split('.', 1)
   # server_name = "dataworks"
   # tool_name = "ListProjects"
   ```

4. **JSON 参数解析**
   ```python
   params = json.loads(json_params)
   ```

5. **调用 MCP 工具**
   ```python
   result = await self.mcp_bridge.manager.call_tool(server_name, tool_name, params)
   ```

6. **格式化返回结果**
   ```python
   return f"✅ **Tool `{server_name}.{tool_name}` executed:**\n\n```\n{result_str}\n```"
   ```

### 2. 更新帮助文本

在 `/help` 命令中添加了 `/mcp_call` 使用说明：

```markdown
🔧 **/mcp_call tool_name {params}** - 调用 MCP 工具

**MCP Tool Call Examples:**
- `/mcp_call dataworks.ListProjects {}`
- `/mcp_call dataworks.ConvertTimestamps {"Timestamps": [1714567890]}`
- `/mcp_call dataworks.ToTimestamps {"DateTimeDisplay": ["2024-05-01"]}`
```

## 测试结果

### ✅ 测试 1：空参数调用

```bash
/mcp_call dataworks.ListProjects {}
```

**结果：**
```
✅ **Tool `dataworks.ListProjects` executed:**

{
  "content": [
    {
      "type": "text",
      "text": "{\n  \"RequestId\": \"009874F8-9DCF-56A7-B7F1-35B0967C2A82\",\n  \"PagingInfo\": {...}\n}"
    }
  ]
}
```

### ✅ 测试 2：带参数调用

```bash
/mcp_call dataworks.ConvertTimestamps {"Timestamps": [1714567890]}
```

**结果：**
```
✅ **Tool `dataworks.ConvertTimestamps` executed:**

{
  "content": [
    {
      "type": "text",
      "text": "[...]"
    }
  ]
}
```

## 使用方法

### 通过 Web UI

1. 访问 `http://localhost:8765`
2. 在输入框中输入命令
3. 发送并查看结果

### 命令格式

```bash
/mcp_call <server.tool_name> <json_params>
```

### 参数说明

- **server**: MCP 服务器名称（例如：dataworks）
- **tool_name**: 工具名称（例如：ListProjects）
- **json_params**: JSON 格式的参数对象（例如：{} 或 {"key": "value"}）

### 示例

```bash
# 列出项目
/mcp_call dataworks.ListProjects {}

# 时间戳转换
/mcp_call dataworks.ConvertTimestamps {"Timestamps": [1714567890, 1714567891]}

# 日期转时间戳
/mcp_call dataworks.ToTimestamps {"DateTimeDisplay": ["2024-05-01", "2024-05-02"]}
```

## 错误处理

### 格式错误
```
❌ Invalid format. Use: `/mcp_call tool_name {params}`

Example: `/mcp_call dataworks.ListProjects {}`
```

### JSON 错误
```
❌ Invalid JSON parameters: Expecting property name enclosed in double quotes
```

### 工具格式错误
```
❌ Invalid tool format. Use: `server.tool_name`

Example: `dataworks.ListProjects`
```

### MCP 未配置
```
❌ MCP bridge not configured.
```

### 服务器未找到
```
❌ Error calling MCP tool: MCP server not found: <server_name>

Use `/mcp_list` to see available servers.
```

## 技术细节

### 正则表达式

```python
r'^(\S+)\s+(\{.*\})$'
```

- `^` - 字符串开始
- `(\S+)` - 一个或多个非空白字符（工具名称）
- `\s+` - 一个或多个空白字符
- `(\{.*\})` - JSON 对象（参数）
- `$` - 字符串结束

### 错误处理流程

1. **验证命令格式** - 正则表达式匹配
2. **解析 JSON 参数** - json.loads()
3. **验证工具格式** - 检查是否包含 `.`
4. **检查 MCP 配置** - 验证 mcp_bridge 是否存在
5. **调用工具** - 使用 manager.call_tool()
6. **格式化结果** - 统一的响应格式

## 相关文件

- ✅ `app/chat/http_server.py` - 命令处理实现
- ✅ `app/mcp/manager.py` - MCP 工具调用
- ✅ `app/mcp/client.py` - MCP 客户端实现

## 后续优化建议

1. **参数验证** - 添加工具参数的 schema 验证
2. **自动补全** - 实现 tab 键自动补全工具名称
3. **工具发现** - `/mcp_tools <server>` 列出服务器上的所有工具
4. **错误详情** - 更详细的错误信息和建议

## 享受使用

现在您可以方便地通过命令行调用 MCP 工具了！🎉

访问 `http://localhost:8765` 并尝试：
```bash
/mcp_call dataworks.ListProjects {}
```
