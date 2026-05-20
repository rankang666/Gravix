#!/bin/bash
set -e

echo "🔄 开始部署 Gravix..."

# 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin main

# 停止旧容器
echo "⏹️  停止旧容器..."
docker compose down

# 重新构建并启动
echo "🔨 重新构建并启动..."
docker compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查健康状态
echo "🔍 检查服务健康状态..."
if curl -f http://localhost:8001/health; then
    echo "✅ 部署成功！"
else
    echo "❌ 部署失败，请检查日志"
    docker compose logs gravix
    exit 1
fi

echo "🎉 部署完成！"
