"""
主窗口模块
集成所有功能，提供完整的用户界面
"""

import yaml
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QStackedWidget,
    QMessageBox, QMenuBar, QStatusBar, QFrame
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QAction

from gui.welcome_page import WelcomePage
from gui.download_page import DownloadPage
from gui.report_page import ReportPage
from gui.modern_style import ModernStyle
from core.icloud_worker import ICloudWorker, DiskSpaceChecker
from core.state_db import StateDB
from core.logger import get_logger


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        self.logger = get_logger()
        self.logger.info("初始化主窗口")
        
        self.setWindowTitle("iCloud 照片迁移助手")
        self.setMinimumSize(1000, 700)
        
        # 初始化数据库
        self.db = StateDB("migration_state.db")
        
        # 加载配置
        self.config = self._load_config()
        
        # 下载工作线程
        self.worker = None
        self.current_run_id = None
        
        self._init_ui()
        self._load_previous_state()
        
        self.logger.info("主窗口初始化完成")
    
    def _init_ui(self):
        """初始化界面"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {ModernStyle.COLORS['bg_secondary']};
            }}
            QMenuBar {{
                background: {ModernStyle.COLORS['bg_primary']};
                border-bottom: 1px solid {ModernStyle.COLORS['border_light']};
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 8px 12px;
                border-radius: {ModernStyle.BORDER_RADIUS['sm']}px;
            }}
            QMenuBar::item:selected {{
                background: {ModernStyle.COLORS['bg_secondary']};
            }}
            QStatusBar {{
                background: {ModernStyle.COLORS['bg_primary']};
                border-top: 1px solid {ModernStyle.COLORS['border_light']};
                padding: 4px;
                font-size: {ModernStyle.FONT_SIZES['body_small']}px;
                color: {ModernStyle.COLORS['text_tertiary']};
            }}
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 页面堆栈
        self.page_stack = QStackedWidget()
        layout.addWidget(self.page_stack)
        
        # 创建页面
        self.welcome_page = WelcomePage()
        self.download_page = DownloadPage()
        self.report_page = ReportPage()
        
        # 添加到堆栈
        self.page_stack.addWidget(self.welcome_page)
        self.page_stack.addWidget(self.download_page)
        self.page_stack.addWidget(self.report_page)
        
        # 连接信号
        self._connect_signals()
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
        # 菜单栏
        self._create_menu_bar()
        
        # 显示欢迎页面
        self.page_stack.setCurrentWidget(self.welcome_page)
        
        self.logger.info("界面初始化完成")
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("文件")
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Cmd+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_signals(self):
        """连接信号"""
        # 欢迎页面信号
        self.welcome_page.start_migration.connect(self._on_start_migration)
        
        # 下载页面信号
        self.download_page.pause_clicked.connect(self._on_pause)
        self.download_page.resume_clicked.connect(self._on_resume)
        self.download_page.stop_clicked.connect(self._on_stop)
        
        # 报告页面信号
        self.report_page.close_clicked.connect(self.close)
        self.report_page.view_failed_clicked.connect(self._on_view_failed)
        
        self.logger.info("信号连接完成")
    
    def _load_config(self):
        """加载配置文件"""
        config_path = Path("config.yaml")
        
        default_config = {
            "apple_id": "",
            "nas_path": "",
            "cookie_dir": "./cookies",
            "folder_format": "%Y/%Y-%m/%Y-%d",
            "threads_num": 3,
            "only_new": True,
            "download_photos": True,
            "download_videos": True,
            "skip_live_photos": False,
            "max_retries": 3,
        }
        
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    saved_config = yaml.safe_load(f)
                    if saved_config:
                        default_config.update(saved_config)
                self.logger.info("配置文件加载成功")
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {e}")
        
        return default_config
    
    def _save_config(self):
        """保存配置文件"""
        config_path = Path("config.yaml")
        
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            self.logger.info("配置文件保存成功")
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
    
    def _load_previous_state(self):
        """加载之前的状态（支持断点续传）"""
        resume_info = self.db.get_resume_info()
        
        if resume_info["can_resume"]:
            self.logger.info(f"发现未完成的迁移: {resume_info}")
            
            reply = QMessageBox.question(
                self,
                "发现未完成的迁移",
                f"检测到上次迁移未完成（已完成 {resume_info['downloaded']}/{resume_info['total']}）\n\n是否继续？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self._resume_migration(resume_info["run_id"])
    
    def _on_start_migration(self):
        """开始迁移"""
        welcome_config = self.welcome_page.get_config()
        self.config["apple_id"] = welcome_config["apple_id"]
        self.config["nas_path"] = welcome_config["nas_path"]
        
        self._save_config()
        
        self.page_stack.setCurrentWidget(self.download_page)
        
        self.download_page.set_target_path(self.config["nas_path"])
        self.download_page.start_timer()
        
        # 创建数据库记录
        self.current_run_id = self.db.start_run(
            welcome_config.get("total_assets", 0)
        )
        
        self.logger.info(f"开始迁移: apple_id={self.config['apple_id']}, nas_path={self.config['nas_path']}")
        
        self._start_download()
    
    def _start_download(self):
        """启动下载"""
        self.worker = ICloudWorker(
            self.config, 
            self.config["nas_path"],
            db=self.db
        )
        
        # 连接信号
        self.worker.progress.connect(self._on_progress)
        self.worker.log_message.connect(self._on_log_message)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.disk_space_warning.connect(self._on_disk_space_warning)
        self.worker.retry_attempt.connect(self._on_retry_attempt)
        
        self.worker.start()
        
        self.status_bar.showMessage("迁移进行中...")
        self.logger.info("下载线程已启动")
    
    def _on_progress(self, downloaded, total, message):
        """更新进度"""
        self.download_page.update_progress(downloaded, total, message)
        
        if self.current_run_id:
            self.db.update_run(self.current_run_id, downloaded=downloaded)
    
    def _on_log_message(self, message):
        """日志消息"""
        self.download_page.add_log(message)
    
    def _on_error(self, error_message):
        """错误处理"""
        self.download_page.add_log(f"❌ 错误: {error_message}")
        self.status_bar.showMessage(f"错误: {error_message}")
        self.logger.error(f"下载错误: {error_message}")
    
    def _on_disk_space_warning(self, warning_msg):
        """磁盘空间警告"""
        self.download_page.show_disk_space_warning(warning_msg)
        self.download_page.add_log(f"⚠️ {warning_msg}")
        self.logger.warning(f"磁盘空间警告: {warning_msg}")
    
    def _on_retry_attempt(self, current, max_retries, delay):
        """重试尝试"""
        self.download_page.show_retry_info(current, max_retries, delay)
        self.download_page.add_log(f"🔄 重试 {current}/{max_retries}，等待 {delay} 秒...")
        self.logger.info(f"重试 {current}/{max_retries}，等待 {delay} 秒")
    
    def _on_finished(self, stats):
        """下载完成"""
        if self.current_run_id:
            if stats.get("status") == "completed":
                self.db.complete_run(self.current_run_id, stats)
            elif stats.get("status") == "stopped":
                self.db.pause_run(self.current_run_id)
        
        self.page_stack.setCurrentWidget(self.report_page)
        
        stats["target_path"] = self.config["nas_path"]
        self.report_page.set_stats(stats)
        
        if "duration_seconds" in stats:
            self.report_page.set_duration(stats["duration_seconds"])
        
        if stats.get("status") == "completed":
            self.status_bar.showMessage("迁移完成")
            self.download_page.set_completed()
            self.logger.info("迁移完成")
        elif stats.get("status") == "stopped":
            self.status_bar.showMessage("迁移已停止")
            self.logger.info("迁移已停止")
        else:
            self.status_bar.showMessage("迁移异常结束")
            self.download_page.set_error(stats.get("error", "未知错误"))
            self.logger.error(f"迁移异常结束: {stats.get('error')}")
    
    def _on_pause(self):
        """暂停下载"""
        if self.worker:
            self.worker.pause()
            self.download_page.set_paused(True)
            self.status_bar.showMessage("已暂停")
            self.logger.info("下载已暂停")
    
    def _on_resume(self):
        """继续下载"""
        if self.worker:
            self.worker.resume()
            self.download_page.set_paused(False)
            self.status_bar.showMessage("继续中...")
            self.logger.info("下载已继续")
    
    def _on_stop(self):
        """停止下载"""
        reply = QMessageBox.question(
            self,
            "确认停止",
            "确定要停止迁移吗？已下载的文件将保留。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.worker:
                self.worker.stop()
            self.status_bar.showMessage("正在停止...")
            self.logger.info("正在停止下载...")
    
    def _on_view_failed(self):
        """查看失败文件"""
        failed_files = self.db.get_failed_files()
        
        if failed_files:
            from gui.report_page import FailedFilesDialog
            dialog = FailedFilesDialog(failed_files, self)
            dialog.show()
        else:
            QMessageBox.information(self, "提示", "没有失败的文件")
    
    def _resume_migration(self, run_id):
        """恢复迁移"""
        saved_configs = self.db.get_all_configs()
        
        if "apple_id" in saved_configs:
            self.config["apple_id"] = saved_configs["apple_id"]
        if "nas_path" in saved_configs:
            self.config["nas_path"] = saved_configs["nas_path"]
        
        self.page_stack.setCurrentWidget(self.download_page)
        self.download_page.set_target_path(self.config["nas_path"])
        
        self.current_run_id = run_id
        
        self.download_page.add_log("📥 恢复中断的迁移...")
        self.logger.info(f"恢复迁移: run_id={run_id}")
        
        self._start_download()
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 iCloud 照片迁移助手",
            """
            <h2>iCloud 照片迁移助手</h2>
            <p><b>版本:</b> 2.0.0</p>
            <p><b>描述:</b> 将 iCloud 照片和视频安全迁移到您的 NAS</p>
            <p><b>特性:</b></p>
            <ul>
                <li>多线程下载 - 速度提升 3-5 倍</li>
                <li>断点续传 - 中断后可继续</li>
                <li>自动重试 - 网络异常自动恢复</li>
                <li>磁盘空间检查 - 避免下载失败</li>
                <li>友好错误提示 - 降低使用门槛</li>
                <li>日志系统 - 便于问题排查</li>
            </ul>
            """
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        self.logger.info("正在关闭应用...")
        
        self._save_config()
        
        for key, value in self.config.items():
            self.db.save_config(key, str(value))
        
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "迁移正在进行中，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            
            self.worker.stop()
            self.worker.wait(3000)
        
        self.db.close()
        self.logger.info("应用已关闭")
        
        event.accept()
