# Gravix HTTP 服务访问指南

## 🌐 通过端口访问 Gravix

现在您可以直接在浏览器中通过端口访问 Gravix 聊天界面！

### 启动服务

```bash
python3 run_all.py
```

### 访问地址

启动成功后，在浏览器中访问：

```
http://localhost:8765
```

或从局域网其他设备访问：

```
http://your-ip-address:8765
```

## 🚀 访问方式对比

### 之前（文件协议）
```
file:///path/to/Gravix/web/static/index.html
```
- ❌ 需要手动打开文件
- ❌ 部分浏览器限制文件协议
- ❌ 无法远程访问
- ❌ WebSocket 连接可能有问题

### 现在（HTTP 协议）
```
http://localhost:8765
```
- ✅ 浏览器直接输入地址
- ✅ 支持远程访问
- ✅ WebSocket 连接稳定
- ✅ 更好的用户体验

## 🔧 配置说明

### 修改端口

编辑 `run_all.py`：

```python
chat_server = ChatHTTPServer(
    host="0.0.0.0",  # 0.0.0.0 允许所有IP访问，localhost 只允许本机
    port=8765,       # 修改为其他端口，如 8080
    ...
)
```

### 仅本机访问

如果只想在本机访问，修改 `host` 参数：

```python
chat_server = ChatHTTPServer(
    host="127.0.0.1",  # 只允许本机访问
    port=8765,
    ...
)
```

### 局域网访问

默认配置允许局域网访问：

```python
chat_server = ChatHTTPServer(
    host="0.0.0.0",  # 允许所有IP访问
    port=8765,
    ...
)
```

查看本机 IP 地址：

```bash
# Linux/Mac
ifconfig | grep inet

# Windows
ipconfig
```

然后从其他设备访问：`http://your-ip:8765`

## 📱 使用场景

### 1. 本地开发
```
http://localhost:8765
```

### 2. 局域网演示
```
http://192.168.1.100:8765
```

### 3. 内网部署
```
http://192.168.2.85:8765
```

## 🔒 安全建议

### 生产环境部署

如果需要公网访问，建议：

1. **使用反向代理**（Nginx）
2. **启用 HTTPS**
3. **添加认证机制**
4. **配置防火墙规则**

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 🛠️ 故障排查

### 无法访问服务

1. **检查端口是否被占用**
   ```bash
   # 查看端口占用
   lsof -i :8765
   
   # 或
   netstat -an | grep 8765
   ```

2. **检查防火墙设置**
   ```bash
   # Linux 开放端口
   sudo ufw allow 8765
   
   # 或临时关闭防火墙测试
   sudo ufw disable
   ```

3. **查看服务日志**
   ```bash
   python3 run_all.py
   # 查看是否有错误信息
   ```

### WebSocket 连接失败

1. **检查 WebSocket URL**
   ```javascript
   // 确保使用正确的协议
   ws://localhost:8765  // HTTP 用 ws
   wss://localhost:8765 // HTTPS 用 wss
   ```

2. **浏览器控制台查看错误**
   - F12 打开开发者工具
   - 查看 Console 标签
   - 查看 Network 标签

## 📊 启动日志示例

```bash
$ python3 run_all.py

============================================================
Starting Gravix Services
============================================================
✅ Loaded environment variables from .env
✅ LLM service initialized
✅ Chat server running on http://0.0.0.0:8765
✅ WebSocket server running on ws://0.0.0.0:8765

============================================================
🚀 Gravix Services Ready!
============================================================
🌐 Web UI: http://localhost:8765
🔌 WebSocket: ws://localhost:8765
🤖 LLM Provider: openai
📦 LLM Model: Qwen3-32B

💡 Open your browser and visit: http://localhost:8765
============================================================
```

## 🎉 现在开始使用

1. **启动服务**
   ```bash
   python3 run_all.py
   ```

2. **打开浏览器**
   访问 `http://localhost:8765`

3. **开始聊天**
   在输入框中输入您的问题，开始与 AI 对话！

享受全新的 Gravix 聊天体验！🎊
