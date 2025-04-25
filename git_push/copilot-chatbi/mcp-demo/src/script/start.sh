#! /bin/bash
# set -x

python3 src/main.py

sleep 10

# 防止容器退出，禁止删除
while true
do
    sleep 60
done
