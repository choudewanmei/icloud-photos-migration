"""
配置管理模块
提供配置验证、默认值和模板
"""

import os
import yaml
from datetime import datetime
from typing import Dict, Any, Optional, List

from core.logger import get_logger
from core.constants import (
    DEFAULT_THREADS_NUM, MIN_THREADS_NUM, MAX_THREADS_NUM,
    DEFAULT_MAX_RETRIES, MAX_RETRIES_LIMIT, DEFAULT_FOLDER_FORMAT,
    DEFAULT_COOKIE_DIR
)


# 默认配置
DEFAULT_CONFIG = {
    "apple_id": "",
    "cookie_dir": DEFAULT_COOKIE_DIR,
    "nas_path": "",
    "folder_format": DEFAULT_FOLDER_FORMAT,
    "threads_num": DEFAULT_THREADS_NUM,
    "only_new": True,
    "download_photos": True,
    "download_videos": True,
    "skip_live_photos": False,
    "max_retries": DEFAULT_MAX_RETRIES,
    "log_level": "INFO",
    "log_to_file": True,
}

# 配置验证规则
VALIDATION_RULES = {
    "apple_id": {
        "type": str,
        "required": False,
        "description": "Apple ID 邮箱"
    },
    "nas_path": {
        "type": str,
        "required": True,
        "description": "NAS 挂载路径"
    },
    "threads_num": {
        "type": int,
        "min": MIN_THREADS_NUM,
        "max": 20,
        "description": "下载线程数"
    },
    "max_retries": {
        "type": int,
        "min": 0,
        "max": MAX_RETRIES_LIMIT,
        "description": "最大重试次数"
    },
    "folder_format": {
        "type": str,
        "description": "文件夹格式"
    },
}


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.logger = get_logger()
        self.config = DEFAULT_CONFIG.copy()
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            self.warnings.append(f"配置文件不存在: {self.config_path}，使用默认配置")
            self.logger.warning(f"配置文件不存在: {self.config_path}")
            return self.config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                user_config = yaml.safe_load(f)
                
            if user_config:
                self.config.update(user_config)
                self.logger.info(f"配置文件加载成功: {self.config_path}")
                
        except yaml.YAMLError as e:
            self.errors.append(f"配置文件格式错误: {e}")
            self.logger.error(f"配置文件格式错误: {e}")
        except OSError as e:
            self.errors.append(f"加载配置文件失败: {e}")
            self.logger.error(f"加载配置文件失败: {e}")
        
        return self.config
    
    def save(self) -> bool:
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            self.logger.info(f"配置文件保存成功: {self.config_path}")
            return True
        except OSError as e:
            self.errors.append(f"保存配置文件失败: {e}")
            self.logger.error(f"保存配置文件失败: {e}")
            return False
    
    def validate(self) -> bool:
        """验证配置"""
        self.errors = []
        self.warnings = []
        
        for key, rule in VALIDATION_RULES.items():
            value = self.config.get(key)
            
            # 检查必填项
            if rule.get("required") and not value:
                self.errors.append(f"缺少必填配置: {key} ({rule.get('description', '')})")
                continue
            
            if value is None:
                continue
            
            # 检查类型
            expected_type = rule.get("type")
            if expected_type and not isinstance(value, expected_type):
                self.errors.append(f"配置类型错误: {key} 应为 {expected_type.__name__}，实际为 {type(value).__name__}")
                continue
            
            # 检查范围
            if isinstance(value, (int, float)):
                min_val = rule.get("min")
                max_val = rule.get("max")
                
                if min_val is not None and value < min_val:
                    self.errors.append(f"配置值过小: {key} = {value}，最小值为 {min_val}")
                
                if max_val is not None and value > max_val:
                    self.errors.append(f"配置值过大: {key} = {value}，最大值为 {max_val}")
        
        # 检查路径
        if self.config.get("nas_path"):
            nas_path = self.config["nas_path"]
            if not nas_path.startswith("/Volumes/"):
                self.warnings.append(f"NAS 路径建议以 /Volumes/ 开头: {nas_path}")
        
        return len(self.errors) == 0
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
    
    def get_errors(self) -> List[str]:
        """获取错误列表"""
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """获取警告列表"""
        return self.warnings
    
    def get_template(self) -> str:
        """获取配置模板"""
        template = "# iCloud 照片迁移助手配置文件\n"
        template += f"# 生成时间: {datetime.now()}\n\n"
        
        for key, value in DEFAULT_CONFIG.items():
            desc = VALIDATION_RULES.get(key, {}).get("description", "")
            if desc:
                template += f"# {desc}\n"
            template += f"{key}: {value}\n\n"
        
        return template
