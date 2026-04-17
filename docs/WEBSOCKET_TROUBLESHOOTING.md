# WebSocket 连接故障排查

## 问题：❌ Disconnected - Reconnecting...

### 症状
- 浏览器显示 "❌ Disconnected - Reconnecting..."
- 无法发送消息
- AI 没有响应

### 原因分析

WebSocket 服务端点配置错误。之前使用的是 `ws://localhost:8765`，现在应该是 `ws://localhost:8765/ws`。

### 解决方案

#### 1. 确认服务器正在运行

```bash
# 检查端口占用
lsof -i :8765

# 应该看到 python3 进程在监听
# python3.1  PID  USER   FD   TYPE  DEVICE SIZE/OFF NODE NAME
# python3.1  70821 jerry    7u  IPv4  ...  TCP *:ultraseek-http (LISTEN)
```

#### 2. 重启服务器

```bash
# 停止现有服务器（如果需要）
# 找到进程 ID (PID) 并杀掉
kill -9 70821

# 重新启动
python3 run_all.py
```

#### 3. 测试连接

```bash
# 运行连接测试
python3 test_websocket_connection.py

# 应该看到：
# ✅ Connected to ws://localhost:8765/ws
# ✅ WebSocket connection test completed!
```

#### 4. 检查浏览器控制台

1. 打开浏览器
2. 按 F12 打开开发者工具
3. 查看 Console 标签
4. 查看 Network 标签 → WS (WebSocket)

### 已修复的问题

#### ✅ 修复 1: 统一 HTTP 和 WebSocket

之前 HTTP 和 WebSocket 是分开的服务，现在统一在同一个 aiohttp 应用中：

```python
# HTTP: http://localhost:8765
# WebSocket: ws://localhost:8765/ws
```

#### ✅ 修复 2: 使用 aiohttp WebSocket

从 websockets 库切换到 aiohttp 内置的 WebSocket 支持：

```python
# 之前（有问题）
import websockets
async with websockets.serve(...)  # 独立服务

# 现在（修复后）
from aiohttp import web
app.router.add_get('/ws', self.handle_websocket)  # 统一路由
```

#### ✅ 修复 3: 更新前端连接地址

```javascript
// 之前（错误）
const wsUrl = 'ws://localhost:8765';

// 现在（正确）
const wsUrl = 'ws://localhost:8765/ws';
```

### 验证修复

#### 方法 1: 浏览器测试

1. 启动服务器：
   ```bash
   python3 run_all.py
   ```

2. 打开浏览器：
   ```
   http://localhost:8765
   ```

3. 应该看到：
   ```
   ✅ Connected
   👋 Welcome to Gravix AI Chat!
   ```

#### 方法 2: 命令行测试

```bash
python3 test_websocket_connection.py
```

预期输出：
```
✅ Connected to ws://localhost:8765/ws
📩 Server message: ✅ Connected to Gravix AI Chat Server
📤 Sending test message: /help
💭 🤔 正在分析您的问题...
🤖 AI Response: **Available Commands:**...
✅ WebSocket connection test completed!
```

### 常见问题

#### Q1: 仍然显示 "Disconnected"

**检查：**
1. 服务器是否在运行？
   ```bash
   lsof -i :8765
   ```

2. 防火墙是否阻止连接？
   ```bash
   # 临时关闭防火墙测试
   sudo ufw disable
   ```

3. 浏览器控制台是否有错误？
   - F12 → Console
   - F12 → Network → WS

#### Q2: 连接后立即断开

**原因：** 可能是前端代码缓存

**解决：**
1. 硬刷新页面：Ctrl+Shift+R (Windows/Linux) 或 Cmd+Shift+R (Mac)
2. 清除浏览器缓存
3. 检查前端代码中的 WebSocket URL

#### Q3: 服务器启动失败

**检查：**
```bash
# 查看完整启动日志
python3 run_all.py

# 检查端口是否被占用
lsof -i :8765

# 如果被占用，停止旧进程
kill -9 <PID>
```

### 下一步

如果问题仍然存在：

1. **查看日志**
   ```bash
   python3 run_all.py
   # 观察启动日志和错误信息
   ```

2. **测试连接**
   ```bash
   python3 test_websocket_connection.py
   ```

3. **检查配置**
   ```bash
   # 确认 .env 配置正确
   cat .env | grep LLM
   ```

4. **重置环境**
   ```bash
   # 停止所有 Python 进程
   pkill -f python3

   # 重新启动
   python3 run_all.py
   ```

### 成功的标志

当一切正常时，您应该看到：

**服务器端：**
```
============================================================
🚀 Gravix Services Ready!
============================================================
🌐 Web UI: http://localhost:8765
🔌 WebSocket: ws://localhost:8765/ws
🤖 LLM Provider: openai
📦 LLM Model: Qwen3-32B

💡 Open your browser and visit: http://localhost:8765
============================================================
```

**浏览器端：**
```
✅ Connected
👋 Welcome to Gravix AI Chat! Type /help to see available commands.
```

现在 WebSocket 连接应该可以正常工作了！🎉
