# Gravix 部署指南 (开发模式)

## 🚀 快速部署

### 日常代码更新 (推荐)

修改代码后使用 `deploy.sh`，**只需几秒钟**：

```bash
./deploy.sh
```

**优势**：
- ✅ 代码目录已挂载到容器
- ✅ 修改代码后只需重启，无需重新构建
- ✅ 秒级部署完成

### Dockerfile 或依赖更新

只有修改了以下文件时才需要使用 `rebuild.sh`：
- `Dockerfile`
- `requirements.txt`

```bash
./rebuild.sh
```

**注意**：完整重建可能需要几分钟。

## 📦 开发模式配置

当前 `docker-compose.yml` 已配置以下目录挂载：

```yaml
volumes:
  - ./.env:/app/.env              # 环境变量
  - ./logs:/app/logs              # 日志目录
  - ./web/static:/app/web/static  # 前端静态文件
  - ./app:/app/app                # ✅ 应用代码
  - ./skills:/app/skills          # ✅ Skills 代码
  - ./run_all.py:/app/run_all.py  # ✅ 启动脚本
  - ./requirements.txt:/app/requirements.txt
```

## 💡 使用场景

### 场景 1：修改业务代码

修改了 `app/` 或 `skills/` 目录下的代码：

```bash
./deploy.sh
```

### 场景 2：添加 Python 依赖

```bash
# 1. 编辑 requirements.txt 添加依赖
vim requirements.txt

# 2. 完整重建
./rebuild.sh
```

### 场景 3：修改配置文件

修改了 `.env`、`docker-compose.yml` 等：

```bash
./deploy.sh
```

### 场景 4：实时查看代码修改效果

由于代码已挂载，可以直接在容器内重启进程：

```bash
docker-compose exec gravix python run_all.py
```

或者：
```bash
docker-compose restart gravix
```

## 🔧 常用命令

### 查看日志
```bash
docker-compose logs -f gravix
```

### 进入容器
```bash
docker-compose exec gravix sh
```

### 在容器内安装 Python 包
```bash
docker-compose exec gravix pip install package-name
```

### 手动重启
```bash
docker-compose restart
```

### 完全停止
```bash
docker-compose down
```

## ⚠️ 注意事项

1. **生产环境**：生产环境应该移除代码挂载，使用 `rebuild.sh` 部署
2. **首次部署**：首次部署需要使用 `./rebuild.sh` 构建镜像
3. **依赖更新**：修改 `requirements.txt` 后必须使用 `./rebuild.sh`

## 🎯 工作流程建议

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 检查改了什么
git diff HEAD@{1} HEAD --name-only

# 3. 如果改了 Dockerfile 或 requirements.txt
./rebuild.sh

# 4. 否则
./deploy.sh
```

## 📊 部署速度对比

| 操作 | 开发模式 | 生产模式 |
|------|----------|----------|
| 代码修改 | ~5秒 | ~5分钟 |
| 配置修改 | ~5秒 | ~1分钟 |
| 依赖更新 | ~3分钟 | ~3分钟 |
| Dockerfile 修改 | ~3分钟 | ~3分钟 |
