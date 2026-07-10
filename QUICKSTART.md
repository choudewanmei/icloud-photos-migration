# 快速开始指南

## 第一步：安装依赖

```bash
cd iCloud照片迁移助手
pip3 install -r requirements.txt
```

等待安装完成（PySide6 约 100MB，需要几分钟）。

## 第二步：挂载 NAS

### 方法一：Finder 挂载（推荐）

1. 打开 Finder
2. 按 `Cmd + K` 打开"连接服务器"
3. 输入 NAS 地址：`smb://你的NAS地址`
4. 输入用户名和密码
5. 选择共享文件夹
6. 挂载成功后会出现在 Finder 侧边栏

### 方法二：命令行挂载

```bash
# 创建挂载点
sudo mkdir -p /Volumes/MyNAS

# 挂载（替换 username、password 和 NAS_IP）
mount_smbfs //username:password@NAS_IP/share /Volumes/MyNAS
```

## 第三步：启动应用

```bash
# 方法一：双击 run.command 文件

# 方法二：命令行启动
python3 main.py
```

## 第四步：配置迁移

1. **输入 Apple ID**
   - 输入你的 Apple ID 邮箱
   - 点击"连接 iCloud"
   - 在弹出的终端窗口中输入密码
   - 输入两步验证码

2. **设置 NAS 路径**
   - 输入 NAS 挂载路径（如 `/Volumes/MyNAS/iCloud-Photos`）
   - 点击"检测 NAS 连接"
   - 等待显示"✅ NAS 已连接"

3. **开始迁移**
   - 点击"开始迁移"
   - 等待下载完成

## 常见问题

### Q: 安装依赖失败？

```bash
# 升级 pip
pip3 install --upgrade pip

# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: NAS 无法挂载？

1. 确认 NAS 已开机并连接网络
2. 确认 SMB 服务已启用
3. 检查用户名和密码
4. 尝试使用 NAS 的 IP 地址

### Q: iCloud 认证失败？

1. 确认 Apple ID 正确
2. 确认已开启两步验证
3. 检查网络连接
4. 尝试删除 `cookies` 目录重试

## 获取帮助

查看完整文档：[README.md](README.md)
