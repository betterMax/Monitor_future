#!/bin/bash
source /root/app/Monitor_future/venv/bin/activate
git pull origin main
pip install -r requirements.txt
alembic upgrade head
# 其他部署步骤，如重启服务等