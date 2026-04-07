#!/bin/bash

# 检查程序是否运行
PID=$(ps aux | grep 'python main.py' | grep -v grep | awk '{print $2}')

# 如果 PID 存在，则杀掉该进程
if [ ! -z "$PID" ]; then
    echo "Process found. Killing PID $PID"
    kill -9 $PID
    echo "Process killed."
else
    echo "No process found running "
fi

MODE=${1:-local}  # local=本地开发机，docker=docker容器
WORKERS=${UVICORN_WORKERS:-1}  # 进程数，默认为 1，UVICORN_WORKERS来自环境变量
# --no-access-log: 关闭 uvicorn 的访问日志；--log-config None: 禁用 uvicorn 的默认日志配置；最佳 workers 数 = (2 * CPU核心数) + 1
if [ "$MODE" = "docker" ]; then
    uvicorn main:app --host 0.0.0.0 --port 3002 --workers $WORKERS --no-access-log
else
    nohup python main.py > /dev/null 2>&1 &
    echo "main-app Server started"
fi