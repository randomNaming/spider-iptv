#!/bin/bash
# IPTV项目部署脚本
# 适用于宝塔面板和Linux服务器

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为root用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        log_error "请使用root用户运行此脚本"
        exit 1
    fi
}

# 检查系统类型
check_system() {
    if [ -f /etc/redhat-release ]; then
        OS="centos"
        log_info "检测到CentOS系统"
    elif [ -f /etc/debian_version ]; then
        OS="debian"
        log_info "检测到Debian/Ubuntu系统"
    else
        log_error "不支持的操作系统"
        exit 1
    fi
}

# 安装系统依赖
install_system_deps() {
    log_info "安装系统依赖..."
    
    if [ "$OS" = "centos" ]; then
        yum update -y
        yum install -y python3 python3-pip mysql-server ffmpeg
        systemctl start mysqld
        systemctl enable mysqld
    elif [ "$OS" = "debian" ]; then
        apt update
        apt install -y python3 python3-pip mysql-server ffmpeg
        systemctl start mysql
        systemctl enable mysql
    fi
    
    log_info "系统依赖安装完成"
}

# 安装Python依赖
install_python_deps() {
    log_info "安装Python依赖..."
    
    # 升级pip
    python3 -m pip install --upgrade pip
    
    # 安装依赖包
    pip3 install -r requirements.txt
    
    log_info "Python依赖安装完成"
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    # 检查MySQL是否运行
    if ! systemctl is-active --quiet mysql mysqld; then
        log_error "MySQL服务未运行，请先启动MySQL"
        exit 1
    fi
    
    # 创建数据库和用户
    mysql -e "CREATE DATABASE IF NOT EXISTS iptv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    mysql -e "CREATE USER IF NOT EXISTS 'iptv'@'localhost' IDENTIFIED BY 'iptv';"
    mysql -e "GRANT ALL PRIVILEGES ON iptv.* TO 'iptv'@'localhost';"
    mysql -e "FLUSH PRIVILEGES;"
    
    # 导入数据库结构
    if [ -f "data/iptv_data.sql" ]; then
        mysql iptv < data/iptv_data.sql
        log_info "数据库结构导入完成"
    else
        log_warn "未找到数据库结构文件 data/iptv_data.sql"
    fi
}

# 创建环境配置文件
setup_env() {
    log_info "创建环境配置文件..."
    
    if [ ! -f ".env" ]; then
        cp env.example .env
        log_info "已创建 .env 配置文件，请编辑其中的配置信息"
        log_warn "请务必修改 .env 文件中的 QUAKE_TOKEN 配置"
    else
        log_info ".env 文件已存在"
    fi
}

# 创建目录结构
create_directories() {
    log_info "创建目录结构..."
    
    mkdir -p source/download
    mkdir -p source/hotels
    mkdir -p source/multicast
    
    log_info "目录结构创建完成"
}

# 设置权限
set_permissions() {
    log_info "设置文件权限..."
    
    chmod +x *.py
    chmod +x deploy.sh
    chown -R www-data:www-data . 2>/dev/null || true
    
    log_info "权限设置完成"
}

# 创建定时任务
setup_cron() {
    log_info "设置定时任务..."
    
    # 获取当前目录
    CURRENT_DIR=$(pwd)
    
    # 创建定时任务
    (crontab -l 2>/dev/null; echo "0 2 * * * cd $CURRENT_DIR && python3 main.py >> /var/log/iptv.log 2>&1") | crontab -
    
    log_info "定时任务设置完成（每天凌晨2点执行）"
}

# 创建systemd服务
create_service() {
    log_info "创建systemd服务..."
    
    cat > /etc/systemd/system/iptv.service << EOF
[Unit]
Description=IPTV Service
After=network.target mysql.service

[Service]
Type=oneshot
User=www-data
WorkingDirectory=$(pwd)
ExecStart=/usr/bin/python3 main.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    log_info "systemd服务创建完成"
}

# 主函数
main() {
    log_info "开始部署IPTV项目..."
    
    check_root
    check_system
    install_system_deps
    install_python_deps
    setup_database
    setup_env
    create_directories
    set_permissions
    setup_cron
    create_service
    
    log_info "部署完成！"
    log_warn "请编辑 .env 文件配置API Token"
    log_info "可以使用以下命令测试运行："
    log_info "python3 main.py"
}

# 运行主函数
main "$@"
