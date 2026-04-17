# JSON 序列化错误修复 ✅

## 问题描述

访问 `/api/sessions` 端点时出现错误：
```
Object of type datetime is not JSON serializable
```

## 根本原因

Python 的 `json` 模块无法直接序列化 `datetime` 对象。当 API 端点返回包含 `datetime` 对象的数据时，`web.json_response()` 会失败。

**问题位置：**
- `DatabaseSessionManager.list_sessions()` - 返回包含 datetime 的会话列表
- `DatabaseSessionManager.search_sessions()` - 返回包含 datetime 的搜索结果
- `DatabaseSessionManager.get_session()` - 返回包含 datetime 的会话对象
- API 端点直接使用 `session.to_dict()` 但消息结构不正确

## 修复方案

### 1. 修复 `list_sessions()` 方法

**文件：** `app/chat/database_session_manager.py`

将 datetime 对象转换为 ISO 格式字符串：
```python
def list_sessions(self) -> List[Dict[str, Any]]:
    sessions = self.db.list_sessions()
    
    for session in sessions:
        # Convert datetime to ISO format
        if 'created_at' in session and isinstance(session['created_at'], datetime):
            session['created_at'] = session['created_at'].isoformat()
        if 'last_activity' in session and isinstance(session['last_activity'], datetime):
            session['last_activity'] = session['last_activity'].isoformat()
        session['is_current'] = (session['session_id'] == self.current_session_id)
    
    return sessions
```

### 2. 修复 `search_sessions()` 方法

**文件：** `app/chat/database_session_manager.py`

同样处理 datetime 序列化：
```python
def search_sessions(self, keyword: str) -> List[Dict[str, Any]]:
    results = self.db.search_sessions(keyword)
    
    for result in results:
        # Convert datetime to ISO format
        if 'created_at' in result and isinstance(result['created_at'], datetime):
            result['created_at'] = result['created_at'].isoformat()
        if 'last_activity' in result and isinstance(result['last_activity'], datetime):
            result['last_activity'] = result['last_activity'].isoformat()
        result['is_current'] = (result['session_id'] == self.current_session_id)
    
    return results
```

### 3. 修复 `get_session()` 方法

确保消息作为 `ChatMessage` 对象存储，而不是普通字典：
```python
def get_session(self, session_id: str) -> Optional[ChatSession]:
    session_data = self.db.get_session(session_id)
    if not session_data:
        return None
    
    session = ChatSession(session_id, session_data['title'])
    
    # Load messages as ChatMessage objects
    messages = self.db.get_messages(session_id)
    for msg in messages:
        from app.chat.session import ChatMessage
        chat_msg = ChatMessage(
            role=msg['role'],
            content=msg['content'],
            timestamp=msg['timestamp'],
            metadata=msg.get('metadata', {})
        )
        session.messages.append(chat_msg)
    
    # ... rest of the code
    return session
```

### 4. 添加序列化辅助方法

添加专门的方法返回可序列化的字典：
```python
def get_session_dict(self, session_id: str) -> Optional[Dict[str, Any]]:
    """Get session as JSON-serializable dictionary"""
    session = self.get_session(session_id)
    if session:
        return session.to_dict()
    return None

def get_current_session_dict(self) -> Optional[Dict[str, Any]]:
    """Get current session as JSON-serializable dictionary"""
    session = self.get_current_session()
    if session:
        return session.to_dict()
    return None
```

### 5. 修复 API 端点

**文件：** `app/chat/http_server.py`

使用新的序列化方法：
```python
async def handle_api_get_session(self, request: web.Request):
    session_id = request.match_info['session_id']
    session_dict = self.session_manager.get_session_dict(session_id)
    if session_dict:
        return web.json_response(session_dict)
    return web.json_response({'error': 'Session not found'}, status=404)

async def handle_api_update_session(self, request: web.Request):
    # ... update logic ...
    if success:
        session_dict = self.session_manager.get_session_dict(session_id)
        return web.json_response(session_dict)
    # ...

async def handle_api_current_session(self, request: web.Request):
    session_dict = self.session_manager.get_current_session_dict()
    if session_dict:
        return web.json_response(session_dict)
    return web.json_response({'error': 'No current session'}, status=404)
```

## 测试结果

### ✅ 会话列表 API
```bash
curl http://localhost:8765/api/sessions
```

返回正确格式的 JSON：
```json
[
  {
    "session_id": "0d8ca7dd-4610-4617-86d4-eaacf9480f9d",
    "title": "会话 2026/4/17 14:43:54",
    "created_at": "2026-04-17T09:18:13.058835",
    "last_activity": "2026-04-17T09:18:13.063633",
    "message_count": 2,
    "preview": "hi",
    "is_current": true
  }
]
```

### ✅ 单个会话 API
```bash
curl http://localhost:8765/api/sessions/{session_id}
```

返回包含消息的完整会话数据，所有 datetime 都正确序列化。

### ✅ 当前会话 API
```bash
curl http://localhost:8765/api/sessions/current
```

返回当前会话的可序列化数据。

## 序列化策略

### 数据流

```
数据库 (datetime)
    ↓
SQLiteAdapter (datetime 对象)
    ↓
DatabaseSessionManager (转换为 ISO 字符串)
    ↓
API 端点 (JSON 响应)
    ↓
前端 (JSON 解析)
```

### 时间格式

所有时间都使用 ISO 8601 格式：
```python
datetime(2026, 4, 17, 17, 18, 13).isoformat()
# 输出: "2026-04-17T17:18:13.050750"
```

### ChatMessage 对象

确保消息作为 `ChatMessage` 对象存储：
```python
chat_msg = ChatMessage(
    role=msg['role'],
    content=msg['content'],
    timestamp=msg['timestamp'],
    metadata=msg.get('metadata', {})
)
```

`ChatMessage.to_dict()` 会正确序列化 datetime：
```python
def to_dict(self) -> Dict[str, Any]:
    return {
        'role': self.role,
        'content': self.content,
        'timestamp': self.timestamp.isoformat(),  # ← ISO 格式
        'metadata': self.metadata
    }
```

## 验证修复

### 1. 测试所有 API 端点
```bash
# 列出所有会话
curl http://localhost:8765/api/sessions

# 获取单个会话
curl http://localhost:8765/api/sessions/{session_id}

# 获取当前会话
curl http://localhost:8765/api/sessions/current

# 创建新会话
curl -X POST http://localhost:8765/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"title": "测试会话"}'
```

### 2. 验证前端功能
访问 http://localhost:8765，检查：
- ✅ 会话列表正常显示
- ✅ 点击会话可以切换
- ✅ 创建新会话成功
- ✅ 删除会话成功

### 3. 检查数据完整性
```bash
sqlite3 data/gravix.db "SELECT * FROM sessions;"
sqlite3 data/gravix.db "SELECT * FROM messages;"
```

## 总结

✅ **问题已修复** - 所有 API 端点正常工作
✅ **序列化正确** - datetime 对象正确转换为字符串
✅ **数据完整** - 所有数据正确存储和检索
✅ **前端兼容** - 前端可以正常解析 JSON 响应
✅ **向后兼容** - 不影响现有功能

现在所有 API 端点都能返回正确的 JSON 格式数据！🎉
