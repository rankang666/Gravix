# Docker 部署指南

本文档说明如何使用Docker部署Gravix项目。

## 🚀 快速开始

### 1. 准备环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
nano .env  # 编辑配置
```

**必需配置：**

```bash
# LLM配置（至少配置一个）
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxx
# 或
OPENAI_API_KEY=sk-xxx

# DataWorks配置（可选）
ALIBABA_CLOUD_ACCESS_KEY_ID=your_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret
ALIBABA_CLOUD_REGION_ID=cn-hangzhou
```

### 2. 启动服务

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查状态
docker-compose ps
```

### 3. 访问应用

- **Web UI**: 在浏览器中打开 `web/static/index.html`
- **WebSocket**: ws://localhost:8765
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 📦 构建镜像

### 使用docker-compose（推荐）

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d
```

### 使用docker命令

```bash
# 构建镜像
docker build -t gravix:latest .

# 运行容器
docker run -d \
  --name gravix \
  -p 8765:8765 \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  gravix:latest
```

## 🔧 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f gravix

# 查看实时日志
docker-compose logs -f --tail=100 gravix
```

### 进入容器

```bash
# 进入运行中的容器
docker-compose exec gravix bash

# 或使用docker命令
docker exec -it gravix-app bash
```

### 更新服务

```bash
# 停止并删除旧容器
docker-compose down

# 重新构建镜像
docker-compose build --no-cache

# 启动新容器
docker-compose up -d
```

### 清理资源

```bash
# 停止并删除容器、网络
docker-compose down

# 删除容器、网络、卷
docker-compose down -v

# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune
```

## 🌐 生产环境部署

### 1. 使用多阶段构建优化

创建 `Dockerfile.prod`：

```dockerfile
# Builder stage
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.9-slim

WORKDIR /app
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /root/.local /root/.local
COPY . .

ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8765 8000

CMD ["python", "run_all.py"]
```

### 2. 使用docker-compose.prod.yml

```yaml
version: '3.8'

services:
  gravix:
    build:
      context: .
      dockerfile: Dockerfile.prod
    container_name: gravix-prod
    restart: always
    ports:
      - "8765:8765"
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 3. 启动生产环境

```bash
# 使用生产配置
docker-compose -f docker-compose.prod.yml up -d

# 查看资源使用
docker stats gravix-prod
```

## 🔍 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs gravix

# 检查容器状态
docker-compose ps -a

# 检查健康状态
docker inspect --format='{{.State.Health.Status}}' gravix-app
```

### 端口冲突

如果端口已被占用：

```bash
# 查看端口占用
lsof -i :8765
lsof -i :8000

# 修改docker-compose.yml中的端口映射
ports:
  - "8766:8765"  # 使用不同端口
  - "8001:8000"
```

### 环境变量未生效

```bash
# 检查环境变量
docker-compose exec gravix env | grep -E "LLM|API"

# 确认.env文件存在且格式正确
cat .env

# 重新加载环境变量
docker-compose down
docker-compose up -d
```

### MCP服务器无法启动

```bash
# 检查Node.js和npm
docker-compose exec gravix node --version
docker-compose exec gravix npm --version

# 手动测试MCP服务器
docker-compose exec gravix npx -y alibabacloud-dataworks-mcp-server
```

### 性能问题

```bash
# 查看资源使用
docker stats gravix-app

# 查看容器进程
docker-compose exec gravix ps aux

# 增加资源限制
# 在docker-compose.yml中添加：
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

## 📊 监控和日志

### 查看日志

```bash
# 实时日志
docker-compose logs -f gravix

# 最近100行日志
docker-compose logs --tail=100 gravix

# 持久化日志
docker-compose logs -f gravix > logs/gravix.log
```

### 健康检查

```bash
# 手动健康检查
curl http://localhost:8000/health

# 查看健康状态
docker inspect --format='{{json .State.Health}}' gravix-app | jq
```

### 性能监控

```bash
# 容器资源使用
docker stats gravix-app --no-stream

# 持续监控
docker stats gravix-app
```

## 🔄 更新和维护

### 更新镜像

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 重启服务
docker-compose up -d
```

### 备份数据

```bash
# 备份日志
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# 备份配置
cp .env .env.backup
```

### 数据恢复

```bash
# 恢复日志
tar -xzf logs-backup-20260404.tar.gz

# 恢复配置
cp .env.backup .env
```

## 🚢 CI/CD集成

### GitHub Actions示例

```yaml
name: Docker Build

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build Docker image
        run: docker build -t gravix:${{ github.sha }} .

      - name: Log in to Docker Hub
        run: docker login -u ${{ secrets.DOCKER_USERNAME }} -p ${{ secrets.DOCKER_PASSWORD }}

      - name: Push to Docker Hub
        run: docker push gravix:${{ github.sha }}
```

## 💡 最佳实践

1. **使用特定版本标签**
   ```bash
   docker build -t gravix:v1.0.0 .
   docker run gravix:v1.0.0
   ```

2. **日志轮转**
   - 配置日志驱动限制大小
   - 定期清理旧日志

3. **资源限制**
   - 设置CPU和内存限制
   - 防止容器耗尽主机资源

4. **安全实践**
   - 不要在镜像中包含敏感信息
   - 使用 `.dockerignore` 排除不必要文件
   - 定期更新基础镜像

5. **健康检查**
   - 配置合适的健康检查间隔
   - 设置合理的超时和重试次数

## 📚 相关文档

- [README.md](README.md) - 项目总览
- [LLM_SETUP_GUIDE.md](LLM_SETUP_GUIDE.md) - LLM配置
- [LLM_RESILIENCE.md](LLM_RESILIENCE.md) - 稳定性优化

## 🆘 获取帮助

遇到问题？

1. 查看日志：`docker-compose logs -f`
2. 检查健康状态：`curl http://localhost:8000/health`
3. 查看容器状态：`docker-compose ps`
4. 提交Issue：https://github.com/rankang666/Gravix/issues
