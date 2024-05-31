#!/bin/bash

# 更新系统
sudo apt update

# 安装 Python 3.10 和虚拟环境工具
sudo apt install -y python3.10 python3.10-venv python3.10-dev

# 创建虚拟环境
cd ~/app/monitoring_app
python3.10 -m venv venv

# 激活虚拟环境并安装依赖
source venv/bin/activate
pip install -r requirements.txt

echo "项目初始化完成。"

