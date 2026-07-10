"""
下载进度页面
支持：实时进度、重试显示、磁盘空间警告、日志系统
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QProgressBar, QTextEdit, QGroupBox,
    QGridLayout, QFrame, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from gui.modern_style import ModernStyle
from core.logger import get_logger


class DownloadPage(QWidget):
    """下载进度页面"""
    
    # 信号
    pause_clicked = Signal()
    resume_clicked = Signal()
    stop_clicked = Signal()
    view_log_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.start_time = None
        self._init_ui()
        self._reset_stats()
        self.logger.info("下载页面初始化完成")
    
    def _init_ui(self):
        """初始化界面"""
        self.setStyleSheet(f"background: {ModernStyle.COLORS['bg_secondary']};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING['xl'])
        layout.setContentsMargins(
            ModernStyle.SPACING['xxxl'], 
            ModernStyle.SPACING['xxl'],
            ModernStyle.SPACING['xxxl'], 
            ModernStyle.SPACING['xxl']
        )
        
        # 标题
        title_row = QHBoxLayout()
        title_icon = QLabel("⬇️")
        title_icon.setStyleSheet("background: transparent; border: none;")
        title_icon.setFont(QFont("", 24))
        
        title = QLabel("迁移进行中...")
        title.setStyleSheet(ModernStyle.get_title_style('title'))
        
        title_row.addWidget(title_icon)
        title_row.addWidget(title)
        title_row.addStretch()
        layout.addLayout(title_row)
        
        # 磁盘空间警告（默认隐藏）
        self.space_warning = QFrame()
        self.space_warning.setStyleSheet(f"""
            QFrame {{
                background: {ModernStyle.COLORS['warning']}20;
                border: 2px solid {ModernStyle.COLORS['warning']};
                border-radius: {ModernStyle.BORDER_RADIUS['md']}px;
                padding: 12px;
            }}
        """)
        warning_layout = QHBoxLayout(self.space_warning)
        warning_icon = QLabel("⚠️")
        warning_icon.setStyleSheet("background: transparent; border: none;")
        self.warning_text = QLabel("磁盘空间不足警告")
        self.warning_text.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['warning']};
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        warning_layout.addWidget(warning_icon)
        warning_layout.addWidget(self.warning_text)
        self.space_warning.hide()
        layout.addWidget(self.space_warning)
        
        # 进度区域
        self._create_progress_section(layout)
        
        # 统计卡片
        self._create_stats_section(layout)
        
        # 重试信息
        self.retry_frame = QFrame()
        self.retry_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernStyle.COLORS['primary']}10;
                border: 1px solid {ModernStyle.COLORS['primary']}30;
                border-radius: {ModernStyle.BORDER_RADIUS['md']}px;
                padding: 12px;
            }}
        """)
        retry_layout = QHBoxLayout(self.retry_frame)
        retry_icon = QLabel("🔄")
        retry_icon.setStyleSheet("background: transparent; border: none;")
        self.retry_text = QLabel("重试信息")
        self.retry_text.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['primary']};
                background: transparent;
                border: none;
            }}
        """)
        retry_layout.addWidget(retry_icon)
        retry_layout.addWidget(self.retry_text)
        self.retry_frame.hide()
        layout.addWidget(self.retry_frame)
        
        # 控制按钮
        self._create_control_section(layout)
        
        # 日志区域
        self._create_log_section(layout)
    
    def _create_progress_section(self, parent_layout):
        """创建进度区域"""
        card = QFrame()
        card.setStyleSheet(ModernStyle.get_card_style())
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(ModernStyle.SPACING['lg'])
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(24)
        self.progress_bar.setStyleSheet(ModernStyle.get_progress_bar_style())
        self.progress_bar.setFormat("%p%")
        card_layout.addWidget(self.progress_bar)
        
        # 进度详情
        detail_layout = QHBoxLayout()
        
        self.progress_label = QLabel("0 / 0")
        self.progress_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['text_primary']};
                font-size: {ModernStyle.FONT_SIZES['title']}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.percent_label = QLabel("0%")
        self.percent_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['primary']};
                font-size: {ModernStyle.FONT_SIZES['title']}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        detail_layout.addWidget(self.progress_label)
        detail_layout.addWidget(self.percent_label)
        card_layout.addLayout(detail_layout)
        
        # 状态消息
        self.status_label = QLabel("准备开始...")
        self.status_label.setStyleSheet(ModernStyle.get_label_style('secondary'))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_label)
        
        # 预估时间
        self.eta_label = QLabel("")
        self.eta_label.setStyleSheet(ModernStyle.get_label_style('tertiary'))
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.eta_label)
        
        parent_layout.addWidget(card)
    
    def _create_stats_section(self, parent_layout):
        """创建统计卡片区域"""
        grid = QGridLayout()
        grid.setSpacing(ModernStyle.SPACING['md'])
        
        self.downloaded_card = self._create_stat_card("已下载", "0", ModernStyle.COLORS['success'])
        grid.addWidget(self.downloaded_card, 0, 0)
        
        self.skipped_card = self._create_stat_card("跳过", "0", ModernStyle.COLORS['warning'])
        grid.addWidget(self.skipped_card, 0, 1)
        
        self.failed_card = self._create_stat_card("失败", "0", ModernStyle.COLORS['error'])
        grid.addWidget(self.failed_card, 0, 2)
        
        self.duplicates_card = self._create_stat_card("重复", "0", ModernStyle.COLORS['purple'])
        grid.addWidget(self.duplicates_card, 0, 3)
        
        self.speed_card = self._create_stat_card("速度", "0 MB/s", ModernStyle.COLORS['primary'])
        grid.addWidget(self.speed_card, 1, 0)
        
        self.retries_card = self._create_stat_card("重试", "0", ModernStyle.COLORS['warning'])
        grid.addWidget(self.retries_card, 1, 1)
        
        self.elapsed_card = self._create_stat_card("已用时间", "00:00:00", ModernStyle.COLORS['text_tertiary'])
        grid.addWidget(self.elapsed_card, 1, 2)
        
        self.target_card = self._create_stat_card("目标", "N/A", ModernStyle.COLORS['text_tertiary'])
        grid.addWidget(self.target_card, 1, 3)
        
        parent_layout.addLayout(grid)
    
    def _create_stat_card(self, title, value, color):
        """创建统计卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {ModernStyle.COLORS['bg_card']};
                border: 1px solid {ModernStyle.COLORS['border_light']};
                border-radius: {ModernStyle.BORDER_RADIUS['lg']}px;
                padding: 16px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(ModernStyle.SPACING['xs'])
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['text_tertiary']};
                font-size: {ModernStyle.FONT_SIZES['caption']}px;
                background: transparent;
                border: none;
            }}
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {ModernStyle.FONT_SIZES['title']}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        card.value_label = value_label
        
        return card
    
    def _create_control_section(self, parent_layout):
        """创建控制按钮区域"""
        btn_container = QFrame()
        btn_container.setStyleSheet("background: transparent; border: none;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(ModernStyle.SPACING['md'])
        
        self.pause_btn = QPushButton("⏸️ 暂停")
        self.pause_btn.setStyleSheet(ModernStyle.get_button_style('warning', 'medium'))
        self.pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pause_btn.clicked.connect(self._on_pause_clicked)
        
        self.stop_btn = QPushButton("⏹️ 停止")
        self.stop_btn.setStyleSheet(ModernStyle.get_button_style('error', 'medium'))
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        
        self.log_btn = QPushButton("📋 查看完整日志")
        self.log_btn.setStyleSheet(ModernStyle.get_button_style('primary', 'medium'))
        self.log_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.log_btn.clicked.connect(self.view_log_clicked.emit)
        
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.log_btn)
        
        parent_layout.addWidget(btn_container)
    
    def _create_log_section(self, parent_layout):
        """创建日志区域"""
        card = QFrame()
        card.setStyleSheet(ModernStyle.get_card_style())
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(ModernStyle.SPACING['md'])
        
        title_row = QHBoxLayout()
        title_icon = QLabel("📜")
        title_icon.setStyleSheet("background: transparent; border: none;")
        title_icon.setFont(QFont("", 16))
        
        title_text = QLabel("最近日志")
        title_text.setStyleSheet(ModernStyle.get_label_style('primary', 'body'))
        
        title_row.addWidget(title_icon)
        title_row.addWidget(title_text)
        title_row.addStretch()
        card_layout.addLayout(title_row)
        
        self.log_text = QTextEdit()
        self.log_text.setFixedHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet(f"""
            QTextEdit {{
                background: {ModernStyle.COLORS['bg_secondary']};
                border: 1px solid {ModernStyle.COLORS['border_light']};
                border-radius: {ModernStyle.BORDER_RADIUS['md']}px;
                padding: 12px;
                font-family: 'SF Mono', 'Menlo', 'Monaco', 'Courier New', monospace;
                font-size: {ModernStyle.FONT_SIZES['caption']}px;
                color: {ModernStyle.COLORS['text_secondary']};
            }}
        """)
        card_layout.addWidget(self.log_text)
        
        parent_layout.addWidget(card)
    
    def _reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
            "duplicates": 0,
            "total": 0,
            "speed": 0,
            "elapsed": 0,
            "retries": 0
        }
    
    def set_total(self, total):
        """设置总数"""
        self.stats["total"] = total
        self.progress_bar.setMaximum(total)
        self.progress_label.setText(f"0 / {total}")
    
    def set_target_path(self, path):
        """设置目标路径"""
        self.target_card.value_label.setText(path)
    
    def show_disk_space_warning(self, message):
        """显示磁盘空间警告"""
        self.warning_text.setText(message)
        self.space_warning.show()
        self.logger.warning(f"显示磁盘空间警告: {message}")
    
    def hide_disk_space_warning(self):
        """隐藏磁盘空间警告"""
        self.space_warning.hide()
    
    def show_retry_info(self, current, max_retries, delay):
        """显示重试信息"""
        self.retry_text.setText(f"重试中... ({current}/{max_retries}) - {delay}秒后重试")
        self.retry_frame.show()
        self.stats["retries"] = current
        self.retries_card.value_label.setText(str(current))
    
    def hide_retry_info(self):
        """隐藏重试信息"""
        self.retry_frame.hide()
    
    def update_progress(self, downloaded, total, message=""):
        """更新进度"""
        self.stats["downloaded"] = downloaded
        self.stats["total"] = total
        
        self.progress_bar.setValue(downloaded)
        self.progress_label.setText(f"{downloaded} / {total}")
        
        if total > 0:
            percent = int(downloaded / total * 100)
            self.percent_label.setText(f"{percent}%")
            
            # 计算预估时间
            if downloaded > 0 and self.start_time:
                elapsed = (datetime.now() - self.start_time).total_seconds()
                if elapsed > 0:
                    speed = downloaded / elapsed
                    remaining = (total - downloaded) / speed if speed > 0 else 0
                    
                    if remaining < 60:
                        eta_str = f"预计剩余: {int(remaining)}秒"
                    elif remaining < 3600:
                        eta_str = f"预计剩余: {int(remaining/60)}分钟"
                    else:
                        hours = int(remaining / 3600)
                        minutes = int((remaining % 3600) / 60)
                        eta_str = f"预计剩余: {hours}小时{minutes}分钟"
                    
                    self.eta_label.setText(eta_str)
        
        if message:
            self.status_label.setText(message)
        
        self.downloaded_card.value_label.setText(str(downloaded))
    
    def update_stats(self, **kwargs):
        """更新统计信息"""
        for key, value in kwargs.items():
            if key in self.stats:
                self.stats[key] = value
                
                if key == "skipped":
                    self.skipped_card.value_label.setText(str(value))
                elif key == "failed":
                    self.failed_card.value_label.setText(str(value))
                elif key == "duplicates":
                    self.duplicates_card.value_label.setText(str(value))
                elif key == "speed":
                    self.speed_card.value_label.setText(f"{value:.1f} MB/s")
                elif key == "retries":
                    self.retries_card.value_label.setText(str(value))
    
    def add_log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_timer(self):
        """启动计时器"""
        self.start_time = datetime.now()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_elapsed)
        self.timer.start(1000)
        self.logger.info("计时器已启动")
    
    def _update_elapsed(self):
        """更新已用时间"""
        if self.start_time:
            elapsed = datetime.now() - self.start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.elapsed_card.value_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.stats["elapsed"] = elapsed.total_seconds()
    
    def _on_pause_clicked(self):
        """暂停按钮点击"""
        if self.pause_btn.text() == "⏸️ 暂停":
            self.pause_btn.setText("▶️ 继续")
            self.pause_clicked.emit()
            self.logger.info("用户点击暂停")
        else:
            self.pause_btn.setText("⏸️ 暂停")
            self.resume_clicked.emit()
            self.logger.info("用户点击继续")
    
    def _on_stop_clicked(self):
        """停止按钮点击"""
        self.stop_clicked.emit()
        self.logger.info("用户点击停止")
    
    def set_paused(self, paused):
        """设置暂停状态"""
        if paused:
            self.pause_btn.setText("▶️ 继续")
            self.status_label.setText("⏸️ 已暂停")
            self.status_label.setStyleSheet(ModernStyle.get_label_style('warning'))
        else:
            self.pause_btn.setText("⏸️ 暂停")
            self.status_label.setText("▶️ 继续中...")
            self.status_label.setStyleSheet(ModernStyle.get_label_style('success'))
    
    def set_completed(self):
        """设置完成状态"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("✅ 迁移完成!")
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['success']};
                font-size: {ModernStyle.FONT_SIZES['body']}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        
        self.hide_retry_info()
        self.logger.info("下载页面已设置为完成状态")
    
    def set_error(self, error_message):
        """设置错误状态"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        self.status_label.setText(f"❌ 错误: {error_message}")
        self.status_label.setStyleSheet(ModernStyle.get_label_style('error'))
        self.logger.error(f"下载页面显示错误: {error_message}")
    
    def get_stats(self):
        """获取统计信息"""
        return self.stats.copy()
