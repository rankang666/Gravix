# 历史会话引用功能文档

## 功能概述

现在您可以在对话中引用和访问其他会话的历史信息。这对于需要结合之前讨论内容的场景非常有用。

## 可用命令

### 1. `/sessions_list` - 列出所有会话

显示所有可用会话的列表，包括标题、预览和会话 ID。

**示例：**
```
用户: /sessions_list

助手: 📝 **所有会话:**

1. **DataWorks 项目讨论** (当前)
   - 预览: 如何创建 DataWorks 项目？
   - 消息数: 5
   - ID: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`

2. **Python 代码调试**
   - 预览: 这段代码为什么会报错？
   - 消息数: 12
   - ID: `b2c3d4e5-f6g7-8901-bcde-f12345678901`
```

### 2. `/sessions_new <标题>` - 创建新会话

创建一个带有指定标题的新会话。

**示例：**
```
用户: /sessions_new 机器学习项目讨论

助手: ✅ **新会话已创建:**

- 标题: 机器学习项目讨论
- ID: `c3d4e5f6-g7h8-9012-cdef-123456789012`
```

### 3. `/sessions_recent` - 显示最近会话

显示最近活跃的会话（排除当前会话）。

**示例：**
```
用户: /sessions_recent

助手: 📝 **最近会话:**

1. **Python 代码调试**
   - 预览: 这段代码为什么会报错？
   - 消息数: 12
   - ID: `b2c3d4e5-f6g7-8901-bcde-f12345678901`

2. **数据库设计**
   - 预览: 如何设计用户表？
   - 消息数: 8
   - ID: `d4e5f6g7-h8i9-0123-defg-234567890123`
```

### 4. `/session_context <ID> [行数]` - 加载会话上下文

加载指定会话的对话内容作为上下文。

**参数：**
- `ID`: 会话 ID（必填）
- `行数`: 要加载的消息数量（可选，默认 10）

**示例：**
```
用户: /session_context a1b2c3d4-e5f6-7890-abcd-ef1234567890

助手: 📋 **会话上下文:**

## 会话: DataWorks 项目讨论
创建时间: 2026-04-17 14:00
消息数: 5

**用户**: 如何创建 DataWorks 项目？
**助手**: 创建 DataWorks 项目的步骤如下...
**用户**: 需要什么权限？
**助手**: 您需要以下权限...
```

### 5. `/session_search <关键词>` - 搜索会话

在所有会话中搜索包含指定关键词的内容。

**示例：**
```
用户: /session_search python

助手: 🔍 **包含 'python' 的会话:**

1. **Python 代码调试**
   - 预览: 这段代码为什么会报错？
   - ID: `b2c3d4e5-f6g7-8901-bcde-f12345678901`

2. **数据分析**
   - 预览: 使用 Python 处理数据
   - ID: `e5f6g7h8-i9j0-1234-efgh-345678901234`
```

## 使用场景

### 场景 1：跨会话引用上下文

```
用户: 我们之前讨论过 DataWorks 项目，能继续那个话题吗？

助手: 我可以帮您继续之前的话题。让我先查看一下相关的历史会话。

用户: /sessions_list

助手: [显示会话列表]

用户: /session_context a1b2c3d4-e5f6-7890-abcd-ef1234567890

助手: [加载会话上下文]

用户: 好的，基于之前的内容，我想了解...

助手: 根据我们之前关于 DataWorks 项目的讨论，结合您现在的问题...
```

### 场景 2：搜索历史讨论

```
用户: 我记得之前讨论过 Python 代码优化，能帮我找找吗？

用户: /session_search python

助手: 🔍 **包含 'python' 的会话:**
1. **Python 代码调试**
   ...

用户: 太好了，让我看看第二个会话的详细内容

用户: /session_context b2c3d4e5-f6g7-8901-bcde-f12345678901

助手: [显示完整的会话内容]
```

### 场景 3：多项目并行讨论

```
用户: /sessions_new 机器学习项目

助手: [创建新会话]

用户: 在这个项目中，我想使用之前讨论过的数据处理方法

用户: /session_search 数据处理

助手: [显示相关会话]

用户: /session_context [之前的会话ID]

助手: [加载之前的讨论内容]

用户: 好的，基于之前的数据处理方法，现在我想应用到机器学习项目中...

助手: 完美的想法！结合我们之前讨论的数据处理方法...
```

## LLM 集成

系统现在会自动在对话中包含会话上下文信息：

### System Prompt 更新

每个新对话的系统提示现在包含：

```markdown
### Session Context

**Current Session:** DataWorks 项目讨论
**Messages:** 5

**Recent Sessions:**
1. Python 代码调试 (12 messages)
   Preview: 这段代码为什么会报错？...

2. 数据库设计 (8 messages)
   Preview: 如何设计用户表？...

3. API 开发 (15 messages)
   Preview: RESTful API 设计...

You can reference these sessions using commands like:
- `/sessions_list` - List all sessions
- `/session_context <ID>` - Load content from a specific session
- `/session_search <keyword>` - Search for sessions
```

### 智能上下文感知

当您在对话中提到以下内容时，AI 会自动建议使用相关命令：

- "之前的对话"
- "历史记录"
- "我们讨论过"
- "之前的会议"
- "上次说的"

## 快捷按钮

前端界面已添加会话管理快捷按钮：

- **📝 会话** - 列出所有会话
- **🕐 最近会话** - 显示最近活跃的会话

## 技术实现

### 后端新增方法

#### `SessionManager.get_session_context(session_id, max_messages)`
获取会话的格式化上下文文本。

#### `SessionManager.search_sessions(keyword)`
搜索包含关键词的会话。

#### `SessionManager.get_recent_sessions(limit)`
获取最近活跃的会话列表。

### 命令处理

在 `ChatHTTPServer._handle_command` 中添加了新命令：
- `/sessions_list`
- `/sessions_new <title>`
- `/sessions_recent`
- `/session_context <ID> [lines]`
- `/session_search <keyword>`

### System Prompt 增强

`_build_system_prompt` 方法现在自动包含：
- 当前会话信息
- 最近会话列表
- 会话引用命令说明

## 最佳实践

### 1. 使用描述性的会话标题
```
好的: "DataWorks 项目 - 数据建模"
坏的: "会话 1"
```

### 2. 及时切换到相关会话
```
讨论主题 A → 切换到主题 A 的会话
讨论主题 B → 切换到主题 B 的会话
```

### 3. 使用搜索功能查找历史内容
```
不用: 手动浏览所有会话
使用: /session_search 关键词
```

### 4. 适度加载上下文
```
查看最近: /session_context <ID> 5
查看全部: /session_context <ID> 100
```

## 数据隐私

- 所有会话数据存储在本地 `data/sessions.json`
- AI 只能访问您明确加载的会话内容
- 不会自动跨会话共享信息
- 您完全控制哪些会话内容被引用

## 示例工作流

### 完整的多会话工作流

```
# 1. 开始新项目
用户: /sessions_new 电商平台设计

# 2. 讨论用户系统
用户: 用户系统应该如何设计？
助手: [详细讨论]

# 3. 切换到另一个项目
用户: /sessions_new 移动应用开发

# 4. 需要参考之前的讨论
用户: 之前我们讨论过用户登录，能参考一下吗？
用户: /session_search 用户登录

# 5. 加载相关会话
用户: /session_context [found-session-id]

# 6. 继续新项目的讨论，结合之前的经验
用户: 基于之前的用户系统设计，移动应用的登录应该...
助手: 结合我们之前讨论的用户系统设计经验...
```

## 故障排查

### 问题：找不到会话
**解决**：
1. 使用 `/sessions_list` 确认会话存在
2. 检查会话 ID 是否正确
3. 会话 ID 是完整的 UUID 格式

### 问题：搜索结果为空
**解决**：
1. 尝试不同的关键词
2. 检查关键词拼写
3. 使用更通用的搜索词

### 问题：上下文加载不完整
**解决**：
1. 增加行数参数：`/session_context <ID> 50`
2. 检查会话是否真的有足够消息
3. 确认会话 ID 正确

## 未来增强

计划中的功能：
- 📌 **会话标签** - 为会话添加标签便于分类
- 🔗 **会话链接** - 直接引用特定消息
- 🤝 **会话合并** - 合并多个相关会话
- 📤 **会话导出** - 导出会话为文档
- 🔍 **智能推荐** - AI 推荐相关历史会话

## 总结

历史会话引用功能让您可以：

✅ 跨会话访问历史讨论
✅ 在对话中结合之前的上下文
✅ 搜索和查找特定话题
✅ 管理多个并行项目
✅ 保持对话的连贯性

现在您可以更高效地利用历史对话内容了！🎉
