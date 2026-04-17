# 会话切换错误修复

## 问题描述
切换会话时出现错误：
```
⚠️ Failed to switch session
2026-04-17 14:43:27.296 | ERROR | app.chat.http_server:handle_api_update_session:705 - Error updating session: Expecting value: line 1 column 1 (char 0)
```

## 根本原因
前端发送 PATCH 请求切换会话时，没有发送请求体（空 body），但后端代码尝试解析 JSON，导致解析失败。

## 修复方案

### 1. 后端修复 (`app/chat/http_server.py`)
在 `handle_api_update_session` 方法中添加 try-except 处理空请求体：

```python
async def handle_api_update_session(self, request: web.Request):
    try:
        session_id = request.match_info['session_id']

        # Try to parse JSON body (may be empty for switch requests)
        try:
            data = await request.json()
        except:
            data = {}

        # Update title if provided, otherwise switch session
        if 'title' in data:
            success = self.session_manager.update_session_title(session_id, data['title'])
        else:
            success = self.session_manager.switch_session(session_id)

        if success:
            session = self.session_manager.get_session(session_id)
            return web.json_response(session.to_dict())
        return web.json_response({'error': 'Operation failed'}, status=400)
    except Exception as e:
        logger.error(f"Error updating session: {e}")
        return web.json_response({'error': str(e)}, status=500)
```

### 2. 前端修复 (`web/static/index.html`)
在 `switchSession` 方法中添加空的 JSON 请求体：

```javascript
async switchSession(sessionId) {
    try {
        const response = await fetch(`/api/sessions/${sessionId}`, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({})  // 添加空 JSON 对象
        });
        // ... 其余代码
    }
}
```

## 测试步骤

1. **重启服务器**
   ```bash
   # 停止现有服务器
   pkill -f "python.*run_all.py"

   # 启动新服务器
   python3 run_all.py
   ```

2. **打开浏览器**
   访问：http://localhost:8765

3. **创建多个会话**
   - 点击 "+ 新建" 创建至少 2 个会话
   - 在不同会话中发送不同的消息

4. **测试会话切换**
   - 点击左侧列表中的不同会话
   - 确认能够成功切换
   - 确认消息历史正确加载

5. **验证控制台**
   - 打开浏览器开发者工具（F12）
   - 查看 Console 标签页
   - 确认没有错误信息

## 预期结果

✅ **正常行为**：
- 点击会话卡片立即切换
- 加载该会话的历史消息
- 更新会话标题
- 无错误提示

❌ **如果还有问题**：
- 检查浏览器控制台错误
- 检查服务器日志
- 确认网络连接正常

## 相关 API 端点

### 切换会话
```bash
curl -X PATCH http://localhost:8765/api/sessions/{session_id} \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 更新会话标题
```bash
curl -X PATCH http://localhost:8765/api/sessions/{session_id} \
  -H "Content-Type: application/json" \
  -d '{"title": "新标题"}'
```

## 修复状态
✅ **已修复** - 会话切换功能现在应该可以正常工作了

重启服务器并刷新浏览器页面以应用修复。
