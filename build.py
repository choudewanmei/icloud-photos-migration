#!/usr/bin/env python3
"""
iCloud 照片迁移助手 - 打包脚本
用于将项目打包成 macOS .app 应用
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """清理构建目录"""
    dirs_to_clean = ['build', 'dist', '*.spec']
    for pattern in dirs_to_clean:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"✅ 清理目录: {path}")
            elif path.is_file():
                path.unlink()
                print(f"✅ 清理文件: {path}")


def build_app():
    """构建 .app 应用"""
    print("\n🔨 开始构建应用...")
    
    # PyInstaller 命令
    cmd = [
        'python3', '-m', 'PyInstaller',
        '--name=iCloud照片迁移助手',
        '--windowed',                    # 无控制台窗口
        '--onedir',                      # 打包成目录（而非单文件）
        '--noconfirm',                   # 覆盖输出目录
        '--clean',                       # 清理临时文件
        '--add-data=core:core',          # 添加 core 模块
        '--add-data=gui:gui',            # 添加 gui 模块
        '--add-data=README.md:.',        # 添加说明文档
        '--add-data=QUICKSTART.md:.',    # 添加快速开始指南
        '--add-data=SCAN_LOGIN_GUIDE.md:.',  # 添加扫码登录指南
        '--icon=icon.png',               # 应用图标
        '--hidden-import=PySide6',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=qrcode',
        '--hidden-import=PIL',
        '--hidden-import=yaml',
        '--hidden-import=sqlite3',
        'main.py'
    ]
    
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出:\n{e.stderr}")
        return False


def create_dmg():
    """创建 DMG 安装包"""
    print("\n💿 创建 DMG 安装包...")
    
    app_path = Path('dist/iCloud照片迁移助手.app')
    dmg_path = Path('dist/iCloud照片迁移助手.dmg')
    
    if not app_path.exists():
        print(f"❌ 应用不存在: {app_path}")
        return False
    
    # 删除已存在的 DMG
    if dmg_path.exists():
        dmg_path.unlink()
    
    # 使用 hdiutil 创建 DMG
    cmd = [
        'hdiutil', 'create',
        '-volname', 'iCloud照片迁移助手',
        '-srcfolder', str(app_path),
        '-ov',
        '-format', 'UDZO',
        str(dmg_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ DMG 创建成功: {dmg_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ DMG 创建失败: {e}")
        print(f"错误输出:\n{e.stderr}")
        return False


def create_zip():
    """创建 ZIP 压缩包"""
    print("\n📦 创建 ZIP 压缩包...")
    
    app_path = Path('dist/iCloud照片迁移助手.app')
    zip_path = Path('dist/iCloud照片迁移助手.zip')
    
    if not app_path.exists():
        print(f"❌ 应用不存在: {app_path}")
        return False
    
    # 删除已存在的 ZIP
    if zip_path.exists():
        zip_path.unlink()
    
    # 使用 ditto 创建 ZIP（保留 macOS 元数据）
    cmd = [
        'ditto',
        '-c', '-k', '--sequesterRsrc', '--keepParent',
        str(app_path),
        str(zip_path)
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ ZIP 创建成功: {zip_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ ZIP 创建失败: {e}")
        print(f"错误输出:\n{e.stderr}")
        return False


def create_readme():
    """创建安装说明"""
    print("\n📝 创建安装说明...")
    
    readme_content = """# iCloud 照片迁移助手 - 安装说明

## 安装方法

### 方法一：使用 DMG 安装（推荐）

1. 双击 `iCloud照片迁移助手.dmg` 文件
2. 将 `iCloud照片迁移助手.app` 拖动到 `Applications` 文件夹
3. 在 Launchpad 或 Applications 中找到并打开应用

### 方法二：使用 ZIP 安装

1. 双击 `iCloud照片迁移助手.zip` 文件解压
2. 将解压后的 `iCloud照片迁移助手.app` 拖动到 `Applications` 文件夹
3. 在 Launchpad 或 Applications 中找到并打开应用

### 方法三：直接运行

1. 双击 `iCloud照片迁移助手.app` 文件即可运行

## 首次运行

1. 首次运行时，macOS 可能会提示"无法打开，因为无法验证开发者"
2. 解决方法：
   - 打开"系统偏好设置" -> "安全性与隐私"
   - 在"通用"选项卡中，点击"仍要打开"
   - 或者右键点击应用，选择"打开"

## 使用说明

详细的使用说明请查看应用内的帮助文档，或访问：
- README.md - 完整使用说明
- QUICKSTART.md - 快速开始指南
- SCAN_LOGIN_GUIDE.md - 扫码登录指南

## 系统要求

- macOS 10.15 或更高版本
- 无需安装 Python（已打包）

## 卸载方法

1. 将 `iCloud照片迁移助手.app` 从 `Applications` 文件夹拖到废纸篓
2. 清空废纸篓

## 常见问题

### Q: 应用无法打开？

A: 
1. 检查 macOS 版本是否满足要求
2. 尝试右键点击应用，选择"打开"
3. 在"安全性与隐私"中允许运行

### Q: 应用崩溃？

A: 
1. 重启应用
2. 重启 Mac
3. 重新下载应用

### Q: 如何更新？

A: 
1. 下载新版本
2. 替换旧版本
3. 重新运行

## 技术支持

如有问题，请提供以下信息：
1. macOS 版本
2. 应用版本
3. 错误信息或截图

## 版本历史

### v1.0.0
- 首次发布
- 支持 iCloud 照片迁移到 NAS
- 支持扫码登录
- 支持增量同步
- 支持断点续传
"""
    
    readme_path = Path('dist/安装说明.txt')
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"✅ 安装说明创建成功: {readme_path}")
    
    return True


def main():
    """主函数"""
    print("=" * 50)
    print("iCloud 照片迁移助手 - 打包工具")
    print("=" * 50)
    
    # 清理之前的构建
    print("\n1. 清理之前的构建...")
    clean_build()
    
    # 构建应用
    print("\n2. 构建应用...")
    if not build_app():
        print("\n❌ 打包失败!")
        return 1
    
    # 创建 DMG
    print("\n3. 创建 DMG 安装包...")
    create_dmg()
    
    # 创建 ZIP
    print("\n4. 创建 ZIP 压缩包...")
    create_zip()
    
    # 创建安装说明
    print("\n5. 创建安装说明...")
    create_readme()
    
    print("\n" + "=" * 50)
    print("✅ 打包完成!")
    print("=" * 50)
    print("\n输出文件:")
    print("  - 应用: dist/iCloud照片迁移助手.app")
    print("  - DMG:  dist/iCloud照片迁移助手.dmg")
    print("  - ZIP:  dist/iCloud照片迁移助手.zip")
    print("  - 说明: dist/安装说明.txt")
    print("\n分享方式:")
    print("  1. 分享 .dmg 文件（推荐，macOS 标准安装包）")
    print("  2. 分享 .zip 文件（通用，解压即用）")
    print("  3. 直接分享 .app 文件夹")
    print("\n注意事项:")
    print("  - 首次运行可能需要在'安全性与隐私'中允许")
    print("  - 建议将应用放到 Applications 文件夹")
    print("  - 应用已包含所有依赖，无需安装 Python")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
