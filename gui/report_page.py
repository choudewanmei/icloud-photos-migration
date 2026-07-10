"""
完成报告页面 - 现代UI设计
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QGroupBox, QGridLayout, QFrame,
    QTextEdit, QFileDialog, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from gui.modern_style import ModernStyle


class ReportPage(QWidget):
    """完成报告页面 - 现代UI设计"""
    
    # 信号
    close_clicked = Signal()
    export_clicked = Signal()
    view_failed_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stats = {}
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        # 设置背景色
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
        self._create_header(layout)
        
        # 统计卡片区域
        self._create_stats_section(layout)
        
        # 详细信息
        self._create_detail_section(layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 操作按钮
        self._create_action_section(layout)
    
    def _create_header(self, layout):
        """创建标题区域"""
        header_frame = QFrame()
        header_frame.setStyleSheet("background: transparent; border: none;")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(ModernStyle.SPACING['md'])
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 图标
        icon_label = QLabel("✅")
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        header_layout.addWidget(icon_label)
        
        # 标题
        self.title_label = QLabel("迁移完成！")
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['success']};
                font-size: {ModernStyle.FONT_SIZES['title_large']}px;
                font-weight: 700;
                background: transparent;
                border: none;
            }}
        """)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.title_label)
        
        # 副标题
        self.subtitle_label = QLabel("所有照片和视频已成功迁移到 NAS")
        self.subtitle_label.setStyleSheet(ModernStyle.get_subtitle_style())
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.subtitle_label)
        
        layout.addWidget(header_frame)
    
    def _create_stats_section(self, parent_layout):
        """创建统计卡片区域"""
        grid = QGridLayout()
        grid.setSpacing(ModernStyle.SPACING['md'])
        
        # 统计卡片
        self.total_card = self._create_stat_card("总资源数", "0", ModernStyle.COLORS['primary'])
        grid.addWidget(self.total_card, 0, 0)
        
        self.downloaded_card = self._create_stat_card("成功下载", "0", ModernStyle.COLORS['success'])
        grid.addWidget(self.downloaded_card, 0, 1)
        
        self.skipped_card = self._create_stat_card("跳过(已存在)", "0", ModernStyle.COLORS['warning'])
        grid.addWidget(self.skipped_card, 0, 2)
        
        self.failed_card = self._create_stat_card("失败", "0", ModernStyle.COLORS['error'])
        grid.addWidget(self.failed_card, 1, 0)
        
        self.duplicates_card = self._create_stat_card("去重", "0", ModernStyle.COLORS['purple'])
        grid.addWidget(self.duplicates_card, 1, 1)
        
        self.duration_card = self._create_stat_card("总耗时", "00:00:00", ModernStyle.COLORS['text_tertiary'])
        grid.addWidget(self.duration_card, 1, 2)
        
        parent_layout.addLayout(grid)
    
    def _create_stat_card(self, title, value, color):
        """创建统计卡片"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {ModernStyle.COLORS['bg_card']};
                border: 1px solid {ModernStyle.COLORS['border_light']};
                border-radius: {ModernStyle.BORDER_RADIUS['lg']}px;
                padding: 20px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(ModernStyle.SPACING['sm'])
        
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['text_tertiary']};
                font-size: {ModernStyle.FONT_SIZES['body_small']}px;
                background: transparent;
                border: none;
            }}
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: {ModernStyle.FONT_SIZES['title_large']}px;
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
    
    def _create_detail_section(self, parent_layout):
        """创建详细信息区域"""
        card = QFrame()
        card.setStyleSheet(ModernStyle.get_card_style())
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(ModernStyle.SPACING['md'])
        
        # 标题
        title_row = QHBoxLayout()
        title_icon = QLabel("📊")
        title_icon.setStyleSheet("background: transparent; border: none;")
        title_icon.setFont(QFont("", 16))
        
        title_text = QLabel("迁移详情")
        title_text.setStyleSheet(ModernStyle.get_label_style('primary', 'body'))
        
        title_row.addWidget(title_icon)
        title_row.addWidget(title_text)
        title_row.addStretch()
        card_layout.addLayout(title_row)
        
        # 详细信息表格
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(2)
        self.detail_table.setHorizontalHeaderLabels(["项目", "值"])
        self.detail_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.detail_table.verticalHeader().setVisible(False)
        self.detail_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.detail_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.detail_table.setStyleSheet(ModernStyle.get_table_style())
        
        card_layout.addWidget(self.detail_table)
        parent_layout.addWidget(card)
    
    def _create_action_section(self, parent_layout):
        """创建操作按钮区域"""
        btn_container = QFrame()
        btn_container.setStyleSheet("background: transparent; border: none;")
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setSpacing(ModernStyle.SPACING['md'])
        
        # 查看失败列表按钮
        self.view_failed_btn = QPushButton("❌ 查看失败列表")
        self.view_failed_btn.setStyleSheet(ModernStyle.get_button_style('error', 'medium'))
        self.view_failed_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.view_failed_btn.clicked.connect(self.view_failed_clicked.emit)
        
        # 导出报告按钮
        self.export_btn = QPushButton("📤 导出报告")
        self.export_btn.setStyleSheet(ModernStyle.get_button_style('purple', 'medium'))
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self._on_export_clicked)
        
        # 关闭按钮
        self.close_btn = QPushButton("✖️ 关闭")
        self.close_btn.setStyleSheet(ModernStyle.get_button_style('primary', 'medium'))
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.close_clicked.emit)
        
        btn_layout.addWidget(self.view_failed_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self.export_btn)
        btn_layout.addWidget(self.close_btn)
        
        parent_layout.addWidget(btn_container)
    
    def set_stats(self, stats):
        """设置统计信息"""
        self.stats = stats
        
        total = stats.get("total", 0)
        downloaded = stats.get("downloaded", 0)
        skipped = stats.get("skipped", 0)
        failed = stats.get("failed", 0)
        duplicates = stats.get("duplicates", 0)
        
        self.total_card.value_label.setText(str(total))
        self.downloaded_card.value_label.setText(str(downloaded))
        self.skipped_card.value_label.setText(str(skipped))
        self.failed_card.value_label.setText(str(failed))
        self.duplicates_card.value_label.setText(str(duplicates))
        
        self.view_failed_btn.setEnabled(failed > 0)
        
        if failed > 0:
            self.title_label.setText("迁移完成（有失败）")
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {ModernStyle.COLORS['warning']};
                    font-size: {ModernStyle.FONT_SIZES['title_large']}px;
                    font-weight: 700;
                    background: transparent;
                    border: none;
                }}
            """)
            self.subtitle_label.setText(f"有 {failed} 个文件下载失败，请查看详情")
        else:
            self.title_label.setText("迁移完成！")
            self.title_label.setStyleSheet(f"""
                QLabel {{
                    color: {ModernStyle.COLORS['success']};
                    font-size: {ModernStyle.FONT_SIZES['title_large']}px;
                    font-weight: 700;
                    background: transparent;
                    border: none;
                }}
            """)
            self.subtitle_label.setText("所有照片和视频已成功迁移到 NAS")
        
        self._update_detail_table(stats)
    
    def set_duration(self, seconds):
        """设置耗时"""
        hours, remainder = divmod(int(seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        duration_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        self.duration_card.value_label.setText(duration_str)
    
    def _update_detail_table(self, stats):
        """更新详情表格"""
        details = [
            ("总资源数", str(stats.get("total", 0))),
            ("成功下载", str(stats.get("downloaded", 0))),
            ("跳过(已存在)", str(stats.get("skipped", 0))),
            ("失败", str(stats.get("failed", 0))),
            ("去重", str(stats.get("duplicates", 0))),
            ("目标路径", stats.get("target_path", "N/A")),
            ("开始时间", stats.get("start_time", "N/A")),
            ("结束时间", stats.get("end_time", "N/A")),
            ("总耗时", stats.get("duration", "N/A")),
        ]
        
        self.detail_table.setRowCount(len(details))
        
        for i, (key, value) in enumerate(details):
            self.detail_table.setItem(i, 0, QTableWidgetItem(key))
            self.detail_table.setItem(i, 1, QTableWidgetItem(value))
    
    def _on_export_clicked(self):
        """导出报告"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "导出迁移报告",
            "migration_report.txt",
            "文本文件 (*.txt);;所有文件 (*)"
        )
        
        if filename:
            try:
                self._export_to_file(filename)
                QMessageBox.information(self, "成功", f"报告已导出到:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败:\n{str(e)}")
    
    def _export_to_file(self, filename):
        """导出报告到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("=" * 50 + "\n")
            f.write("iCloud 照片迁移报告\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("统计信息:\n")
            f.write("-" * 30 + "\n")
            f.write(f"总资源数: {self.stats.get('total', 0)}\n")
            f.write(f"成功下载: {self.stats.get('downloaded', 0)}\n")
            f.write(f"跳过(已存在): {self.stats.get('skipped', 0)}\n")
            f.write(f"失败: {self.stats.get('failed', 0)}\n")
            f.write(f"去重: {self.stats.get('duplicates', 0)}\n\n")
            
            f.write("详细信息:\n")
            f.write("-" * 30 + "\n")
            f.write(f"目标路径: {self.stats.get('target_path', 'N/A')}\n")
            f.write(f"开始时间: {self.stats.get('start_time', 'N/A')}\n")
            f.write(f"结束时间: {self.stats.get('end_time', 'N/A')}\n")
            f.write(f"总耗时: {self.stats.get('duration', 'N/A')}\n")


class FailedFilesDialog(QWidget):
    """失败文件列表对话框 - 现代UI设计"""
    
    def __init__(self, failed_files, parent=None):
        super().__init__(parent)
        self.failed_files = failed_files
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        self.setWindowTitle("失败文件列表")
        self.setMinimumSize(600, 400)
        self.setStyleSheet(f"background: {ModernStyle.COLORS['bg_secondary']};")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(ModernStyle.SPACING['xl'])
        layout.setContentsMargins(
            ModernStyle.SPACING['xxl'], 
            ModernStyle.SPACING['xxl'],
            ModernStyle.SPACING['xxl'], 
            ModernStyle.SPACING['xxl']
        )
        
        # 标题
        title_row = QHBoxLayout()
        title_icon = QLabel("❌")
        title_icon.setStyleSheet("background: transparent; border: none;")
        title_icon.setFont(QFont("", 20))
        
        title_text = QLabel(f"失败文件列表 ({len(self.failed_files)} 个)")
        title_text.setStyleSheet(ModernStyle.get_title_style('title_small'))
        
        title_row.addWidget(title_icon)
        title_row.addWidget(title_text)
        title_row.addStretch()
        layout.addLayout(title_row)
        
        # 文件列表
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(3)
        self.file_table.setHorizontalHeaderLabels(["文件名", "错误信息", "重试次数"])
        self.file_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.file_table.verticalHeader().setVisible(False)
        self.file_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.file_table.setStyleSheet(ModernStyle.get_table_style())
        
        self.file_table.setRowCount(len(self.failed_files))
        
        for i, file_info in enumerate(self.failed_files):
            self.file_table.setItem(i, 0, QTableWidgetItem(file_info.get("filename", "")))
            self.file_table.setItem(i, 1, QTableWidgetItem(file_info.get("error_message", "")))
            self.file_table.setItem(i, 2, QTableWidgetItem(str(file_info.get("retry_count", 0))))
        
        layout.addWidget(self.file_table)
        
        # 关闭按钮
        close_btn = QPushButton("✖️ 关闭")
        close_btn.setStyleSheet(ModernStyle.get_button_style('primary', 'medium'))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)
