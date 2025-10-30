# IPTV直播源爬虫项目

官方发布站：https://taoiptv.com

技术交流群：https://qm.qq.com/q/4ZwUd7rlb2

## 项目简介

这是一个IPTV直播源自动爬取和管理系统，支持：
- 酒店IPTV源爬取
- 组播源解析
- 直播源有效性检测
- 自动生成M3U播放列表

### Python 版本要求

- 推荐：Python 3.8 ~ 3.11（稳定、生态完备）
- 最低：Python 3.7（因 `numpy>=1.20` 需要 Python≥3.7）
- 如使用 Conda，建议：`conda create -n iptv python=3.8`

### 项目用途/应用场景

- 自动化收集各省市酒店/组播直播源，过滤低分辨率，优先保留 1080p 及以上；
- 周期性测速筛选，优先保留稳定、流畅的优质源；
- 每日自动检测，持续输出可直接导入播放器的 `M3U` 列表；
- 适合个人自建 IPTV 列表、家庭播放、离线播放器导入、盒子类软件订阅等使用；

## 快速部署

### 方法一：宝塔面板部署（推荐）

适合新手，一步一步照做即可。

1) 上传与解压
- 将项目打包为 zip 上传到服务器任意目录（如 `/www/wwwroot/iptv`），并在宝塔面板文件管理中解压。

2) 进入项目目录并安装依赖（避免 pip/pip3 混乱）
- 打开宝塔终端（或SSH），进入项目目录：
```bash
cd /www/wwwroot/iptv
```
- 优先使用“python3 -m pip”安装，确保装到正确的 Python3：
```bash
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
- 如服务器只有 `pip` 没有 `pip3`，也可以：
```bash
python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

3) 安装系统依赖（FFmpeg 等）
- Debian/Ubuntu：
```bash
sudo apt update && sudo apt install -y ffmpeg libgl1 libglib2.0-0
```
- CentOS/RHEL：
```bash
sudo yum install -y epel-release ffmpeg mesa-libGL glib2
```

4) 数据库准备（避免“连接失败/找不到库/找不到表”的报错）
- 若使用本机 MySQL，执行：
```bash
mysql -e "CREATE DATABASE IF NOT EXISTS iptv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -e "CREATE USER IF NOT EXISTS 'iptv'@'localhost' IDENTIFIED BY 'iptv';"
mysql -e "GRANT ALL PRIVILEGES ON iptv.* TO 'iptv'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"
mysql iptv < data/iptv_data.sql
```
- 若使用宝塔的 MySQL，请在“数据库”界面中创建名为 `iptv` 的库与用户，授予权限，然后在终端执行：
```bash
mysql iptv < data/iptv_data.sql
```

5) 配置环境变量（API Token）
```bash
cp env.example .env
vi .env   # 编辑 QUAKE_TOKEN（360网络测绘）
```

6) 首次运行测试（看到持续滚动日志为正常）
```bash
python3 start.py
```

如果提示“缺少依赖”，请确认是用 `python3 -m pip install -r requirements.txt` 安装的；如果使用了 `pip` 但系统默认指向 Python2/其他环境，也会导致此问题。

### 方法二：手动部署（通用服务器/SSH）

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

5. 运行项目（看到滚动日志即正常）：
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

## 定时任务（明确说明）

目的：每天自动更新直播源文件。

方式一：Linux crontab
```bash
crontab -e
# 每天 02:00 执行（将路径改为你的项目目录）
0 2 * * * cd /www/wwwroot/iptv && /usr/bin/python3 start.py >> /var/log/iptv.log 2>&1
```

方式二：宝塔-计划任务
- 面板 → 计划任务 → 添加计划任务
- 任务类型：Shell 脚本
- 执行周期：每天 02:00
- 脚本内容：
```bash
cd /www/wwwroot/iptv && /usr/bin/python3 start.py >> /var/log/iptv.log 2>&1
```
- 保存后即可。若 python3 路径不同，请用 `which python3` 查询真实路径。

## 运行结果在哪（非常重要）

- 生成的聚合文本：`source/iptv.txt`
- 同步生成的 M3U 列表：`source/iptv.m3u`（由 `tools.convertToM3u` 转换产生）
- 分省份/组播的原始/转换文件：`source/hotels/`、`source/multicast/`、`source/download/`
- 运行日志（若使用定时任务示例）：`/var/log/iptv.log`

你可以直接把 `source/iptv.m3u` 导入播放器（如 VLC、PotPlayer、TVBox 等）试播。

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
    ├── iptv.txt           # 最终聚合输出（TXT）
    └── iptv.m3u           # 最终聚合输出（M3U）
```

## 常见问题（FAQ）

1) 运行 `python3 start.py` 数据库报错？
- 确认已创建数据库/用户，并且已导入 `data/iptv_data.sql`。
- 确认 `.env` 或 `config.py` 中数据库指向 `localhost/127.0.0.1` 且账号密码正确。

2) 宝塔测试提示缺少依赖，`pip3` 无效？
- 使用 `python3 -m pip install -r requirements.txt`，确保安装到 Python3。
- 或者使用完整路径：`/usr/bin/python3 -m pip install -r requirements.txt`。

3) FFmpeg/依赖缺失导致测速失败？
- 按上文“系统依赖”安装 FFmpeg；最小系统还需安装 `ca-certificates tzdata curl` 等基础包。

4) Windows/Powershell 执行与 Linux 不一致？
- 建议在 Linux 环境或宝塔终端执行；Windows 请用 CMD 或 Anaconda Prompt，并优先 `python -m pip`。

5) 网络不稳定导致下载/请求超时？
- 稍后重试或切换服务器网络；依赖安装可使用清华源加速（文中示例已给出）。

6) API Token 从哪来？
- 访问 `https://quake.360.net` 申请，填入 `.env` 的 `QUAKE_TOKEN`。


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
