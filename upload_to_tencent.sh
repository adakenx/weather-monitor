#!/bin/bash

# 腾讯云服务器上传脚本
# 自动上传天气监控项目到腾讯云服务器

set -e

# 服务器配置
SERVER_IP="your_server_ip"
USERNAME="ubuntu"
PASSWORD="your_password"
REMOTE_DIR="/home/ubuntu/weather-monitor"
LOCAL_DIR="$(dirname "$0")"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 测试服务器连接
test_connection() {
    print_status "测试服务器连接..."
    
    if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$USERNAME@$SERVER_IP" "echo '连接成功'" 2>/dev/null; then
        print_success "服务器连接正常"
    else
        print_error "无法连接到服务器"
        exit 1
    fi
}

# 创建远程目录
create_remote_directory() {
    print_status "创建远程目录..."
    
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USERNAME@$SERVER_IP" "mkdir -p $REMOTE_DIR"
    print_success "远程目录创建成功: $REMOTE_DIR"
}

# 上传文件
upload_files() {
    print_status "开始上传文件..."
    
    # 上传Python文件和配置
    local files=(
        "weather_monitor.py"
        "config.py"
        "requirements.txt"
        "deploy_server.sh"
    )
    
    for file in "${files[@]}"; do
        if [ -f "$LOCAL_DIR/$file" ]; then
            sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no \
                "$LOCAL_DIR/$file" "$USERNAME@$SERVER_IP:$REMOTE_DIR/"
            print_success "已上传: $file"
        fi
    done
    
    print_success "文件上传完成"
}

# 远程部署
remote_deploy() {
    print_status "在服务器上执行部署..."
    
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USERNAME@$SERVER_IP" "
        cd $REMOTE_DIR
        chmod +x deploy_server.sh
        ./deploy_server.sh
    "
    
    print_success "远程部署完成"
}

# 显示完成信息
show_info() {
    echo ""
    echo "=========================================="
    echo "         天气监控部署完成"
    echo "=========================================="
    echo ""
    echo "服务器: $USERNAME@$SERVER_IP"
    echo "目录: $REMOTE_DIR"
    echo ""
    echo "管理命令:"
    echo "  查看日志: ssh $USERNAME@$SERVER_IP 'tail -f $REMOTE_DIR/weather.log'"
    echo "  手动测试: ssh $USERNAME@$SERVER_IP 'cd $REMOTE_DIR && python3 weather_monitor.py once'"
    echo "  查看cron: ssh $USERNAME@$SERVER_IP 'crontab -l | grep weather'"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo "=========================================="
    echo "    北京天气监控 - 上传到腾讯云"
    echo "=========================================="
    echo ""
    
    # 检查sshpass
    if ! command -v sshpass &> /dev/null; then
        print_error "sshpass未安装"
        echo "请运行: brew install hudochenkov/sshpass/sshpass"
        exit 1
    fi
    
    test_connection
    echo ""
    
    create_remote_directory
    echo ""
    
    upload_files
    echo ""
    
    remote_deploy
    echo ""
    
    show_info
}

main "$@"

