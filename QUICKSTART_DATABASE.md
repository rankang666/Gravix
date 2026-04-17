# 数据库存储功能 - 快速启动

## 🚀 立即开始

### 1. 更新 .env 配置

```bash
# 启用数据库存储（默认已启用）
USE_DATABASE=true

# 使用 SQLite（默认）
DATABASE_TYPE=sqlite
SQLITE_PATH=data/gravix.db
```

### 2. 重启服务器

```bash
# 停止现有服务器
pkill -f "python.*run_all.py"

# 启动服务器
python3 run_all.py
```

### 3. 自动迁移

如果之前使用 JSON 文件存储，首次启动时会自动：
- ✅ 检测 `data/sessions.json`
- ✅ 迁移所有会话到数据库
- ✅ 创建 JSON 文件备份
- ✅ 使用数据库存储

## ✨ 功能特性

### 已实现
- ✅ SQLite 数据库支持
- ✅ 会话和消息持久化
- ✅ 自动从 JSON 迁移
- ✅ 高效索引查询
- ✅ 事务支持
- ✅ 数据库抽象层

### 计划中
- 🔄 MySQL 适配器
- 🔄 PostgreSQL 适配器
- 🔄 数据库连接池
- 🔄 读写分离

## 📊 数据库 Schema

```
gravix.db
├── sessions (会话表)
│   ├── session_id (主键)
│   ├── title (标题)
│   ├── metadata (元数据 JSON)
│   ├── created_at (创建时间)
│   └── last_activity (最后活动时间)
│
└── messages (消息表)
    ├── id (自增主键)
    ├── session_id (外键 → sessions)
    ├── role (角色: user/assistant/system)
    ├── content (消息内容)
    ├── metadata (元数据 JSON)
    └── timestamp (时间戳)
```

## 🔄 数据迁移

### 自动迁移

```bash
# 首次启动时自动执行
python3 run_all.py

# 日志输出
🔄 Starting automatic migration from JSON to database...
✅ Successfully migrated 5/5 sessions
✅ JSON file backed up to: data/sessions.json.backup
✅ Migration completed successfully
```

### 手动迁移

```python
from app.database import DatabaseAdapterFactory
from app.database.migration import DataMigration

# 创建数据库
db = DatabaseAdapterFactory.create_from_env({
    'type': 'sqlite',
    'path': 'data/gravix.db'
})
db.connect()
db.initialize_schema()

# 执行迁移
migration = DataMigration('data/sessions.json')
success = migration.migrate_to_database(db)
```

## 💾 备份和恢复

### 备份数据库

```bash
# 备份 SQLite 数据库
cp data/gravix.db data/gravix.db.backup.$(date +%Y%m%d)

# 或使用 SQLite 导出
sqlite3 data/gravix.db .dump > backup.sql
```

### 恢复数据库

```bash
# 从备份恢复
cp data/gravix.db.backup data/gravix.db

# 从 SQL 导入
sqlite3 data/gravix.db < backup.sql
```

## 🗑️ 清理数据

### 删除旧会话

```bash
# 使用 SQLite 命令
sqlite3 data/gravix.db "DELETE FROM sessions WHERE last_activity < datetime('now', '-30 days');"
```

### 重置数据库

```bash
# 删除数据库文件（会丢失所有数据！）
rm data/gravix.db

# 重启服务器会自动创建新数据库
python3 run_all.py
```

## 🔍 查询数据

### 使用 SQLite 命令行

```bash
# 查看所有会话
sqlite3 data/gravix.db "SELECT session_id, title, created_at FROM sessions;"

# 查看消息数量
sqlite3 data/gravix.db "SELECT COUNT(*) FROM messages;"

# 查看最近活动
sqlite3 data/gravix.db "
SELECT title, last_activity 
FROM sessions 
ORDER BY last_activity DESC 
LIMIT 5;
"
```

### Python 脚本查询

```python
from app.database import DatabaseAdapterFactory

# 创建连接
db = DatabaseAdapterFactory.create_from_env({
    'type': 'sqlite',
    'path': 'data/gravix.db'
})
db.connect()

# 查询会话
sessions = db.list_sessions()
for session in sessions:
    print(f"{session['title']}: {session['message_count']} messages")

# 搜索会话
results = db.search_sessions('python')
print(f"Found {len(results)} sessions containing 'python'")
```

## 📈 性能优化

### 索引优化

数据库已自动创建以下索引：
- `idx_messages_session_id` - 加速按会话查询消息
- `idx_sessions_last_activity` - 加速按时间排序会话
- `idx_messages_timestamp` - 加速按时间查询消息

### 查询优化

```python
# ✅ 好的做法：使用限制
messages = db.get_messages(session_id, limit=10)

# ❌ 不好的做法：加载所有消息
messages = db.get_messages(session_id)
```

## 🐛 故障排查

### 问题：数据库锁定

```bash
# 检查是否有多个实例运行
ps aux | grep "python.*run_all.py"

# 停止所有实例
pkill -f "python.*run_all.py"

# 重新启动
python3 run_all.py
```

### 问题：迁移失败

```bash
# 检查 JSON 文件
cat data/sessions.json | python -m json.tool

# 查看日志
python3 run_all.py | grep -i migration

# 手动备份 JSON
cp data/sessions.json data/sessions.json.manual_backup
```

### 问题：查询缓慢

```python
# 检查会话数量
sessions = db.list_sessions()
print(f"Total sessions: {len(sessions)}")

# 考虑归档旧数据
# 删除 30 天前的会话
db.execute_raw("""
    DELETE FROM sessions 
    WHERE last_activity < datetime('now', '-30 days')
""")
```

## 🎯 下一步

1. **测试功能**
   - 创建多个会话
   - 发送消息
   - 重启服务器验证数据持久化

2. **性能监控**
   - 观察数据库文件大小
   - 测试查询响应时间
   - 监控并发性能

3. **数据维护**
   - 设置定期备份
   - 定期清理旧数据
   - 监控数据库增长

## 📚 相关文档

- `DATABASE_CONFIG_EXAMPLES.md` - 详细配置说明
- `app/database/` - 数据库实现代码
- `app/database/schema.py` - 数据库结构

## 🎉 完成设置

您的数据库存储已配置完成！

现在所有会话和消息都存储在 `data/gravix.db` 中，享受：
- ✅ 更快的查询速度
- ✅ 更好的数据完整性
- ✅ 更容易的备份恢复
- ✅ 支持未来扩展到 MySQL

立即重启服务器体验：
```bash
python3 run_all.py
```
