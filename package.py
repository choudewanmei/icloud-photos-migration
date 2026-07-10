#!/usr/bin/env python3
"""
打包脚本：将程序打包成 macOS .app 应用
"""

import os
import sys
import subprocess
import shutil

def create_spec_file():
    """创建 PyInstaller spec 文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('core', 'core'),
        ('gui', 'gui'),
        ('config.yaml.example', '.'),
        ('requirements.txt', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'qrcode',
        'PIL',
        'yaml',
        'sqlite3',
        'core.config',
        'core.constants',
        'core.logger',
        'core.state_db',
        'core.icloud_worker',
        'core.nas_detector',
        'core.dedup',
        'core.qrcode_auth',
        'gui.modern_style',
        'gui.welcome_page',
        'gui.download_page',
        'gui.report_page',
        'gui.main_window',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='iCloud照片迁移助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='iCloud照片迁移助手',
)

app = BUNDLE(
    coll,
    name='iCloud照片迁移助手.app',
    icon=None,
    bundle_identifier='com.icloud.migrator',
    info_plist={
        'CFBundleName': 'iCloud照片迁移助手',
        'CFBundleDisplayName': 'iCloud照片迁移助手',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)
'''
    
    with open('iCloud照片迁移助手.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Spec 文件创建完成")

def build_app():
    """构建 .app 应用"""
    print("\n🔨 开始构建应用...")
    
    # 使用 spec 文件构建
    cmd = [
        'python3', '-m', 'PyInstaller',
        '--noconfirm',
        '--clean',
        'iCloud照片迁移助手.spec'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 应用构建成功")
            return True
        else:
            print(f"❌ 构建失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_dmg():
    """创建 DMG 安装包"""
    print("\n📦 创建 DMG 安装包...")
    
    app_path = 'dist/iCloud照片迁移助手.app'
    dmg_path = 'dist/iCloud照片迁移助手.dmg'
    
    if not os.path.exists(app_path):
        print(f"❌ 应用不存在: {app_path}")
        return False
    
    # 删除已存在的 DMG
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    
    # 创建 DMG
    cmd = [
        'hdiutil', 'create',
        '-volname', 'iCloud照片迁移助手',
        '-srcfolder', app_path,
        '-ov',
        '-format', 'UDZO',
        dmg_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ DMG 创建成功: {dmg_path}")
            return True
        else:
            print(f"❌ DMG 创建失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ DMG 创建失败: {e}")
        return False

def create_zip():
    """创建 ZIP 压缩包"""
    print("\n📦 创建 ZIP 压缩包...")
    
    app_path = 'dist/iCloud照片迁移助手.app'
    zip_path = 'dist/iCloud照片迁移助手.zip'
    
    if not os.path.exists(app_path):
        print(f"❌ 应用不存在: {app_path}")
        return False
    
    # 删除已存在的 ZIP
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    # 创建 ZIP
    cmd = [
        'ditto',
        '-c', '-k', '--sequesterRsrc', '--keepParent',
        app_path,
        zip_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ ZIP 创建成功: {zip_path}")
            return True
        else:
            print(f"❌ ZIP 创建失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ZIP 创建失败: {e}")
        return False

def main():
    """主函数"""
    print("="*60)
    print("📦 iCloud 照片迁移助手 - 打包工具")
    print("="*60)
    
    # 1. 创建 spec 文件
    create_spec_file()
    
    # 2. 构建应用
    if not build_app():
        print("\n❌ 打包失败")
        return 1
    
    # 3. 创建 DMG
    create_dmg()
    
    # 4. 创建 ZIP
    create_zip()
    
    print("\n" + "="*60)
    print("✅ 打包完成！")
    print("="*60)
    print("\n输出文件:")
    print("  📁 dist/iCloud照片迁移助手.app")
    print("  💿 dist/iCloud照片迁移助手.dmg")
    print("  📦 dist/iCloud照片迁移助手.zip")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
