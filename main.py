"""
iCloud 照片迁移助手 - 主入口文件
版本: 2.0.0
"""

import sys
import os
from pathlib import Path

# 确保当前目录在 Python 路径中
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from gui.main_window import MainWindow
from core.logger import get_logger
from core.config import ConfigManager


def main():
    """主函数"""
    # 设置工作目录
    os.chdir(current_dir)
    
    # 初始化日志
    logger = get_logger()
    logger.info("=" * 50)
    logger.info("iCloud 照片迁移助手启动")
    logger.info("=" * 50)
    
    # 加载配置
    config_manager = ConfigManager()
    config = config_manager.load()
    
    if not config_manager.validate():
        for error in config_manager.get_errors():
            logger.error(f"配置错误: {error}")
        for warning in config_manager.get_warnings():
            logger.warning(f"配置警告: {warning}")
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用信息
    app.setApplicationName("iCloud 照片迁移助手")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("iCloud Migrator")
    
    # 设置默认字体
    font = QFont()
    font.setPointSize(13)
    app.setFont(font)
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    logger.info("主窗口已显示")
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
