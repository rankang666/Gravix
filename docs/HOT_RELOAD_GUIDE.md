# 热加载（Hot Reload）使用指南

## 🔄 功能介绍

热加载功能让服务器在代码修改时自动重新加载，无需手动重启服务器。

### 主要特性

✅ **自动监控** - 监控项目中的 Python 文件变化  
✅ **智能重载** - 只在必要时重新加载，避免频繁重启  
✅ **保持连接** - 尽量保持现有客户端连接  
✅ **实时通知** - 告知客户端服务器已重载  
✅ **开发友好** - 提升开发效率  

## 🚀 快速开始

### 启用热加载

#### 方法 1: 环境变量（推荐）

```bash
# 启动服务时启用热加载
ENABLE_HOT_RELOAD=true python3 run_all.py
```

#### 方法 2: .env 文件配置

```bash
# 在 .env 文件中添加
ENABLE_HOT_RELOAD=true
```

然后正常启动：
```bash
python3 run_all.py
```

### 验证热加载是否启用

启动日志显示：
```
♻️  Hot reload ENABLED - Server will auto-reload on code changes
📁 Monitoring: /path/to/Gravix
✅ Hot reload manager started
```

## 📝 工作流程

### 正常开发流程

#### 1. 启动服务器（启用热加载）
```bash
ENABLE_HOT_RELOAD=true python3 run_all.py
```

#### 2. 修改代码
```python
# 修改任何 Python 文件
# app/chat/server.py
# app/llm/service.py
# system_prompt.txt
# 等等...
```

#### 3. 自动重载
```
服务器日志显示：
📝 Code change detected: app/chat/server.py
♻️  Reloading server...
✅ Reload complete
```

#### 4. 客户端通知
浏览器中显示：
```
♻️  Server reloaded (change: server.py)
```

#### 5. 继续开发
- 刷新浏览器页面（如果需要）
- 测试新功能
- 无需重启服务器！

## 📂 监控范围

### 监控的文件类型

✅ **Python 源代码** - `.py` 文件  
✅ **系统提示词** - `system_prompt.txt`  
✅ **配置文件** - 部分配置修改  

### 忽略的目录

❌ `__pycache__` - Python 缓存  
❌ `.git` - Git 仓库  
❌ `.pytest_cache` - 测试缓存  
❌ `node_modules` - Node.js 依赖  
❌ `.venv`, `venv` - 虚拟环境  
❌ `Html` - 静态文件目录（避免 HTML 变化触发重载）  

### 忽略的文件类型

❌ `.pyc`, `.pyo`, `.pyd` - 编译的 Python 文件  
❌ `.so` - 共享库  
❌ `.log` - 日志文件  
❌ `.db`, `.sqlite` - 数据库文件  

## 🎯 使用场景

### 适用场景

✅ **修改系统提示词**
```bash
# 1. 编辑 system_prompt.txt
vim system_prompt.txt

# 2. 保存后自动重载
# 服务器日志：♻️  Reloading server...

# 3. 刷新浏览器测试新提示词
```

✅ **修改业务逻辑**
```bash
# 1. 修改 Python 代码
vim app/chat/server.py

# 2. 保存后自动重载
# 3. 继续开发，无需重启
```

✅ **调整配置**
```bash
# 1. 修改配置
vim app/llm/service.py

# 2. 自动重载生效
# 3. 测试新配置
```

✅ **调试和测试**
```bash
# 快速迭代开发
# 修改代码 → 自动重载 → 测试 → 修改代码
```

### 不适用场景

❌ **生产环境** - 应该关闭热加载  
❌ **大规模重构** - 建议完全重启  
❌ **依赖变更** - 新增包需要重启  
❌ **HTML/CSS/JS 修改** - 前端文件变化不触发重载  

## ⚙️ 配置选项

### 环境变量

| 变量 | 值 | 说明 |
|-----|-----|------|
| `ENABLE_HOT_RELOAD` | `true` / `false` | 启用/禁用热加载 |

### 高级配置

如需自定义监控目录或文件类型，可以修改 `app/utils/reloader.py`：

```python
# 修改监控目录
watch_paths = [
    Path('app'),
    Path('skills'),
    Path('system_prompt.txt')
]

# 修改忽略目录
ignored_dirs = {
    '__pycache__',
    '.git',
    'Html'  # 添加要忽略的目录
}
```

## 🛠️ 故障排查

### 热加载不工作

#### 问题 1: 修改代码后没有重载

**检查：**
```bash
# 确认热加载已启用
ps aux | grep run_all.py | grep ENABLE_HOT_RELOAD

# 或查看启动日志
python3 run_all.py | grep "Hot reload"
```

**解决：**
```bash
# 确保设置环境变量
export ENABLE_HOT_RELOAD=true
python3 run_all.py
```

#### 问题 2: 频繁重载

**原因：** 文件系统监控触发多次

**解决：** 已有 1 秒冷却时间，如仍有问题：
```python
# 在 app/utils/reloader.py 中调整
self.reload_cooldown = 2.0  # 增加到 2 秒
```

#### 问题 3: 重载后功能异常

**原因：** 某些状态在重载时丢失

**解决：**
```bash
# 完全重启服务器
# 停止当前服务
# 重新启动
python3 run_all.py
```

### 性能影响

#### 内存使用

热加载会略微增加内存使用（约 10-20MB），对开发环境影响很小。

#### CPU 使用

文件监控的 CPU 使用极低，几乎可以忽略。

#### 建议

- ✅ 开发环境：启用热加载
- ❌ 生产环境：禁用热加载

## 📊 日志输出示例

### 启用时
```
============================================================
Starting Gravix Services
============================================================
♻️  Hot reload ENABLED - Server will auto-reload on code changes
📁 Monitoring: /path/to/Gravix
✅ Hot reload manager started
```

### 检测到代码变化
```
📝 Code change detected: app/chat/server.py
♻️  Reloading server...
📝 Code changed: app/chat/server.py
♻️  Reloading server configuration...
✅ System prompt reloaded from file
✅ Reload complete
```

### 客户端通知
```
[系统] ♻️  Server reloaded (change: server.py)
```

## 🎓 最佳实践

### 开发工作流

1. **启用热加载**
   ```bash
   ENABLE_HOT_RELOAD=true python3 run_all.py
   ```

2. **修改代码**
   - 编辑 Python 文件
   - 保存文件

3. **自动重载**
   - 服务器自动检测变化
   - 重新加载配置
   - 通知客户端

4. **测试变更**
   - 刷新浏览器（如需要）
   - 测试新功能
   - 继续开发

### 生产部署

```bash
# 确保热加载已禁用
unset ENABLE_HOT_RELOAD
# 或
echo "ENABLE_HOT_RELOAD=false" >> .env

# 启动服务
python3 run_all.py
```

### 与 Git 配合

```bash
# 开发循环
vim app/chat/server.py      # 编辑代码
git add app/chat/server.py   # 添加到 Git
git commit -m "Fix bug"       # 提交
# 服务器自动重载，无需手动重启
```

## 🔧 高级用法

### 手动触发重载

如果需要手动触发重载（不依赖文件监控）：

```python
# 在代码中
await chat_server.reload_server()
```

### 自定义重载行为

```python
# 修改 app/chat/http_server.py
async def _handle_code_change(self, changed_file: Path):
    # 添加自定义逻辑
    if 'system_prompt.txt' in str(changed_file):
        await self._reload_system_prompt()
    
    # 自定义处理
    if 'skills/' in str(changed_file):
        await self._reload_skills()
```

## 💡 提示

### 提高开发效率

- ✅ 修改代码后立即看到效果
- ✅ 无需频繁重启服务器
- ✅ 保持开发流程连贯性
- ✅ 快速迭代和调试

### 注意事项

- ⚠️  某些修改可能需要完全重启（如新增依赖）
- ⚠️  生产环境必须禁用热加载
- ⚠️  热加载只监控开发环境
- ⚠️  避免在热加载启用时进行大规模重构

## 🎉 总结

热加载功能让开发更高效：
- 📝 修改代码自动重载
- 🔄 保持开发流程
- ⚡ 提升开发效率
- 🎯 专注业务逻辑

立即启用热加载，享受无缝的开发体验！🚀
