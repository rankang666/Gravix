# 热加载快速开始

## 🚀 3秒启用热加载

### 安装依赖

```bash
pip install watchdog==3.0.0
```

### 启用并启动

```bash
ENABLE_HOT_RELOAD=true python3 run_all.py
```

### 验证

启动日志显示：
```
♻️  Hot reload ENABLED - Server will auto-reload on code changes
✅ Hot reload manager started
```

### 测试

1. 修改任何 `.py` 文件
2. 保存文件
3. 查看日志：
   ```
   📝 Code change detected: app/chat/server.py
   ♻️  Reloading server...
   ✅ Reload complete
   ```

## ✅ 完成！

现在修改代码后会自动重载，无需手动重启服务器！

### 禁用热加载

```bash
# 不设置环境变量即可
python3 run_all.py
```

### 生产环境

```bash
# 确保禁用
ENABLE_HOT_RELOAD=false python3 run_all.py
```

## 💡 主要优势

- ⚡ **快速迭代** - 修改代码立即生效
- 🔄 **无缝体验** - 保持开发流程
- 🎯 **专注开发** - 无需频繁重启
- 📝 **自动通知** - 客户端知道服务器已重载

详细指南：`docs/HOT_RELOAD_GUIDE.md`
