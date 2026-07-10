"""
日志系统模块
提供统一的日志管理和持久化存储
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime


class AppLogger:
    """应用日志管理器"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AppLogger._initialized:
            self._setup_logger()
            AppLogger._initialized = True
    
    def _setup_logger(self):
        """设置日志系统"""
        # 创建日志目录
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建主日志器
        self.logger = logging.getLogger("iCloudMigrator")
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        
        # 文件处理器（带轮转）
        log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """调试日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """错误日志"""
        self.logger.error(message)
    
    def critical(self, message):
        """严重错误日志"""
        self.logger.critical(message)
    
    def exception(self, message):
        """异常日志（包含堆栈）"""
        self.logger.exception(message)


# 全局日志实例
def get_logger():
    """获取日志实例"""
    return AppLogger()
