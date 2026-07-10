"""
iCloud 下载工作线程
支持：多线程下载、断点续传、网络异常处理、磁盘空间检查
"""

import os
import re
import subprocess
import time
from datetime import datetime
from PySide6.QtCore import QThread, Signal

from core.logger import get_logger
from core.constants import (
    DEFAULT_THREADS_NUM, DEFAULT_MAX_RETRIES,
    RETRY_BASE_DELAY, RETRY_MAX_DELAY, MIN_DISK_SPACE_GB,
    BYTES_PER_GB, PROCESS_TIMEOUT, RETRYABLE_ERRORS, FATAL_ERRORS,
    ERROR_MESSAGES, SIZE_UNITS
)


class DiskSpaceChecker:
    """磁盘空间检查器"""
    
    @staticmethod
    def get_free_space(path: str) -> int:
        """获取路径所在磁盘的剩余空间（字节）"""
        try:
            stat = os.statvfs(path)
            return stat.f_bavail * stat.f_frsize
        except OSError as e:
            get_logger().error(f"获取磁盘空间失败: {e}")
            return 0
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in SIZE_UNITS:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    @staticmethod
    def check_space_before_download(target_path: str, estimated_size: int = 0) -> tuple:
        """下载前检查磁盘空间"""
        free_space = DiskSpaceChecker.get_free_space(target_path)
        min_required = max(estimated_size, MIN_DISK_SPACE_GB * BYTES_PER_GB)
        
        if free_space < min_required:
            return False, {
                "free": DiskSpaceChecker.format_size(free_space),
                "required": DiskSpaceChecker.format_size(min_required),
                "path": target_path
            }
        
        return True, {
            "free": DiskSpaceChecker.format_size(free_space),
            "path": target_path
        }


class NetworkRetryHandler:
    """网络重试处理器"""
    
    @staticmethod
    def is_retryable_error(error_msg: str) -> tuple:
        """判断是否可重试"""
        error_lower = error_msg.lower()
        
        for pattern in FATAL_ERRORS:
            if pattern.lower() in error_lower:
                return False, "fatal"
        
        for pattern in RETRYABLE_ERRORS:
            if pattern.lower() in error_lower:
                return True, "retryable"
        
        return True, "unknown"
    
    @staticmethod
    def get_retry_delay(attempt: int) -> int:
        """获取重试延迟（指数退避）"""
        return min(RETRY_BASE_DELAY ** attempt, RETRY_MAX_DELAY)
    
    @staticmethod
    def get_friendly_error(error_msg: str) -> str:
        """获取友好的错误提示"""
        for key, friendly_msg in ERROR_MESSAGES.items():
            if key.lower() in error_msg.lower():
                return friendly_msg
        return f"认证失败: {error_msg[:100]}..."


class ICloudWorker(QThread):
    """iCloud 下载工作线程"""
    
    # 信号定义
    progress = Signal(int, int, str)
    log_message = Signal(str)
    error_occurred = Signal(str)
    finished_signal = Signal(dict)
    disk_space_warning = Signal(str)
    retry_attempt = Signal(int, int, str)
    
    def __init__(self, config: dict, nas_path: str, db=None, parent=None):
        super().__init__(parent)
        self.config = config
        self.nas_path = nas_path
        self.logger = get_logger()
        self._paused = False
        self._stopped = False
        self._process = None
        
        # 断点续传
        self.db = db
        
        # 统计信息
        self.stats = {
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
            "duplicates": 0,
            "total": 0,
            "retries": 0,
            "start_time": None,
            "end_time": None
        }
        
        # 配置
        self.max_retries = config.get("max_retries", DEFAULT_MAX_RETRIES)
        self.current_retry = 0
        self.threads_num = config.get("threads_num", DEFAULT_THREADS_NUM)
    
    def run(self):
        """线程主函数"""
        self.stats["start_time"] = datetime.now()
        
        try:
            self._log_info("=" * 50)
            self._log_info(f"开始迁移: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self._log_info(f"目标路径: {self.nas_path}")
            self._log_info(f"并发线程数: {self.threads_num}")
            self._log_info("=" * 50)
            
            # 1. 检查磁盘空间
            self._check_disk_space()
            
            # 2. 构建命令
            cmd = self._build_command()
            self._log_info(f"执行命令: icloudpd ...")
            
            # 3. 执行下载（带重试）
            self._execute_with_retry(cmd)
            
        except subprocess.CalledProcessError as e:
            self.logger.exception("下载进程异常")
            self.error_occurred.emit(f"下载进程异常: {e.stderr or str(e)}")
            self.finished_signal.emit({"status": "error", "error": str(e)})
        except FileNotFoundError as e:
            self.logger.exception("文件未找到")
            self.error_occurred.emit(f"文件未找到: {str(e)}")
            self.finished_signal.emit({"status": "error", "error": str(e)})
        except OSError as e:
            self.logger.exception("系统错误")
            self.error_occurred.emit(f"系统错误: {str(e)}")
            self.finished_signal.emit({"status": "error", "error": str(e)})
        finally:
            self.stats["end_time"] = datetime.now()
    
    def _log_info(self, message: str):
        """同时输出到日志和UI"""
        self.logger.info(message)
        self.log_message.emit(message)
    
    def _log_warning(self, message: str):
        """同时输出到日志和UI"""
        self.logger.warning(message)
        self.log_message.emit(f"⚠️ {message}")
    
    def _log_error(self, message: str):
        """同时输出到日志和UI"""
        self.logger.error(message)
        self.log_message.emit(f"❌ {message}")
    
    def _check_disk_space(self):
        """检查磁盘空间"""
        self._log_info("检查磁盘空间...")
        
        success, info = DiskSpaceChecker.check_space_before_download(self.nas_path)
        
        if success:
            self._log_info(f"✅ 磁盘空间充足: {info['free']}")
        else:
            warning_msg = f"磁盘空间不足! 剩余: {info['free']}, 需要: {info['required']}"
            self._log_warning(warning_msg)
            self.disk_space_warning.emit(warning_msg)
    
    def _build_command(self) -> list:
        """构建 icloudpd 命令"""
        cmd = [
            "icloudpd",
            "--username", self.config.get("apple_id", ""),
            "--directory", self.nas_path,
            "--cookie-directory", self.config.get("cookie_dir", "./cookies"),
            "--folder-format", self.config.get("folder_format", "%Y/%Y-%m/%Y-%d"),
            "--threads-num", str(self.threads_num),
            "--no-progress-bar",
            "--set-exif-datetime",
        ]
        
        if self.config.get("only_new", True):
            cmd.append("--only-new")
        
        if not self.config.get("download_photos", True):
            cmd.append("--videos-only")
        elif not self.config.get("download_videos", True):
            cmd.append("--photos-only")
        
        if self.config.get("skip_live_photos", False):
            cmd.append("--skip-live-photos")
        
        return cmd
    
    def _execute_with_retry(self, cmd: list):
        """执行命令（带重试机制）"""
        while self.current_retry <= self.max_retries:
            if self._stopped:
                self._log_info("下载已停止")
                break
            
            try:
                self._execute_download(cmd)
                break
                
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr or str(e)
                is_retryable, error_type = NetworkRetryHandler.is_retryable_error(error_msg)
                
                if is_retryable and self.current_retry < self.max_retries:
                    self.current_retry += 1
                    delay = NetworkRetryHandler.get_retry_delay(self.current_retry)
                    
                    self._log_warning(f"下载失败: {error_msg[:100]}...")
                    self._log_info(f"🔄 将在 {delay} 秒后重试 ({self.current_retry}/{self.max_retries})")
                    
                    self.retry_attempt.emit(self.current_retry, self.max_retries, str(delay))
                    time.sleep(delay)
                else:
                    if error_type == "fatal":
                        self._log_error(f"致命错误（无法重试）: {error_msg}")
                    else:
                        self._log_error(f"达到最大重试次数 ({self.max_retries})")
                    raise
                    
            except (OSError, FileNotFoundError) as e:
                self.logger.exception("系统错误")
                raise
    
    def _execute_download(self, cmd: list):
        """执行下载"""
        self._log_info("启动下载进程...")
        
        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        for line in iter(self._process.stdout.readline, ''):
            if self._stopped:
                self._process.terminate()
                break
            
            while self._paused and not self._stopped:
                self.msleep(100)
            
            line = line.strip()
            if line:
                self._parse_output(line)
        
        self._process.wait()
        
        if self._process.returncode != 0:
            stderr = self._process.stderr.read()
            raise subprocess.CalledProcessError(
                self._process.returncode, cmd, stderr=stderr
            )
        
        stats = self._collect_stats()
        
        if self._stopped:
            stats["status"] = "stopped"
            self._log_info("迁移已停止")
        else:
            stats["status"] = "completed"
            self._log_info("迁移完成!")
        
        self.finished_signal.emit(stats)
    
    def _parse_output(self, line: str):
        """解析 icloudpd 输出"""
        self.log_message.emit(line)
        
        if "Downloading" in line or "downloading" in line:
            self.stats["downloaded"] += 1
            filename = line.split("/")[-1] if "/" in line else line
            
            self.progress.emit(
                self.stats["downloaded"],
                self.stats["total"],
                f"下载中: {filename}"
            )
            
            # 记录已下载文件
            if self.db:
                try:
                    self.db.add_downloaded_file(
                        f"file_{self.stats['downloaded']}",
                        filename,
                        self.nas_path
                    )
                except (OSError, RuntimeError) as e:
                    self.logger.error(f"记录已下载文件失败: {e}")
        
        elif "Skipping" in line or "skipping" in line:
            self.stats["skipped"] += 1
        
        elif "Error" in line or "error" in line:
            self.stats["failed"] += 1
            self.error_occurred.emit(line)
        
        total_match = re.search(r"(\d+)\s+(?:photos?|videos?|items?)", line, re.IGNORECASE)
        if total_match:
            self.stats["total"] = int(total_match.group(1))
            self.progress.emit(0, self.stats["total"], "准备开始下载...")
    
    def _collect_stats(self) -> dict:
        """收集统计信息"""
        stats = self.stats.copy()
        
        if stats["start_time"] and stats["end_time"]:
            duration = stats["end_time"] - stats["start_time"]
            stats["duration_seconds"] = duration.total_seconds()
            stats["duration_str"] = str(duration).split('.')[0]
        
        stats["total_retries"] = self.current_retry
        
        self.logger.info(f"统计信息: 下载={stats['downloaded']}, 跳过={stats['skipped']}, "
                        f"失败={stats['failed']}, 重试={stats['total_retries']}")
        
        return stats
    
    def pause(self):
        """暂停下载"""
        self._paused = True
        self._log_info("下载已暂停")
    
    def resume(self):
        """继续下载"""
        self._paused = False
        self._log_info("下载已继续")
    
    def stop(self):
        """停止下载"""
        self._stopped = True
        if self._process:
            self._process.terminate()
        self.logger.info("正在停止下载...")
    
    @property
    def is_paused(self) -> bool:
        return self._paused
    
    @property
    def is_stopped(self) -> bool:
        return self._stopped


class ICloudAuthenticator:
    """iCloud 认证工具"""
    
    @staticmethod
    def test_authentication(username: str, cookie_dir: str = "./cookies", max_retries: int = 3) -> tuple:
        """测试 iCloud 认证"""
        logger = get_logger()
        
        for attempt in range(max_retries):
            try:
                os.makedirs(cookie_dir, exist_ok=True)
                
                cmd = [
                    "icloudpd",
                    "--username", username,
                    "--cookie-directory", cookie_dir,
                    "--list-libraries",
                ]
                
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=PROCESS_TIMEOUT
                )
                
                if result.returncode == 0:
                    total = ICloudAuthenticator._parse_total_assets(result.stdout)
                    logger.info(f"认证成功，资源总数: {total}")
                    return True, "认证成功", total
                else:
                    error_msg = result.stderr or "认证失败"
                    friendly_msg = NetworkRetryHandler.get_friendly_error(error_msg)
                    
                    is_retryable, _ = NetworkRetryHandler.is_retryable_error(error_msg)
                    
                    if is_retryable and attempt < max_retries - 1:
                        delay = NetworkRetryHandler.get_retry_delay(attempt)
                        logger.warning(f"认证失败，{delay}秒后重试: {friendly_msg}")
                        time.sleep(delay)
                        continue
                    
                    logger.error(f"认证失败: {friendly_msg}")
                    return False, friendly_msg, 0
                    
            except subprocess.TimeoutExpired:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                logger.error("认证超时")
                return False, "认证超时，请检查网络连接", 0
                
            except FileNotFoundError:
                logger.error("icloudpd 未安装")
                return False, "icloudpd 未安装，请运行: pip install icloudpd", 0
                
            except OSError as e:
                logger.exception("认证异常")
                return False, NetworkRetryHandler.get_friendly_error(str(e)), 0
        
        return False, "认证失败，已达到最大重试次数", 0
    
    @staticmethod
    def _parse_total_assets(output: str) -> int:
        """解析资源总数"""
        patterns = [
            r"(\d+)\s+photos?",
            r"(\d+)\s+videos?",
            r"(\d+)\s+items?",
            r"Total:\s*(\d+)",
            r"Found\s+(\d+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return 0
