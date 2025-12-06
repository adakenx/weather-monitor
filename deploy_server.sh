#!/bin/bash

# 服务器端部署脚本
# 在腾讯云服务器上执行

set -e

WORK_DIR="/home/ubuntu/weather-monitor"
cd $WORK_DIR

echo "=========================================="
echo "    北京天气监控 - 服务器部署"
echo "=========================================="

# 1. 创建虚拟环境
echo ""
echo "[1/5] 创建Python虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
else
    echo "✅ 虚拟环境已存在"
fi

# 2. 激活虚拟环境并安装依赖
echo ""
echo "[2/5] 安装Python依赖..."
source venv/bin/activate
pip install -r requirements.txt -q
echo "✅ 依赖安装完成"

# 3. 测试连接
echo ""
echo "[3/5] 测试API连接..."
python weather_monitor.py test

# 4. 配置Cron定时任务
# 北京时间06:00执行 = 滑铁卢17:00(冬季)
echo ""
echo "[4/5] 配置定时任务..."

# 移除旧的天气监控cron（如果有）
crontab -l 2>/dev/null | grep -v "weather-monitor" | crontab - 2>/dev/null || true

# 添加新的cron任务：每天北京时间06:00执行
(crontab -l 2>/dev/null; echo "0 6 * * * cd $WORK_DIR && source venv/bin/activate && python weather_monitor.py once >> $WORK_DIR/weather.log 2>&1") | crontab -

echo "✅ Cron定时任务已配置"

# 5. 显示配置结果
echo ""
echo "[5/5] 验证配置..."
echo ""
echo "当前Cron任务:"
crontab -l | grep weather

echo ""
echo "=========================================="
echo "           部署完成！"
echo "=========================================="
echo ""
echo "📋 管理命令:"
echo "   查看日志: tail -f $WORK_DIR/weather.log"
echo "   手动测试: cd $WORK_DIR && source venv/bin/activate && python weather_monitor.py once"
echo "   编辑cron: crontab -e"
echo ""
echo "⏰ 推送时间: 每天 06:00 (北京时间) = 17:00 (滑铁卢冬季)"
echo ""
