#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IPTV项目启动脚本
支持环境变量加载和错误处理
"""

import os
import sys
import subprocess
from pathlib import Path

def load_env_file():
    """加载环境变量文件"""
    env_file = Path('.env')
    if env_file.exists():
        print("加载环境变量文件...")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("环境变量加载完成")
    else:
        print("未找到 .env 文件，使用默认配置")

def check_dependencies():
    """检查依赖"""
    print("检查依赖...")
    try:
        import mysql.connector
        import requests
        import bs4
        import cv2
        import m3u8
        import numpy
        print("所有依赖检查通过")
        return True
    except ImportError as e:
        print(f"缺少依赖: {e}")
        print("请运行: pip3 install -r requirements.txt")
        return False

def check_database():
    """检查数据库连接"""
    print("检查数据库连接...")
    try:
        import config
        db_config = config.config.get_db_config()
        
        import mysql.connector
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database']
        )
        conn.close()
        print("数据库连接正常")
        return True
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("请检查数据库配置和MySQL服务状态")
        return False

def run_scripts():
    """运行脚本"""
    print("开始执行IPTV脚本...")
    
    scripts = [
        'startiptv.py',
        'hotels.py', 
        'multicast.py',
        'iptvdata.py'
    ]
    
    for script in scripts:
        if os.path.exists(script):
            print(f"\n{'='*60}")
            print(f"正在执行脚本: {script}")
            print(f"{'='*60}")
            try:
                # 实时输出日志，不捕获到内存
                result = subprocess.run([sys.executable, script], 
                                      timeout=3600)
                if result.returncode == 0:
                    print(f"\n✓ {script} 执行成功")
                else:
                    print(f"\n✗ {script} 执行失败，退出码: {result.returncode}")
            except subprocess.TimeoutExpired:
                print(f"\n✗ {script} 执行超时（超过1小时）")
            except KeyboardInterrupt:
                print(f"\n⚠ {script} 被用户中断")
                break
            except Exception as e:
                print(f"\n✗ {script} 执行异常: {e}")
        else:
            print(f"⚠ 脚本不存在: {script}")

def main():
    """主函数"""
    print("=" * 60)
    print("IPTV项目启动脚本")
    print("=" * 60)
    
    # 加载环境变量
    load_env_file()
    
    # 检查依赖
    print("\n步骤1: 检查依赖包...")
    if not check_dependencies():
        print("❌ 依赖检查失败，程序退出")
        sys.exit(1)
    print("✅ 依赖检查通过")
    
    # 检查数据库
    print("\n步骤2: 检查数据库连接...")
    if not check_database():
        print("❌ 数据库连接失败，程序退出")
        sys.exit(1)
    print("✅ 数据库连接正常")
    
    # 运行脚本
    print("\n步骤3: 开始执行IPTV脚本...")
    run_scripts()
    
    print("\n" + "=" * 60)
    print("🎉 IPTV项目执行完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
