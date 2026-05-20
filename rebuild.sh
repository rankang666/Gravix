#!/bin/bash
set -e

echo "🔄 完整重建 Gravix (仅在 Dockerfile 或 requirements.txt 改变时使用)"

# 拉取最新代码
echo "📥 拉取最新代码..."
git stash push -u -m "保存本地更改"
git pull origin main
git stash pop

# 停止并删除旧容器
echo "⏹️  停止旧容器..."
docker-compose down

# 重新构建镜像
echo "🔨 重新构建镜像..."
docker-compose build

# 启动新容器
echo "🚀 启动新容器..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 5

# 检查健康状态
echo "🔍 检查服务健康状态..."
if curl -f http://localhost:8001/health; then
    echo ""
    echo "✅ 重建成功！"
    echo ""
    echo "🌐 访问地址："
    echo "   - Web UI: http://localhost:8001"
    echo "   - WebSocket: ws://localhost:8001/ws"
    echo "   - 健康检查: http://localhost:8001/health"
else
    echo ""
    echo "❌ 重建失败，查看日志："
    echo ""
    docker-compose logs --tail=100 gravix
fi
