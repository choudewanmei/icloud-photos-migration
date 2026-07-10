"""
NAS 挂载检测模块
后台线程持续检测 NAS 是否已挂载
"""

import os
import time
from PySide6.QtCore import QThread, Signal


class NASDetector(QThread):
    """后台检测 NAS 是否已挂载"""
    
    nas_ready = Signal(str)   # NAS 路径就绪
    nas_lost = Signal()       # NAS 连接丢失
    status_update = Signal(str)  # 状态信息更新
    
    def __init__(self, mount_path, check_interval=5):
        super().__init__()
        self.mount_path = mount_path
        self.check_interval = check_interval
        self._running = True
        self._was_ready = False
    
    def run(self):
        """线程主循环"""
        while self._running:
            is_ready = self._check_nas()
            
            if is_ready and not self._was_ready:
                self.nas_ready.emit(self.mount_path)
                self.status_update.emit(f"✅ NAS 已连接: {self.mount_path}")
                self._was_ready = True
            elif not is_ready and self._was_ready:
                self.nas_lost.emit()
                self.status_update.emit("❌ NAS 连接已断开")
                self._was_ready = False
            elif not is_ready:
                self.status_update.emit(f"⏳ 等待 NAS 挂载: {self.mount_path}")
            
            self.msleep(self.check_interval * 1000)
    
    def _check_nas(self):
        """检测 NAS 是否可访问"""
        try:
            # 检查路径是否存在
            if not os.path.isdir(self.mount_path):
                return False
            
            # 检查路径是否可写
            test_file = os.path.join(self.mount_path, ".migration_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            return True
        except (OSError, PermissionError):
            return False
    
    def stop(self):
        """停止检测"""
        self._running = False
        self.wait()


class NASPathValidator:
    """NAS 路径验证工具"""
    
    @staticmethod
    def validate_path(path):
        """
        验证 NAS 路径是否有效
        返回: (is_valid, message)
        """
        if not path:
            return False, "路径不能为空"
        
        if not path.startswith("/Volumes/"):
            return False, "NAS 路径应以 /Volumes/ 开头"
        
        if not os.path.exists(path):
            return False, f"路径不存在: {path}"
        
        if not os.path.isdir(path):
            return False, f"路径不是目录: {path}"
        
        # 检查是否可写
        try:
            test_file = os.path.join(path, ".write_test")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            return True, "✅ 路径有效且可写"
        except (OSError, PermissionError):
            return False, "路径不可写，请检查权限"
    
    @staticmethod
    def get_volumes():
        """获取 /Volumes/ 下的所有挂载点"""
        volumes = []
        volumes_path = "/Volumes"
        
        if os.path.exists(volumes_path):
            for item in os.listdir(volumes_path):
                item_path = os.path.join(volumes_path, item)
                if os.path.isdir(item_path):
                    volumes.append(item_path)
        
        return volumes
