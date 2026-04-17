# 数据库配置说明

## 概述

Gravix 支持多种数据库存储方式，默认使用 SQLite。可以通过环境变量配置切换到其他数据库。

## 配置方式

### 方法 1：环境变量

在 `.env` 文件中添加配置：

```bash
# 启用数据库存储（默认：true）
USE_DATABASE=true

# 数据库类型（sqlite/mysql，默认：sqlite）
DATABASE_TYPE=sqlite

# SQLite 配置
SQLITE_PATH=data/gravix.db
```

### 方法 2：MySQL 配置（未来支持）

```bash
# 启用数据库存储
USE_DATABASE=true

# 使用 MySQL
DATABASE_TYPE=mysql

# MySQL 连接配置
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=gravix
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=gravix
```

## 数据库类型对比

### SQLite (默认)
- ✅ 无需额外服务
- ✅ 零配置
- ✅ 适合单机部署
- ✅ 数据库文件：`data/gravix.db`
- ⚠️ 不支持并发写入
- ⚠️ 不适合高并发场景

### MySQL (计划中)
- ✅ 支持高并发
- ✅ 支持分布式部署
- ✅ 事务支持完善
- ⚠️ 需要单独的 MySQL 服务
- ⚠️ 需要额外配置

## 数据迁移

### 从 JSON 迁移到数据库

如果您之前使用 JSON 文件存储（`data/sessions.json`），系统会自动迁移：

1. 首次启动时检测到 JSON 文件
2. 自动迁移所有会话到数据库
3. 创建 JSON 文件备份：`data/sessions.json.backup`
4. 后续使用数据库存储

### 手动迁移

```python
from app.database import DatabaseAdapterFactory
from app.database.migration import DataMigration

# 创建数据库连接
db = DatabaseAdapterFactory.create_from_env({'type': 'sqlite', 'path': 'data/gravix.db'})
db.connect()
db.initialize_schema()

# 执行迁移
migration = DataMigration('data/sessions.json')
migration.migrate_to_database(db)
```

## 数据库 Schema

### sessions 表
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    metadata TEXT,              -- JSON 格式的元数据
    created_at TIMESTAMP,
    last_activity TIMESTAMP
);
```

### messages 表
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,         -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    metadata TEXT,              -- JSON 格式的元数据
    timestamp TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
);
```

### 索引
```sql
CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_sessions_last_activity ON sessions(last_activity DESC);
CREATE INDEX idx_messages_timestamp ON messages(timestamp DESC);
```

## 数据库文件位置

### SQLite
- 默认路径：`data/gravix.db`
- 可通过 `SQLITE_PATH` 环境变量配置

### 备份
SQLite 数据库备份：
```bash
# 备份
cp data/gravix.db data/gravix.db.backup

# 恢复
cp data/gravix.db.backup data/gravix.db
```

## 性能优化

### SQLite 优化
- 已添加索引加速查询
- 使用事务批量操作
- 支持预编译语句（未来）

### 推荐配置
```bash
# SQLite WAL 模式（未来支持）
SQLITE_JOURNAL_MODE=WAL

# 同步设置（未来支持）
SQLITE_SYNCHRONOUS=NORMAL
```

## 故障排查

### 问题：数据库锁定
**解决**：SQLite 不支持多进程同时写入
- 确保只有一个 Gravix 实例在运行
- 或切换到 MySQL

### 问题：迁移失败
**解决**：
1. 检查 JSON 文件格式是否正确
2. 查看日志中的错误信息
3. 手动备份 JSON 文件后重试

### 问题：查询缓慢
**解决**：
1. 检查索引是否创建
2. 使用 `/sessions_list` 查看会话数量
3. 考虑归档旧会话

## 切换数据库

### SQLite → MySQL

1. 导出 SQLite 数据：
```bash
sqlite3 data/gravix.db .dump > backup.sql
```

2. 创建 MySQL 数据库：
```sql
CREATE DATABASE gravix;
```

3. 导入数据（需要调整 SQL 语法）：
```bash
mysql -u root -p gravix < backup.sql
```

4. 更新配置：
```bash
DATABASE_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=gravix
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=gravix
```

5. 重启服务

### MySQL → SQLite

使用数据库导出工具（如 mysqldump）导出数据，然后导入 SQLite。

## 数据库维护

### 定期备份
```bash
# 每日备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
cp data/gravix.db "backups/gravix_$DATE.db"
```

### 清理旧会话
```python
# 删除 30 天前的会话
from app.database import DatabaseAdapterFactory

db = DatabaseAdapterFactory.create_from_env()
db.connect()

# 查询旧会话
sessions = db.execute_raw("""
    SELECT session_id FROM sessions
    WHERE last_activity < datetime('now', '-30 days')
""")

# 删除旧会话
for session in sessions:
    db.delete_session(session['session_id'])
```

## 监控和统计

### 查看数据库大小
```bash
# SQLite
ls -lh data/gravix.db

# 查看表统计
sqlite3 data/gravix.db "SELECT COUNT(*) FROM sessions;"
sqlite3 data/gravix.db "SELECT COUNT(*) FROM messages;"
```

### 性能监控
```python
# 查询慢日志
db.execute_raw("""
    SELECT * FROM messages
    WHERE session_id = ?
    ORDER BY timestamp ASC
    LIMIT 100
""", (session_id,))
```

## 最佳实践

1. **开发环境**：使用 SQLite（简单快速）
2. **生产环境**：使用 MySQL（高可用）
3. **定期备份**：设置自动备份任务
4. **监控性能**：关注查询响应时间
5. **数据归档**：定期归档旧会话数据

## 未来增强

- [ ] MySQL 适配器实现
- [ ] PostgreSQL 适配器
- [ ] Redis 缓存层
- [ ] 数据库连接池
- [ ] 读写分离
- [ ] 数据库分片
- [ ] 自动备份策略
- [ ] 性能监控面板
