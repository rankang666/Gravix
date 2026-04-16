# ReAct Mode - Multi-Step Tool Calling

## 概述

ReAct（Reasoning + Acting）模式是一种让 LLM 通过**思考-行动-观察**循环来解决复杂任务的方法。

## 工作原理

```
用户问题
    ↓
第1轮:
  💭 Thought: [分析需要什么信息]
  🔧 Action: ::tool_name{params}
    ↓
  👁️ Observation: [工具返回结果]
    ↓
第2轮:
  💭 Thought: [根据观察结果决定下一步]
  🔧 Action: ::another_tool{params}  (如果需要更多信息)
    ↓
  👁️ Observation: [新的工具结果]
    ↓
第N轮:
  💭 Thought: [已经有足够信息]
  ✅ Answer: [最终答案]
```

## 示例场景

### 场景1: 查询项目表数量

**用户问题**: "gcc_002项目空间下有多少张表？"

```
💭 Thought: 我需要查询 DataWorks 系统来获取 gcc_002 项目中的表信息。
🔧 Action: ::dataworks.ListTables{"projectName":"gcc_002"}
    ↓
👁️ Observation: 返回了23张表的列表
    ↓
💭 Thought: 我已经收到了表列表，现在可以统计数量了。
✅ Answer: gcc_002 项目空间下共有 **23 张表**。
```

### 场景2: 多步骤查询

**用户问题**: "告诉我关于 gcc_002 项目的信息及其表结构"

```
💭 Thought: 我应该先检查 gcc_002 项目是否存在。
🔧 Action: ::dataworks.ListProjects{}
    ↓
👁️ Observation: 项目存在，状态为 Available
    ↓
💭 Thought: 项目存在。现在我需要获取表列表。
🔧 Action: ::dataworks.ListTables{"projectName":"gcc_002"}
    ↓
👁️ Observation: 返回了23张表的详细信息
    ↓
💭 Thought: 我有了项目信息和表列表，现在可以提供完整的答案。
✅ Answer: gcc_02 项目包含 **23 张表**：
- 用户数据表: users, user_profiles, user_activity
- 订单表: orders, order_items, order_status
- 产品表: products, categories, inventory
... 还有 14 张表。
```

## 配置

### 最大迭代次数

默认最大迭代次数为 5，可以在 `app/chat/server.py` 中修改：

```python
MAX_ITERATIONS = 5  # 可根据需要调整
```

### 系统提示词

ReAct 模式的提示词已自动生成，包含：

1. ReAct 格式说明（Thought/Action/Answer）
2. 可用工具列表
3. 使用示例

## 代码结构

### 核心组件

1. **ReActParser** (`app/chat/tool_calling.py`)
   - 解析 LLM 的 ReAct 响应
   - 提取思考、行动和答案

2. **ReActResponse** (`app/chat/tool_calling.py`)
   - 表示 ReAct 响应的数据结构
   - 包含 thought、action、answer 和 tool_call

3. **ChatServer._generate_response** (`app/chat/server.py`)
   - 实现 ReAct 循环逻辑
   - 处理多轮工具调用

## 测试

运行测试套件：

```bash
python3 tests/test_react_mode.py
```

测试覆盖：
- ✅ ReAct 响应解析
- ✅ 工具调用提取
- ✅ 完整场景测试
- ✅ 多步骤场景测试

## 调试

### 查看推理过程

ReAct 模式会显示推理过程：

```
💭 Thought: 我需要查询 DataWorks 系统...
🔧 Action: ::dataworks.ListTables{"projectName":"gcc_002"}
👁️ Observation: 返回了 23 张表...
✅ Answer: gcc_002 项目下共有 23 张表
```

### 日志

查看详细日志：

```python
import logging
logging.basicConfig(level=logging.INFO)
```

日志会显示：
- ReAct 响应解析结果
- 工具调用详情
- 观察结果
- 循环迭代次数

## 优势

相比单次工具调用，ReAct 模式的优势：

1. ✅ **真正的闭环** - LLM 可自主决策调用序列
2. ✅ **推理透明** - 可以看到完整的思考过程
3. ✅ **错误恢复** - 可以在工具失败后重试或尝试其他方法
4. ✅ **复杂任务** - 支持需要多步骤的复杂查询

## 使用建议

1. **简单问题** - 对于直接的问题，LLM 可以跳过工具调用直接回答
2. **复杂查询** - 对于需要多步骤的问题，LLM 会自动使用 ReAct 循环
3. **错误处理** - 如果工具调用失败，LLM 会尝试其他方法或向用户说明

## 限制

1. **最大迭代次数** - 超过 5 次迭代会返回提示，要求简化问题
2. **工具依赖** - 需要正确配置 MCP/Skills 桥接
3. **LLM 能力** - 依赖 LLM 的推理和格式遵循能力

## 后续优化

- [ ] 添加推理过程的可视化 UI
- [ ] 支持工具调用超时配置
- [ ] 添加工具调用缓存
- [ ] 支持并行工具调用
- [ ] 添加性能监控和统计

## 相关文件

- `app/chat/server.py` - ReAct 循环实现
- `app/chat/tool_calling.py` - ReAct 解析器
- `tests/test_react_mode.py` - 测试套件
- `memory/feedback_multi_step_tool_calling.md` - 设计文档
