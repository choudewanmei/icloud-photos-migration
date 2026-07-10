# iCloud 照片迁移助手

将 iCloud 照片和视频安全迁移到您的 NAS。

## 功能特点

- ✅ **完整迁移**：下载 iCloud 中的所有照片和视频
- ✅ **增量同步**：只下载新文件，跳过已存在的
- ✅ **智能组织**：按 `年/年-月/年-月-日` 自动创建目录结构
- ✅ **断点续传**：中断后可从上次位置继续
- ✅ **去重处理**：自动识别重复文件
- ✅ **图形界面**：直观的进度显示和操作界面
- ✅ **失败记录**：失败文件记录日志，不中断整体流程

## 系统要求

- **操作系统**：macOS 10.15 或更高版本
- **Python**：3.8 或更高版本
- **NAS**：支持 SMB 协议，已挂载到 macOS

## 安装步骤

### 1. 安装 Python（如果未安装）

```bash
# 使用 Homebrew 安装
brew install python

# 或从官网下载：https://www.python.org/downloads/
```

### 2. 安装依赖

```bash
# 进入项目目录
cd iCloud照片迁移助手

# 安装依赖
pip3 install -r requirements.txt
```

### 3. 挂载 NAS

在 Finder 中：
1. 按 `Cmd + K` 打开"连接服务器"
2. 输入 NAS 地址：`smb://你的NAS地址`
3. 选择共享文件夹
4. 挂载后会出现在 `/Volumes/` 目录下

或使用命令行：
```bash
# 创建挂载点
sudo mkdir -p /Volumes/MyNAS

# 挂载 SMB
mount_smbfs //username:password@NAS_IP/share /Volumes/MyNAS
```

## 使用方法

### 首次运行

1. **双击 `run.command`** 启动应用

2. **步骤 1：连接 iCloud**
   - 输入你的 Apple ID
   - 点击"连接 iCloud"
   - 在弹出的终端窗口中输入密码和验证码
   - 等待认证成功

3. **步骤 2：设置 NAS 路径**
   - 输入或浏览选择 NAS 挂载路径（如 `/Volumes/MyNAS/iCloud-Photos`）
   - 点击"检测 NAS 连接"
   - 等待显示"✅ NAS 已连接"

4. **开始迁移**
   - 点击"开始迁移"按钮
   - 迁移过程中可以：
     - 查看实时进度
     - 暂停/继续下载
     - 查看详细日志

5. **完成报告**
   - 迁移完成后显示统计报告
   - 可导出报告文件
   - 可查看失败文件列表（如有）

### 日常使用

迁移中断后再次运行：
1. 双击 `run.command`
2. 应用会自动检测上次未完成的迁移
3. 选择"继续迁移"即可从断点继续

## 配置文件

配置文件 `config.yaml` 会在首次运行时自动生成，可手动编辑：

```yaml
apple_id: "your@apple.id"
nas_path: "/Volumes/MyNAS/iCloud-Photos"
cookie_dir: "./cookies"
folder_format: "%Y/%Y-%m/%Y-%d"
threads_num: 5
only_new: true
download_photos: true
download_videos: true
skip_live_photos: false
```

### 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `apple_id` | Apple ID 邮箱 | - |
| `nas_path` | NAS 挂载路径 | - |
| `cookie_dir` | 认证 cookie 存储目录 | `./cookies` |
| `folder_format` | 目录结构格式 | `%Y/%Y-%m/%Y-%d` |
| `threads_num` | 下载并发数 | `5` |
| `only_new` | 仅下载新文件 | `true` |
| `download_photos` | 下载照片 | `true` |
| `download_videos` | 下载视频 | `true` |
| `skip_live_photos` | 跳过 Live Photos | `false` |

## 目录结构

迁移后的文件会按以下结构组织：

```
iCloud-Photos/
├── 2023/
│   ├── 2023-01/
│   │   ├── 2023-01-01/
│   │   │   ├── IMG_0001.HEIC
│   │   │   ├── IMG_0002.JPG
│   │   │   └── VID_0001.MOV
│   │   ├── 2023-01-15/
│   │   │   └── ...
│   │   └── ...
│   ├── 2023-02/
│   │   └── ...
│   └── ...
├── 2024/
│   └── ...
└── _duplicates/  # 去重后的重复文件（可选）
    └── ...
```

## 常见问题

### Q: 认证失败怎么办？

A: 
1. 确认 Apple ID 和密码正确
2. 确认已开启两步验证
3. 检查网络连接
4. 尝试删除 `cookies` 目录后重新认证

### Q: NAS 连接检测失败？

A:
1. 确认 NAS 已正确挂载到 `/Volumes/`
2. 在 Finder 中确认可以访问 NAS
3. 检查 NAS 路径是否正确
4. 确认有写入权限

### Q: 下载速度很慢？

A:
1. 检查网络带宽
2. 减少 `threads_num` 并发数（网络不稳定时）
3. 避免同时进行其他大流量操作

### Q: 如何查看详细日志？

A:
- 应用内：点击"查看完整日志"按钮
- 文件：查看 `logs/` 目录下的日志文件

### Q: 迁移中断了怎么办？

A:
1. 再次运行应用
2. 应用会自动检测未完成的迁移
3. 选择"继续迁移"即可

### Q: 如何重新开始迁移？

A:
1. 删除 `migration_state.db` 文件
2. 删除 `cookies` 目录
3. 重新运行应用

## 文件说明

| 文件/目录 | 说明 |
|-----------|------|
| `run.command` | 启动脚本（双击运行） |
| `main.py` | Python 入口文件 |
| `config.yaml` | 配置文件 |
| `migration_state.db` | 状态数据库 |
| `cookies/` | iCloud 认证 cookie |
| `logs/` | 运行日志 |
| `core/` | 核心功能模块 |
| `gui/` | 图形界面模块 |

## 技术栈

- **PySide6**：Qt for Python，GUI 框架
- **icloudpd**：iCloud 照片下载工具
- **SQLite**：状态数据库
- **PyYAML**：配置文件解析

## 许可证

MIT License

## 问题反馈

如遇到问题，请提供以下信息：
1. macOS 版本
2. Python 版本（`python3 --version`）
3. 错误信息或日志
4. 操作步骤

## 扫码登录

本工具支持两种 iCloud 登录方式：

### 1. 扫码登录（推荐）

扫码登录更安全、更便捷，推荐使用：

1. 选择"扫码登录（推荐）"
2. 点击"生成二维码"
3. 使用 iPhone 相机扫描二维码
4. 在 iPhone 上完成认证
5. 等待认证成功

**优势**：
- ✅ 无需输入密码，更安全
- ✅ 扫码即登录，更便捷
- ✅ 自动处理两步验证

详细说明请查看：[扫码登录指南](SCAN_LOGIN_GUIDE.md)

### 2. 密码登录

传统登录方式：

1. 选择"密码登录"
2. 输入 Apple ID
3. 点击"连接 iCloud"
4. 在终端中输入密码和验证码

## 依赖

```bash
pip3 install -r requirements.txt
```

包含以下依赖：
- PySide6 - GUI 框架
- icloudpd - iCloud 下载引擎
- pyyaml - 配置管理
- qrcode - 二维码生成
- Pillow - 图像处理
