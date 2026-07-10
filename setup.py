"""
py2app setup script for iCloud 照片迁移助手
"""

from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('', ['config.yaml.example']),
    ('', ['requirements.txt']),
    ('', ['README_如何打开.txt']),
    ('', ['SOP_使用指南.md']),
    ('core', [
        'core/__init__.py',
        'core/config.py',
        'core/constants.py',
        'core/logger.py',
        'core/state_db.py',
        'core/icloud_worker.py',
        'core/nas_detector.py',
        'core/dedup.py',
        'core/qrcode_auth.py',
    ]),
    ('gui', [
        'gui/__init__.py',
        'gui/modern_style.py',
        'gui/welcome_page.py',
        'gui/download_page.py',
        'gui/report_page.py',
        'gui/main_window.py',
    ]),
]

OPTIONS = {
    'argv_emulation': True,
    'packages': [
        'PySide6',
        'qrcode',
        'PIL',
        'yaml',
    ],
    'includes': [
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
    'excludes': [
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    'iconfile': None,
    'plist': {
        'CFBundleName': 'iCloud照片迁移助手',
        'CFBundleDisplayName': 'iCloud照片迁移助手',
        'CFBundleVersion': '2.0.0',
        'CFBundleShortVersionString': '2.0.0',
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
