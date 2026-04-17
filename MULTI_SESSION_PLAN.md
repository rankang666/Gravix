# 多会话支持功能实现计划

## 目标
实现多会话管理功能，允许用户创建、切换、管理和查看多个独立的对话会话。

## 功能需求
1. **多会话管理** - 支持创建多个独立会话
2. **会话列表展示** - 左侧栏显示所有会话
3. **会话切换** - 点击会话项切换当前会话
4. **会话操作** - 新建、删除、重命名会话
5. **会话持久化** - 使用 JSON 文件存储会话数据
6. **向后兼容** - 保持现有单会话模式可用

## 架构设计

### 1. 数据结构设计

#### 1.1 扩展 ChatSession 类
```python
# app/chat/session.py

class ChatSession:
    def __init__(self, session_id: str, title: str = None):
        self.session_id = session_id
        self.title = title or f"会话 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.messages: List[ChatMessage] = []
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()

    def get_preview(self, max_length: int = 50) -> str:
        """获取会话预览文本（最后一条用户消息）"""
        user_messages = [m for m in self.messages if m.role == 'user']
        if user_messages:
            content = user_messages[-1].content
            return content[:max_length] + '...' if len(content) > max_length else content
        return "新会话"

    def to_dict(self) -> Dict[str, Any]:
        """序列化会话为字典"""
        return {
            'session_id': self.session_id,
            'title': self.title,
            'messages': [m.to_dict() for m in self.messages],
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'last_activity': self.last_activity.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """从字典反序列化会话"""
        session = cls(data['session_id'], data['title'])
        session.messages = [
            ChatMessage(
                role=m['role'],
                content=m['content'],
                timestamp=datetime.fromisoformat(m['timestamp']),
                metadata=m.get('metadata', {})
            )
            for m in data['messages']
        ]
        session.metadata = data.get('metadata', {})
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.last_activity = datetime.fromisoformat(data['last_activity'])
        return session
```

#### 1.2 新增 SessionManager 类
```python
# app/chat/session_manager.py

class SessionManager:
    """多会话管理器"""

    def __init__(self, storage_path: str = None):
        self.sessions: Dict[str, ChatSession] = {}
        self.current_session_id: Optional[str] = None
        self.storage_path = storage_path or 'data/sessions.json'
        self._load_sessions()

    def create_session(self, title: str = None) -> ChatSession:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id, title)
        self.sessions[session_id] = session
        self.current_session_id = session_id
        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """获取指定会话"""
        return self.sessions.get(session_id)

    def get_current_session(self) -> Optional[ChatSession]:
        """获取当前会话"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None

    def switch_session(self, session_id: str) -> bool:
        """切换当前会话"""
        if session_id in self.sessions:
            self.current_session_id = session_id
            self._save_sessions()
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.current_session_id == session_id:
                self.current_session_id = next(iter(self.sessions)) if self.sessions else None
            self._save_sessions()
            return True
        return False

    def update_session_title(self, session_id: str, title: str) -> bool:
        """更新会话标题"""
        if session_id in self.sessions:
            self.sessions[session_id].title = title
            self._save_sessions()
            return True
        return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        return [
            {
                'session_id': sid,
                'title': session.title,
                'preview': session.get_preview(),
                'created_at': session.created_at.isoformat(),
                'last_activity': session.last_activity.isoformat(),
                'message_count': session.get_message_count(),
                'is_current': sid == self.current_session_id
            }
            for sid, session in sorted(
                self.sessions.items(),
                key=lambda x: x[1].last_activity,
                reverse=True
            )
        ]

    def _load_sessions(self):
        """从文件加载会话"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_data in data.get('sessions', []):
                        session = ChatSession.from_dict(session_data)
                        self.sessions[session.session_id] = session
                    self.current_session_id = data.get('current_session_id')
            except Exception as e:
                logger.error(f"加载会话失败: {e}")

    def _save_sessions(self):
        """保存会话到文件"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            data = {
                'sessions': [s.to_dict() for s in self.sessions.values()],
                'current_session_id': self.current_session_id
            }
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话失败: {e}")
```

### 2. 前端 UI 设计

#### 2.1 布局结构
```html
<!-- 双栏布局 -->
<div class="app-container">
    <!-- 左侧会话列表 -->
    <aside class="sidebar">
        <div class="sidebar-header">
            <h2>会话</h2>
            <button id="newSessionBtn" class="btn-new">+ 新建</button>
        </div>
        <div id="sessionList" class="session-list">
            <!-- 会话列表项动态生成 -->
        </div>
    </aside>

    <!-- 右侧聊天区域 -->
    <main class="chat-area">
        <div class="chat-header">
            <div class="header-left">
                <button id="toggleSidebar" class="btn-toggle">☰</button>
                <h1 id="sessionTitle">Gravix AI Chat</h1>
            </div>
            <div class="header-right">
                <span id="connectionStatus" class="status disconnected">● 未连接</span>
            </div>
        </div>
        <div id="messagesContainer" class="messages-container"></div>
        <div class="input-container">
            <!-- 输入框保持不变 -->
        </div>
    </main>
</div>
```

#### 2.2 CSS 样式
```css
.app-container {
    display: flex;
    width: 100%;
    height: 100vh;
    overflow: hidden;
}

.sidebar {
    width: 280px;
    background: #f9fafb;
    border-right: 1px solid #e5e7eb;
    display: flex;
    flex-direction: column;
    transition: transform 0.3s ease;
}

.sidebar.collapsed {
    transform: translateX(-100%);
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.session-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

.session-item {
    padding: 12px 16px;
    margin-bottom: 4px;
    border-radius: 8px;
    cursor: pointer;
    transition: background 0.2s;
    position: relative;
}

.session-item:hover {
    background: #f3f4f6;
}

.session-item.active {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.session-item-title {
    font-weight: 500;
    margin-bottom: 4px;
}

.session-item-preview {
    font-size: 12px;
    opacity: 0.7;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.session-item-actions {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    opacity: 0;
    transition: opacity 0.2s;
}

.session-item:hover .session-item-actions {
    opacity: 1;
}

.chat-area {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-width: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .sidebar {
        position: absolute;
        z-index: 100;
        height: 100%;
        box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
    }

    .sidebar.collapsed {
        transform: translateX(-100%);
    }
}
```

#### 2.3 JavaScript 逻辑
```javascript
// 会话管理
class SessionManager {
    constructor() {
        this.currentSessionId = null;
        this.sessionList = [];
    }

    // 加载会话列表
    async loadSessions() {
        const response = await fetch('/api/sessions');
        this.sessionList = await response.json();
        this.renderSessionList();
    }

    // 创建新会话
    async createSession() {
        const response = await fetch('/api/sessions', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({title: '新会话'})
        });
        const session = await response.json();
        this.currentSessionId = session.session_id;
        await this.loadSessions();
        this.clearMessages();
    }

    // 切换会话
    async switchSession(sessionId) {
        const response = await fetch(`/api/sessions/${sessionId}`, {
            method: 'PATCH'
        });
        await this.loadSessions();
        await this.loadMessages(sessionId);
    }

    // 删除会话
    async deleteSession(sessionId) {
        await fetch(`/api/sessions/${sessionId}`, {
            method: 'DELETE'
        });
        await this.loadSessions();
    }

    // 渲染会话列表
    renderSessionList() {
        const container = document.getElementById('sessionList');
        container.innerHTML = this.sessionList.map(session => `
            <div class="session-item ${session.is_current ? 'active' : ''}"
                 data-session-id="${session.session_id}">
                <div class="session-item-title">${this.escapeHtml(session.title)}</div>
                <div class="session-item-preview">${this.escapeHtml(session.preview)}</div>
                <div class="session-item-actions">
                    <button class="btn-delete" data-action="delete">×</button>
                </div>
            </div>
        `).join('');

        // 绑定事件
        container.querySelectorAll('.session-item').forEach(item => {
            item.addEventListener('click', (e) => {
                if (!e.target.classList.contains('btn-delete')) {
                    this.switchSession(item.dataset.sessionId);
                }
            });
        });

        container.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const sessionId = btn.closest('.session-item').dataset.sessionId;
                this.deleteSession(sessionId);
            });
        });
    }
}
```

### 3. 后端 API 设计

#### 3.1 HTTP 端点
```python
# app/chat/http_server.py

async def handle_api_sessions(self, request: web.Request):
    """获取会话列表"""
    sessions = self.session_manager.list_sessions()
    return web.json_response(sessions)

async def handle_api_create_session(self, request: web.Request):
    """创建新会话"""
    data = await request.json()
    title = data.get('title')
    session = self.session_manager.create_session(title)
    return web.json_response(session.to_dict())

async def handle_api_get_session(self, request: web.Request):
    """获取会话详情"""
    session_id = request.match_info['session_id']
    session = self.session_manager.get_session(session_id)
    if session:
        return web.json_response(session.to_dict())
    return web.json_response({'error': 'Session not found'}, status=404)

async def handle_api_update_session(self, request: web.Request):
    """更新会话（切换/重命名）"""
    session_id = request.match_info['session_id']
    data = await request.json()

    if 'title' in data:
        self.session_manager.update_session_title(session_id, data['title'])
    else:
        self.session_manager.switch_session(session_id)

    session = self.session_manager.get_session(session_id)
    return web.json_response(session.to_dict())

async def handle_api_delete_session(self, request: web.Request):
    """删除会话"""
    session_id = request.match_info['session_id']
    self.session_manager.delete_session(session_id)
    return web.json_response({'success': True})
```

#### 3.2 WebSocket 消息扩展
```python
# 扩展消息类型
{
    'type': 'session_created',
    'session': {...}
}

{
    'type': 'session_switched',
    'session_id': 'xxx'
}

{
    'type': 'session_deleted',
    'session_id': 'xxx'
}

{
    'type': 'session_list_updated',
    'sessions': [...]
}
```

### 4. 集成到现有服务器

#### 4.1 修改 ChatHTTPServer
```python
class ChatHTTPServer:
    def __init__(self, ...):
        # 现有初始化代码
        ...

        # 添加会话管理器
        from app.chat.session_manager import SessionManager
        self.session_manager = SessionManager()

        # 确保至少有一个会话
        if not self.session_manager.sessions:
            self.session_manager.create_session("默认会话")

    async def handle_chat_message(self, client_id: str, ws, data: dict):
        """修改消息处理以使用会话管理器"""
        session = self.session_manager.get_current_session()
        if not session:
            session = self.session_manager.create_session()

        content = data.get('content', '')
        session.add_message('user', content)

        # 现有的响应生成逻辑
        ...
```

## 实施步骤

### 阶段 1：后端基础（2-3小时）
1. ✅ 扩展 `ChatSession` 类（添加 title、to_dict、from_dict）
2. ✅ 创建 `SessionManager` 类
3. ✅ 修改 `ChatHTTPServer` 集成会话管理器
4. ✅ 实现会话持久化（JSON文件）

### 阶段 2：API 实现（1-2小时）
1. ✅ 实现 HTTP API 端点
2. ✅ 扩展 WebSocket 消息类型
3. ✅ 添加会话管理命令

### 阶段 3：前端改造（2-3小时）
1. ✅ 重构 HTML 为双栏布局
2. ✅ 实现 CSS 样式（响应式）
3. ✅ 实现 JavaScript 会话管理逻辑
4. ✅ 添加会话切换交互

### 阶段 4：测试优化（1小时）
1. ✅ 功能测试（创建、切换、删除）
2. ✅ 性能优化（大量会话）
3. ✅ 用户体验优化（动画、反馈）

## 兼容性保证

1. **渐进式升级** - 现有单会话模式保持可用
2. **数据迁移** - 首次启动自动创建默认会话
3. **降级处理** - 如果会话管理失败，回退到内存模式
4. **API 版本** - 保留现有 WebSocket 消息格式

## 文件清单

### 新增文件
- `app/chat/session_manager.py` - 会话管理器
- `data/sessions.json` - 会话存储（自动生成）

### 修改文件
- `app/chat/session.py` - 扩展会话类
- `app/chat/http_server.py` - 集成会话管理
- `web/static/index.html` - UI 重构

## 估计时间
总计：6-9小时
- 阶段 1：2-3小时
- 阶段 2：1-2小时
- 阶段 3：2-3小时
- 阶段 4：1小时

## 风险与缓解

1. **数据丢失风险** - 实现自动保存和备份
2. **性能问题** - 懒加载消息，分页显示
3. **兼容性问题** - 充分测试现有功能
