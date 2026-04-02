#!/bin/bash
# Gravix 服务状态检查脚本

echo "================================"
echo "Gravix 服务状态检查"
echo "================================"
echo ""

# 检查进程
echo "1. 检查服务进程:"
if ps aux | grep -v grep | grep "python.*run_all.py" > /dev/null; then
    PID=$(ps aux | grep -v grep | grep "python.*run_all.py" | awk '{print $2}')
    echo "   ✅ 服务正在运行 (PID: $PID)"
else
    echo "   ❌ 服务未运行"
    exit 1
fi

echo ""

# 检查端口
echo "2. 检查WebSocket端口:"
if lsof -i :8765 | grep LISTEN > /dev/null; then
    echo "   ✅ WebSocket 端口 8765 正在监听"
else
    echo "   ❌ WebSocket 端口 8765 未监听"
fi

echo ""

# 检查MCP进程
echo "3. 检查MCP服务器:"
MCP_COUNT=$(ps aux | grep -v grep | grep "alibabacloud-dataworks-mcp-server" | wc -l)
if [ $MCP_COUNT -gt 0 ]; then
    echo "   ✅ DataWorks MCP 正在运行 ($MCP_COUNT 个进程)"
else
    echo "   ⚠️  DataWorks MCP 未运行"
fi

echo ""

# 显示最近日志
echo "4. 最近的日志 (最后10行):"
echo "----------------------------------------"
if [ -f /tmp/gravix.log ]; then
    tail -10 /tmp/gravix.log
else
    echo "   日志文件未找到"
fi

echo ""
echo "================================"
echo "检查完成"
echo "================================"
