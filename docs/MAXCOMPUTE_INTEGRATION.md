# MaxCompute/ODPS Integration

## Overview

Gravix now supports native integration with Alibaba Cloud MaxCompute (formerly ODPS) for SQL query execution and table management.

## Features

The MaxCompute integration provides 4 core tools:

### 1. List Tables (`maxcompute.list_tables`)

List all tables in the MaxCompute project.

**Usage:**
```
::maxcompute.list_tables{}
```

**Returns:**
```json
{
  "success": true,
  "count": 23,
  "tables": [
    {"name": "users", "comment": "User information table"},
    {"name": "orders", "comment": "Order data table"}
  ]
}
```

### 2. Describe Table (`maxcompute.describe_table`)

Get schema information for a specific table.

**Usage:**
```
::maxcompute.describe_table{"table_name":"users"}
```

**Returns:**
```json
{
  "success": true,
  "table_name": "users",
  "schema": "Table: users\nColumns:\n  - id: BIGINT\n  - name: STRING\n..."
}
```

### 3. Get Latest Partition (`maxcompute.get_latest_partition`)

Get the latest partition name for a partitioned table.

**Usage:**
```
::maxcompute.get_latest_partition{"table_name":"sales_data"}
```

**Returns:**
```json
{
  "success": true,
  "table_name": "sales_data",
  "latest_partition": "pt=2026-04-07",
  "is_partitioned": true
}
```

### 4. Read Query (`maxcompute.read_query`)

Execute a SELECT SQL query on the MaxCompute project.

**Usage:**
```
::maxcompute.read_query{"query":"SELECT * FROM users LIMIT 10"}
```

**Security:** Only SELECT, DESC, and SHOW queries are allowed for security reasons.

**Returns:**
```json
{
  "success": true,
  "query": "SELECT * FROM users LIMIT 10",
  "row_count": 10,
  "rows": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
  ]
}
```

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
# Alibaba Cloud Access Key
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret

# MaxCompute Project
ALIBABA_CLOUD_MAXCOMPUTE_PROJECT=your_project_name

# MaxCompute Endpoint
# Examples:
# - China (Shanghai): https://service.cn-shanghai.maxcompute.aliyun.com/api
# - China (Beijing): https://service.cn-beijing.maxcompute.aliyun.com/api
# - China (Hangzhou): https://service.cn-hangzhou.maxcompute.aliyun.com/api
# - China (Shenzhen): https://service.cn-shenzhen.maxcompute.aliyun.com/api
ALIBABA_CLOUD_MAXCOMPUTE_ENDPOINT=https://service.cn-shanghai.maxcompute.aliyun.com/api
```

### Finding Your Endpoint

To find your MaxCompute endpoint:

1. Visit [MaxCompute Console](https://maxcompute.console.aliyun.com/)
2. Select your region
3. Navigate to **Project Management** → **Your Project**
4. The endpoint URL is shown in **Project Information**

## Usage Examples

### Example 1: List All Tables

**User:** "列出所有表"

**AI Response:**
```
📋 **执行计划**

我需要查询 MaxCompute 系统来获取项目中的所有表信息。

**步骤：**

1. 列出项目中的所有表
   - 工具: ::maxcompute.list_tables{}
   - 目的: 获取完整的表列表

**预期结果：** 您将知道该项目中有多少张表以及它们的名称。

---

⚠️ **需要您的确认：**

回复 `yes` 或 `确认` 开始执行此计划
```

### Example 2: Query Data with SQL

**User:** "查询 users 表中前 10 条记录"

**AI Response:**
```
📋 **执行计划**

我需要从 MaxCompute 中查询 users 表的数据。

**步骤：**

1. 执行 SELECT 查询
   - 工具: ::maxcompute.read_query{"query":"SELECT * FROM users LIMIT 10"}
   - 目的: 获取 users 表的前 10 条记录

**预期结果：** 您将看到 users 表中的前 10 条用户数据。

---

⚠️ **需要您的确认：**

回复 `yes` 或 `确认` 开始执行此计划
```

### Example 3: Multi-Step Analysis

**User:** "分析 orders 表的结构和数据量"

**AI Response:**
```
📋 **执行计划**

我需要先了解 orders 表的结构，然后查询数据量。

**步骤：**

1. 获取 orders 表的结构信息
   - 工具: ::maxcompute.describe_table{"table_name":"orders"}
   - 目的: 了解表的列、类型和分区信息

2. 统计 orders 表的记录数
   - 工具: ::maxcompute.read_query{"query":"SELECT COUNT(*) as total FROM orders"}
   - 目的: 获取表中总记录数

**预期结果：** 您将获得 orders 表的完整结构信息和数据总量。

---

⚠️ **需要您的确认：**

回复 `yes` 或 `确认` 开始执行此计划
```

## Integration with Plan-First Mode

MaxCompute tools work seamlessly with Gravix's Plan-First Mode:

1. **Plan Generation**: LLM analyzes your request and creates an execution plan
2. **User Confirmation**: You review and approve the plan before execution
3. **Transparent Execution**: See each step and its results
4. **Final Answer**: LLM synthesizes results into a clear response

## Direct Tool Usage

You can also call tools directly without AI:

```bash
# List tables
/maxcompute.list_tables

# Describe table
/maxcompute.describe_table {"table_name": "users"}

# Execute query
/maxcompute.read_query {"query": "SELECT * FROM users LIMIT 10"}
```

## Security Features

### Query Validation

- Only `SELECT`, `DESC`, and `SHOW` queries are allowed
- All `INSERT`, `UPDATE`, `DELETE`, `DROP` operations are blocked
- Query validation happens before execution

### Connection Security

- Uses official Alibaba Cloud `pyodps` SDK
- Credentials stored in environment variables
- No hardcoded credentials in source code

## Troubleshooting

### Error: "Missing required ODPS configuration"

**Cause:** Required environment variables are not set.

**Solution:**
```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_key
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret
export ALIBABA_CLOUD_MAXCOMPUTE_PROJECT=your_project
export ALIBABA_CLOUD_MAXCOMPUTE_ENDPOINT=your_endpoint
```

### Error: "Only SELECT queries are allowed"

**Cause:** Attempted to execute a non-SELECT query.

**Solution:** Use only SELECT, DESC, or SHOW queries. Data modification is not supported.

### Error: "Table not found"

**Cause:** Table name doesn't exist in the project.

**Solution:**
1. Use `::maxcompute.list_tables{}` to see available tables
2. Check table name spelling
3. Verify you're connected to the correct project

## Testing

Run the test suite to verify your MaxCompute integration:

```bash
python tests/test_maxcompute_tools.py
```

This will test:
1. Client initialization
2. List tables
3. Describe table
4. Execute SELECT query

## Technical Implementation

### Architecture

```
User Request → LLM (Plan Generation) → User Confirmation
                                              ↓
                                      Tool Execution
                                              ↓
                    ┌─────────────────────────────────┐
                    │    MaxCompute Tool Executor     │
                    │  - list_tables                  │
                    │  - describe_table               │
                    │  - get_latest_partition         │
                    │  - read_query                   │
                    └─────────────────────────────────┘
                                              ↓
                                    MaxCompute Client (pyodps)
                                              ↓
                                   Alibaba Cloud MaxCompute
```

### Files

- `app/tools/maxcompute_tools.py` - MaxCompute client implementation
- `app/tools/maxcompute_executor.py` - Tool executor functions
- `app/chat/tool_calling.py` - Tool routing and execution
- `app/chat/server.py` - System prompt integration

## Comparison: MCP vs Native Integration

### MCP Server Approach (Original maxcompute-mcp-server)

**Pros:**
- Standards-based (MCP protocol)
- Easy integration with MCP clients
- Separate process isolation

**Cons:**
- Requires Python 3.10+
- Additional MCP server process
- More complex deployment

### Native Gravix Integration (Current)

**Pros:**
- Works with Python 3.9+
- Direct integration with Gravix tools
- Simpler deployment
- Better performance (no IPC overhead)
- Seamless Plan-First Mode integration

**Cons:**
- Gravix-specific (not portable to other MCP clients)

## References

- [MaxCompute Documentation](https://help.aliyun.com/product/27622.html)
- [PyODPS SDK](https://github.com/aliyun/aliyun-odps-python-sdk)
- [MaxCompute Endpoints](https://help.aliyun.com/document_detail/34951.html)

## Support

For issues or questions:

1. Check environment variables are set correctly
2. Verify network access to MaxCompute endpoint
3. Confirm your Access Key has required permissions
4. Review MaxCompute console for project status
