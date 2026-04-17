# 历史会话引用功能 - 快速启动

## 🚀 立即开始

### 1. 重启服务器
```bash
# 停止现有服务器
pkill -f "python.*run_all.py"

# 启动新服务器
python3 run_all.py
```

### 2. 打开浏览器
访问：**http://localhost:8765**

## 💡 快速示例

### 示例 1：查看所有会话
点击 **"📝 会话"** 按钮或输入：
```
/sessions_list
```

### 示例 2：搜索历史讨论
```
/session_search python
```

### 示例 3：加载会话内容
```
/session_context <会话ID>
```

### 示例 4：创建新会话
```
/sessions_new 新项目讨论
```

## 📋 可用命令

| 命令 | 说明 | 示例 |
|------|------|------|
| `/sessions_list` | 列出所有会话 | `/sessions_list` |
| `/sessions_new <标题>` | 创建新会话 | `/sessions_new 项目讨论` |
| `/sessions_recent` | 显示最近会话 | `/sessions_recent` |
| `/session_context <ID>` | 加载会话内容 | `/session_context abc-123` |
| `/session_search <关键词>` | 搜索会话 | `/session_search python` |

## 🎯 常见用法

### 用法 1：跨会话引用
```
1. 创建项目 A 的会话
2. 讨论技术方案
3. 创建项目 B 的会话
4. 引用项目 A 的讨论：/session_context <ID>
5. 结合之前的经验讨论项目 B
```

### 用法 2：查找历史方案
```
1. /session_search 数据库
2. 选择相关会话
3. /session_context <会话ID>
4. 基于之前的方案继续讨论
```

### 用法 3：多项目并行
```
项目 A 会话 - 讨论前端
项目 B 会话 - 讨论后端
项目 C 会话 - 讨论部署

随时切换和引用不同项目的讨论
```

## ⚡ 快捷按钮

界面新增的快捷按钮：

- **📝 会话** - 快速查看所有会话
- **🕐 最近会话** - 查看最近的会话

## 🔄 完整工作流

```
[开始新会话]
    ↓
[讨论主题 A]
    ↓
[需要参考之前的讨论]
    ↓
[/sessions_list 或 /session_search]
    ↓
[/session_context <ID>]
    ↓
[结合历史内容继续讨论]
    ↓
[切换到其他会话或创建新会话]
```

## 💪 核心优势

✅ **不会丢失上下文** - 所有历史对话都可访问
✅ **快速定位信息** - 搜索功能快速找到相关内容
✅ **跨会话引用** - 在不同会话间共享知识
✅ **AI 自动感知** - AI 知道您的历史会话

## 🎉 立即体验

1. 重启服务器
2. 打开浏览器
3. 点击 "📝 会话" 按钮
4. 开始使用历史会话引用功能！

详细文档：`SESSION_CONTEXT_FEATURE.md`
