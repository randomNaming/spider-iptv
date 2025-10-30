# IPTV直播源爬虫项目

官方发布站：https://taoiptv.com

技术交流群：https://qm.qq.com/q/4ZwUd7rlb2

## 项目简介

这是一个IPTV直播源自动爬取和管理系统，支持：
- 酒店IPTV源爬取
- 组播源解析
- 直播源有效性检测
- 自动生成M3U播放列表

## 快速部署

### 方法一：宝塔面板部署（推荐）

1. 上传项目文件到服务器
2. 在宝塔面板终端执行：
```bash
python3 baota_deploy.py
```

### 方法二：手动部署

1. 安装系统依赖：
```bash
# CentOS/RHEL
yum install -y python3 python3-pip mysql-server ffmpeg

# Ubuntu/Debian  
apt update && apt install -y python3 python3-pip mysql-server ffmpeg
```

2. 安装Python依赖：
```bash
pip3 install -r requirements.txt
```

3. 配置数据库：
```bash
# 创建数据库
mysql -e "CREATE DATABASE iptv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER 'iptv'@'localhost' IDENTIFIED BY 'iptv';"
mysql -e "GRANT ALL PRIVILEGES ON iptv.* TO 'iptv'@'localhost';"

# 导入数据库结构
mysql iptv < data/iptv_data.sql
```

4. 配置环境变量：
```bash
cp env.example .env
# 编辑 .env 文件，配置 QUAKE_TOKEN
```

5. 运行项目：
```bash
python3 start.py
```

## 配置说明

### 环境变量配置

复制 `env.example` 为 `.env` 并修改以下配置：

```bash
# 数据库配置
DB_HOST=localhost
DB_USER=iptv
DB_PASSWORD=iptv
DB_NAME=iptv

# API配置（必须配置）
QUAKE_TOKEN=你的360网络测绘API_TOKEN
```

### 获取API Token

1. 访问 https://quake.360.net
2. 注册账号并获取API Token
3. 将Token填入 `.env` 文件

## 定时任务

项目支持定时执行，每天凌晨2点自动运行：

```bash
# 添加定时任务
crontab -e

# 添加以下行（替换为实际路径）
0 2 * * * cd /path/to/iptv && python3 start.py >> /var/log/iptv.log 2>&1
```

## 文件结构

```
spider-iptv/
├── config.py              # 配置文件
├── main.py                # 主程序
├── start.py               # 启动脚本
├── startiptv.py           # 资源下载
├── hotels.py              # 酒店源处理
├── multicast.py           # 组播源处理
├── iptvdata.py            # 数据处理
├── tools.py               # 工具类
├── requirements.txt       # Python依赖
├── deploy.sh              # 部署脚本
├── baota_deploy.py        # 宝塔部署脚本
├── env.example            # 环境变量示例
├── data/
│   └── iptv_data.sql      # 数据库结构
└── source/                # 输出目录
    ├── download/          # 下载文件
    ├── hotels/            # 酒店源
    ├── multicast/         # 组播源
    └── iptv.txt           # 最终输出
```

## 注意事项

1. 确保MySQL服务正常运行
2. 必须配置有效的QUAKE_TOKEN
3. 确保服务器有足够的网络带宽
4. 建议在VPS或独立服务器上运行

## 故障排除

### 数据库连接失败
- 检查MySQL服务状态：`systemctl status mysql`
- 验证数据库配置：检查 `.env` 文件
- 确认数据库用户权限

### API请求失败
- 检查网络连接
- 验证QUAKE_TOKEN是否有效
- 查看日志文件：`tail -f /var/log/iptv.log`

### 依赖安装失败
- 更新pip：`pip3 install --upgrade pip`
- 使用国内镜像：`pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`
