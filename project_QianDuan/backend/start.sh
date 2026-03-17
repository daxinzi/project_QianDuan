#!/bin/bash

echo "启动写作空间后端服务..."

cd "$(dirname "$0")"

# 检查 MongoDB 是否运行
if ! command -v mongod &> /dev/null; then
    echo "警告: MongoDB 未安装或未启动"
    echo "请先安装 MongoDB: https://www.mongodb.com/try/download/community"
    echo ""
fi

# 安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装后端依赖..."
    npm install
fi

# 启动后端
echo "启动后端服务 (端口 3001)..."
node server.js &
BACKEND_PID=$!

echo "后端 PID: $BACKEND_PID"
echo ""
echo "服务已启动!"
echo "- 后端 API: http://localhost:3001"
echo "- 前端: http://localhost:8080"
echo ""
echo "按 Ctrl+C 停止服务"

# 捕获退出信号
trap "kill $BACKEND_PID 2>/dev/null" EXIT

wait
