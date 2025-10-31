#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IPTV项目配置文件
用于统一管理数据库连接信息和API配置
"""

import os
from typing import Dict, Any

class Config:
    """配置类"""
    
    def __init__(self):
        """初始化配置"""
        self.load_config()
    
    def load_config(self):
        """加载配置信息"""
        # 数据库配置
        self.DB_CONFIG = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'iptv'),
            'password': os.getenv('DB_PASSWORD', 'iptv'),
            'database': os.getenv('DB_NAME', 'iptv'),
            'pool_name': 'iptv_pool',
            'pool_size': 10
        }
        
        # API配置
        self.API_CONFIG = {
            'quake_token': os.getenv('QUAKE_TOKEN', ''),
            'hotels_token': os.getenv('HOTELS_TOKEN', ''),
            'timeout': 30
        }
        
        # 文件路径配置
        self.PATH_CONFIG = {
            'source_dir': 'source/',
            'download_dir': 'source/download/',
            'hotels_dir': 'source/hotels/',
            'multicast_dir': 'source/multicast/',
            'output_file': 'source/iptv.txt'
        }
    
    def get_db_config(self) -> Dict[str, Any]:
        """获取数据库配置"""
        return self.DB_CONFIG.copy()
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self.API_CONFIG.copy()
    
    def get_path_config(self) -> Dict[str, Any]:
        """获取路径配置"""
        return self.PATH_CONFIG.copy()

# 创建全局配置实例
config = Config()
