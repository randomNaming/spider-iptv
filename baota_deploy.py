#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宝塔面板IPTV项目部署脚本
适用于宝塔面板环境
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, check=True):
    """执行命令"""
    print(f"执行命令: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(f"输出: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return None

def check_python():
    """检查Python环境"""
    print("检查Python环境...")
    result = run_command("python3 --version")
    if result and result.returncode == 0:
        print("Python3环境正常")
        return True
    else:
        print("Python3环境异常，尝试安装...")
        run_command("yum install -y python3 python3-pip", check=False)
        return True

def install_dependencies():
    """安装依赖"""
    print("安装Python依赖...")
    
    # 升级pip
    run_command("python3 -m pip install --upgrade pip", check=False)
    
    # 安装依赖
    if os.path.exists("requirements.txt"):
        run_command("pip3 install -r requirements.txt", check=False)
    else:
        # 手动安装主要依赖
        deps = [
            "mysql-connector-python",
            "requests",
            "beautifulsoup4",
            "opencv-python",
            "m3u8",
            "numpy",
            "timeout-decorator",
            "python-dotenv"
        ]
        for dep in deps:
            run_command(f"pip3 install {dep}", check=False)
    
    print("依赖安装完成")

def setup_database():
    """设置数据库"""
    print("设置数据库...")
    
    # 检查MySQL是否运行
    result = run_command("systemctl is-active mysql", check=False)
    if result and result.returncode != 0:
        print("启动MySQL服务...")
        run_command("systemctl start mysql", check=False)
        run_command("systemctl enable mysql", check=False)
    
    # 创建数据库和用户
    db_commands = [
        "CREATE DATABASE IF NOT EXISTS iptv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "CREATE USER IF NOT EXISTS 'iptv'@'localhost' IDENTIFIED BY 'iptv';",
        "GRANT ALL PRIVILEGES ON iptv.* TO 'iptv'@'localhost';",
        "FLUSH PRIVILEGES;"
    ]
    
    for cmd in db_commands:
        run_command(f'mysql -e "{cmd}"', check=False)
    
    # 导入数据库结构
    if os.path.exists("data/iptv_data.sql"):
        print("导入数据库结构...")
        run_command("mysql iptv < data/iptv_data.sql", check=False)
    
    print("数据库设置完成")

def create_directories():
    """创建目录结构"""
    print("创建目录结构...")
    
    dirs = [
        "source",
        "source/download",
        "source/hotels", 
        "source/multicast"
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"创建目录: {dir_path}")
    
    print("目录结构创建完成")

def setup_env_file():
    """设置环境配置文件"""
    print("设置环境配置文件...")
    
    if not os.path.exists(".env"):
        if os.path.exists("env.example"):
            shutil.copy("env.example", ".env")
            print("已创建 .env 文件")
        else:
            # 创建默认配置
            with open(".env", "w", encoding="utf-8") as f:
                f.write("""# IPTV项目环境变量配置文件
DB_HOST=localhost
DB_USER=iptv
DB_PASSWORD=iptv
DB_NAME=iptv
QUAKE_TOKEN=你的360网络测绘API_TOKEN
PYTHON_PATH=/usr/bin/python3
""")
            print("已创建默认 .env 文件")
    else:
        print(".env 文件已存在")
    
    print("请编辑 .env 文件配置API Token")

def install_ffmpeg():
    """安装FFmpeg"""
    print("检查FFmpeg...")
    
    result = run_command("ffmpeg -version", check=False)
    if result and result.returncode == 0:
        print("FFmpeg已安装")
    else:
        print("安装FFmpeg...")
        run_command("yum install -y epel-release", check=False)
        run_command("yum install -y ffmpeg", check=False)
        print("FFmpeg安装完成")

def create_cron_job():
    """创建定时任务"""
    print("设置定时任务...")
    
    current_dir = os.getcwd()
    cron_cmd = f"0 2 * * * cd {current_dir} && python3 main.py >> /var/log/iptv.log 2>&1"
    
    # 检查是否已存在定时任务
    result = run_command("crontab -l", check=False)
    if result and cron_cmd not in result.stdout:
        # 添加定时任务
        if result.stdout.strip():
            new_cron = result.stdout.strip() + "\n" + cron_cmd
        else:
            new_cron = cron_cmd
        
        with open("/tmp/iptv_cron", "w") as f:
            f.write(new_cron)
        
        run_command("crontab /tmp/iptv_cron", check=False)
        os.remove("/tmp/iptv_cron")
        print("定时任务设置完成")
    else:
        print("定时任务已存在")

def main():
    """主函数"""
    print("=" * 50)
    print("宝塔面板IPTV项目部署脚本")
    print("=" * 50)
    
    try:
        check_python()
        install_dependencies()
        setup_database()
        create_directories()
        setup_env_file()
        install_ffmpeg()
        create_cron_job()
        
        print("=" * 50)
        print("部署完成！")
        print("=" * 50)
        print("下一步操作：")
        print("1. 编辑 .env 文件，配置 QUAKE_TOKEN")
        print("2. 运行测试: python3 main.py")
        print("3. 查看日志: tail -f /var/log/iptv.log")
        
    except Exception as e:
        print(f"部署过程中出现错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
