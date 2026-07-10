"""
欢迎页面 - 现代UI设计
遵循 macOS Human Interface Guidelines
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QGroupBox, QFileDialog,
    QMessageBox, QFrame, QSizePolicy, QStackedWidget,
    QRadioButton, QButtonGroup, QScrollArea, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QPixmap, QIcon

from core.nas_detector import NASDetector, NASPathValidator
from core.qrcode_auth import QRCodeAuthManager
from gui.modern_style import ModernStyle


class WelcomePage(QWidget):
    """欢迎/设置页面 - 现代UI设计"""
    
    # 信号
    icloud_connected = Signal(str, int)  # apple_id, total_assets
    nas_ready = Signal(str)              # nas_path
    start_migration = Signal()           # 开始迁移
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apple_id = ""
        self.nas_path = ""
        self.total_assets = 0
        self.nas_detector = None
        self.qr_auth_manager = None
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化界面"""
        # 设置背景色
        self.setStyleSheet(f"background: {ModernStyle.COLORS['bg_secondary']};")
        
        # 使用滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(ModernStyle.get_scroll_area_style())
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(ModernStyle.SPACING['xl'])
        layout.setContentsMargins(
            ModernStyle.SPACING['xxxl'], 
            ModernStyle.SPACING['xxl'],
            ModernStyle.SPACING['xxxl'], 
            ModernStyle.SPACING['xxl']
        )
        
        # 顶部 Logo 和标题
        self._create_header(layout)
        
        # 步骤1：iCloud 登录
        self._create_icloud_section(layout)
        
        # 步骤2：NAS 设置
        self._create_nas_section(layout)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 开始按钮
        self._create_start_button(layout)
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
    
    def _create_header(self, layout):
        """创建顶部标题区域"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(ModernStyle.SPACING['md'])
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 应用图标（使用文字图标）
        icon_label = QLabel("☁️")
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("background: transparent; border: none;")
        header_layout.addWidget(icon_label)
        
        # 标题
        title = QLabel("iCloud 照片迁移助手")
        title.setStyleSheet(ModernStyle.get_title_style('title_large'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("将 iCloud 照片和视频安全迁移到您的 NAS")
        subtitle.setStyleSheet(ModernStyle.get_subtitle_style())
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
    
    def _create_icloud_section(self, layout):
        """创建 iCloud 认证区域"""
        # 使用卡片样式
        card = QFrame()
        card.setStyleSheet(ModernStyle.get_card_style())
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(ModernStyle.SPACING['lg'])
        
        # 标题行
        title_row = QHBoxLayout()
        title_icon = QLabel("🔐")
        title_icon.setStyleSheet("background: transparent; border: none;")
        title_icon.setFont(QFont("", 20))
        
        title_text = QLabel("连接 iCloud")
        title_text.setStyleSheet(ModernStyle.get_title_style('title_small'))
        
        title_row.addWidget(title_icon)
        title_row.addWidget(title_text)
        title_row.addStretch()
        card_layout.addLayout(title_row)
        
        # 登录方式选择
        method_frame = QFrame()
        method_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernStyle.COLORS['bg_secondary']};
                border-radius: {ModernStyle.BORDER_RADIUS['md']}px;
                padding: 8px;
            }}
        """)
        method_layout = QHBoxLayout(method_frame)
        method_layout.setSpacing(ModernStyle.SPACING['sm'])
        
        self.login_method_group = QButtonGroup()
        
        self.qr_login_radio = QRadioButton("📱 扫码登录（推荐）")
        self.qr_login_radio.setStyleSheet(ModernStyle.get_radio_style())
        self.qr_login_radio.setChecked(True)
        
        self.password_login_radio = QRadioButton("🔑 密码登录")
        self.password_login_radio.setStyleSheet(ModernStyle.get_radio_style())
        
        self.login_method_group.addButton(self.qr_login_radio, 0)
        self.login_method_group.addButton(self.password_login_radio, 1)
        
        method_layout.addWidget(self.qr_login_radio)
        method_layout.addWidget(self.password_login_radio)
        method_layout.addStretch()
        
        card_layout.addWidget(method_frame)
        
        # 登录内容堆栈
        self.login_stack = QStackedWidget()
        
        # 扫码登录页面
        self._create_qr_login_page()
        
        # 密码登录页面
        self._create_password_login_page()
        
        card_layout.addWidget(self.login_stack)
        
        # 连接信号
        self.qr_login_radio.toggled.connect(self._on_login_method_changed)
        self.password_login_radio.toggled.connect(self._on_login_method_changed)
        
        # 状态显示
        self.icloud_status = QLabel("")
        self.icloud_status.setStyleSheet(ModernStyle.get_label_style('tertiary'))
        self.icloud_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.icloud_status)
        
        layout.addWidget(card)
    
    def _create_qr_login_page(self):
        """创建扫码登录页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(ModernStyle.SPACING['xl'])
        
        # 说明文字
        desc = QLabel("使用 iPhone 或 iPad 扫描二维码，快速安全登录 iCloud")
        desc.setStyleSheet(ModernStyle.get_label_style('secondary'))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Apple ID 输入（可选）
        input_frame = QFrame()
        input_frame.setStyleSheet("background: transparent; border: none;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(ModernStyle.SPACING['md'])
        
        apple_id_label = QLabel("Apple ID:")
        apple_id_label.setStyleSheet(ModernStyle.get_label_style('secondary'))
        apple_id_label.setFixedWidth(80)
        
        self.qr_apple_id_input = QLineEdit()
        self.qr_apple_id_input.setPlaceholderText("输入 Apple ID 可加速认证（可选）")
        self.qr_apple_id_input.setStyleSheet(ModernStyle.get_input_style())
        
        input_layout.addWidget(apple_id_label)
        input_layout.addWidget(self.qr_apple_id_input)
        layout.addWidget(input_frame)
        
        # 生成二维码按钮
        self.generate_qr_btn = QPushButton("📱 生成二维码")
        self.generate_qr_btn.setStyleSheet(ModernStyle.get_button_style('success', 'large'))
        self.generate_qr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.generate_qr_btn.clicked.connect(self._on_generate_qr_clicked)
        layout.addWidget(self.generate_qr_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 二维码显示区域
        qr_container = QFrame()
        qr_container.setStyleSheet(f"""
            QFrame {{
                background: {ModernStyle.COLORS['bg_primary']};
                border: 3px solid {ModernStyle.COLORS['primary']};
                border-radius: {ModernStyle.BORDER_RADIUS['xl']}px;
                padding: 24px;
            }}
        """)
        qr_container_layout = QVBoxLayout(qr_container)
        qr_container_layout.setSpacing(ModernStyle.SPACING['lg'])
        qr_container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 二维码标签
        self.qr_label = QLabel("等待生成二维码...")
        self.qr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.qr_label.setFixedSize(300, 300)
        self.qr_label.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {ModernStyle.COLORS['border']};
                border-radius: {ModernStyle.BORDER_RADIUS['lg']}px;
                background: {ModernStyle.COLORS['bg_secondary']};
                font-size: 16px;
                color: {ModernStyle.COLORS['text_tertiary']};
            }}
        """)
        qr_container_layout.addWidget(self.qr_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 二维码状态
        self.qr_status = QLabel("")
        self.qr_status.setStyleSheet(ModernStyle.get_label_style('tertiary'))
        self.qr_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        qr_container_layout.addWidget(self.qr_status)
        
        layout.addWidget(qr_container)
        
        # 操作按钮区域
        btn_container = QFrame()
        btn_container.setStyleSheet("background: transparent; border: none;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(ModernStyle.SPACING['md'])
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 在浏览器中打开按钮
        self.open_browser_btn = QPushButton("🌐 在浏览器中打开")
        self.open_browser_btn.setStyleSheet(ModernStyle.get_button_style('primary', 'medium'))
        self.open_browser_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_browser_btn.setEnabled(False)
        self.open_browser_btn.clicked.connect(self._on_open_browser_clicked)
        btn_layout.addWidget(self.open_browser_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 我已完成登录按钮
        self.confirm_login_btn = QPushButton("✅ 我已完成登录")
        self.confirm_login_btn.setStyleSheet(ModernStyle.get_button_style('purple', 'medium'))
        self.confirm_login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_login_btn.setEnabled(False)
        self.confirm_login_btn.clicked.connect(self._on_confirm_login_clicked)
        btn_layout.addWidget(self.confirm_login_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 刷新二维码按钮
        self.refresh_qr_btn = QPushButton("🔄 刷新二维码")
        self.refresh_qr_btn.setStyleSheet(ModernStyle.get_button_style('warning', 'medium'))
        self.refresh_qr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_qr_btn.setEnabled(False)
        self.refresh_qr_btn.clicked.connect(self._on_refresh_qr_clicked)
        btn_layout.addWidget(self.refresh_qr_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(btn_container)
        
        # 使用说明
        instructions_frame = QFrame()
        instructions_frame.setStyleSheet(f"""
            QFrame {{
                background: {ModernStyle.COLORS['primary']}10;
                border: 1px solid {ModernStyle.COLORS['primary']}30;
                border-radius: {ModernStyle.BORDER_RADIUS['md']}px;
                padding: 16px;
            }}
        """)
        instructions_layout = QVBoxLayout(instructions_frame)
        instructions_layout.setSpacing(ModernStyle.SPACING['sm'])
        
        instructions_title = QLabel("📋 使用步骤")
        instructions_title.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['primary']};
                font-size: {ModernStyle.FONT_SIZES['body']}px;
                font-weight: 600;
                background: transparent;
                border: none;
            }}
        """)
        instructions_layout.addWidget(instructions_title)
        
        instructions = QLabel(
            "1. 点击「生成二维码」按钮\n"
            "2. 使用 iPhone 相机扫描二维码\n"
            "3. 在 Safari 浏览器中登录 iCloud\n"
            "4. 返回这里点击「我已完成登录」"
        )
        instructions.setStyleSheet(f"""
            QLabel {{
                color: {ModernStyle.COLORS['text_secondary']};
                font-size: {ModernStyle.FONT_SIZES['body_small']}px;
                background: transparent;
                border: none;
                line-height: 1.5;
            }}
        """)
        instructions.setWordWrap(True)
        instructions_layout.addWidget(instructions)
        
        layout.addWidget(instructions_frame)
        
        self.login_stack.addWidget(page)
    
    def _create_password_login_page(self):
        """创建密码登录页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(ModernStyle.SPACING['lg'])
        
        # Apple ID 输入
        input_frame = QFrame()
        input_frame.setStyleSheet("background: transparent; border: none;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setSpacing(ModernStyle.SPACING['md'])
        
        id_label = QLabel("Apple ID:")
        id_label.setStyleSheet(ModernStyle.get_label_style('secondary'))
        id_label.setFixedWidth(80)
        
        self.apple_id_input = QLineEdit()
        self.apple_id_input.setPlaceholderText("输入您的 Apple ID")
        self.apple_id_input.setStyleSheet(ModernStyle.get_input_style())
        
        input_layout.addWidget(id_label)
        input_layout.addWidget(self.apple_id_input)
        layout.addWidget(input_frame)
        
        # 连接按钮
        self.connect_btn = QPushButton("🔗 连接 iCloud")
        self.connect_btn.setStyleSheet(ModernStyle.get_button_style('success', 'medium'))
        self.connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.connect_btn.clicked.connect(self._on_connect_clicked)
        layout.addWidget(self.connect_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 说明
        note = QLabel("💡 扫码登录更安全、更便捷，推荐使用")
        note.setStyleSheet(ModernStyle.get_label_style('warning'))
        note.setWordWrap(True)
        layout.addWidget(note)
        
        self.login_stack.addWidget(page)
    
    def _on_login_method_changed(self):
        """登录方式切换"""
        if self.qr_login_radio.isChecked():
            self.login_stack.setCurrentIndex(0)
        else:
            self.login_stack.setCurrentIndex(1)
    
    def _on_generate_qr_clicked(self):
        """生成二维码"""
        apple_id = self.qr_apple_id_input.text().strip()
        
        # 创建认证管理器
        if not self.qr_auth_manager:
            self.qr_auth_manager = QRCodeAuthManager(self)
            self.qr_auth_manager.qrcode_generated.connect(self._on_qrcode_generated)
            self.qr_auth_manager.auth_success.connect(self._on_auth_success)
            self.qr_auth_manager.auth_failed.connect(self._on_auth_failed)
            self.qr_auth_manager.auth_timeout.connect(self._on_auth_timeout)
            self.qr_auth_manager.status_update.connect(self._on_status_update)
            self.qr_auth_manager.auth_started.connect(self._on_auth_started)
        
        # 生成二维码
        self.generate_qr_btn.setEnabled(False)
        self.generate_qr_btn.setText("⏳ 生成中...")
        self.qr_status.setText("正在生成二维码...")
        self.qr_status.setStyleSheet(ModernStyle.get_label_style('warning'))
        
        self.qr_auth_manager.generate_auth_qrcode(apple_id)
    
    def _on_qrcode_generated(self, pixmap):
        """二维码生成完成"""
        self.qr_label.setPixmap(pixmap)
        self.qr_label.setStyleSheet(f"""
            QLabel {{
                border: 2px solid {ModernStyle.COLORS['success']};
                border-radius: {ModernStyle.BORDER_RADIUS['lg']}px;
                background: {ModernStyle.COLORS['bg_primary']};
            }}
        """)
        self.qr_status.setText("✅ 二维码已生成，请使用 iPhone 扫描")
        self.qr_status.setStyleSheet(ModernStyle.get_label_style('success'))
        
        self.generate_qr_btn.setText("📱 生成二维码")
        self.generate_qr_btn.setEnabled(False)
        self.open_browser_btn.setEnabled(True)
        self.confirm_login_btn.setEnabled(True)
        self.refresh_qr_btn.setEnabled(True)
    
    def _on_auth_started(self):
        """认证开始"""
        self.qr_status.setText("⏳ 请在浏览器中完成 iCloud 登录...")
        self.qr_status.setStyleSheet(ModernStyle.get_label_style('warning'))
    
    def _on_auth_success(self, session):
        """认证成功"""
        self.apple_id = self.qr_apple_id_input.text().strip() or "已认证用户"
        self.icloud_status.setText(f"✅ iCloud 认证成功: {self.apple_id}")
        self.icloud_status.setStyleSheet(ModernStyle.get_label_style('success'))
        
        if self.qr_auth_manager:
            self.qr_auth_manager.stop_polling()
        
        self._update_start_button()
    
    def _on_auth_failed(self, error):
        """认证失败"""
        self.qr_status.setText(f"❌ 认证失败: {error}")
        self.qr_status.setStyleSheet(ModernStyle.get_label_style('error'))
        self.generate_qr_btn.setText("📱 生成二维码")
        self.generate_qr_btn.setEnabled(True)
        self.confirm_login_btn.setEnabled(False)
    
    def _on_auth_timeout(self):
        """认证超时"""
        self.qr_status.setText("⏰ 二维码已过期，请重新生成")
        self.qr_status.setStyleSheet(ModernStyle.get_label_style('warning'))
        self.generate_qr_btn.setText("📱 生成二维码")
        self.generate_qr_btn.setEnabled(True)
        self.open_browser_btn.setEnabled(False)
        self.confirm_login_btn.setEnabled(False)
        self.refresh_qr_btn.setEnabled(False)
    
    def _on_status_update(self, status):
        """状态更新"""
        self.qr_status.setText(status)
        if "✅" in status:
            self.qr_status.setStyleSheet(ModernStyle.get_label_style('success'))
        elif "❌" in status:
            self.qr_status.setStyleSheet(ModernStyle.get_label_style('error'))
        elif "⏳" in status:
            self.qr_status.setStyleSheet(ModernStyle.get_label_style('warning'))
    
    def _on_open_browser_clicked(self):
        """在浏览器中打开"""
        if self.qr_auth_manager:
            self.qr_auth_manager.open_auth_url_in_browser()
    
    def _on_confirm_login_clicked(self):
        """确认登录完成"""
        if self.qr_auth_manager:
            self.confirm_login_btn.setEnabled(False)
            self.qr_status.setText("⏳ 正在验证登录状态...")
            self.qr_status.setStyleSheet(ModernStyle.get_label_style('warning'))
            self.qr_auth_manager.confirm_auth_completed()
    
    def _on_refresh_qr_clicked(self):
        """刷新二维码"""
        self._on_generate_qr_clicked()
    
    def _on_connect_clicked(self):
        """点击连接 iCloud（密码登录）"""
        apple_id = self.apple_id_input.text().strip()
        
        if not apple_id:
            QMessageBox.warning(self, "提示", "请输入 Apple ID")
            return
        
        self.apple_id = apple_id
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("⏳ 连接中...")
        self.icloud_status.setText("正在连接 iCloud...")
        self.icloud_status.setStyleSheet(ModernStyle.get_label_style('warning'))
        
        # 模拟认证过程
        QTimer.singleShot(100, self._simulate_authentication)
    
    def _simulate_authentication(self):
        """模拟认证过程"""
        self.icloud_status.setText("ℹ️ 请在终端中完成 iCloud 认证（输入密码和验证码）")
        self.icloud_status.setStyleSheet(ModernStyle.get_label_style('accent'))
        self.connect_btn.setEnabled(True)
        self.connect_btn.setText("🔗 连接 iCloud")
        self.apple_id = self.apple_id_input.text().strip()
    
    def _create_nas_section(self, layout):
        """创建 NAS 设置区域"""
        # 使用卡片样式
        card = QFrame()
        card.setStyleSheet(ModernStyle.get_card_style())
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(ModernStyle.SPACING['lg'])
        
        # 标题行
        title_row = QHBoxLayout()
        title_icon = QLabel("💾")
        title_icon.setStyleSheet("background: transparent; border: none;")
        title_icon.setFont(QFont("", 20))
        
        title_text = QLabel("设置 NAS 路径")
        title_text.setStyleSheet(ModernStyle.get_title_style('title_small'))
        
        title_row.addWidget(title_icon)
        title_row.addWidget(title_text)
        title_row.addStretch()
        card_layout.addLayout(title_row)
        
        # NAS 路径输入
        path_frame = QFrame()
        path_frame.setStyleSheet("background: transparent; border: none;")
        path_layout = QHBoxLayout(path_frame)
        path_layout.setSpacing(ModernStyle.SPACING['md'])
        
        path_label = QLabel("NAS 路径:")
        path_label.setStyleSheet(ModernStyle.get_label_style('secondary'))
        path_label.setFixedWidth(80)
        
        self.nas_path_input = QLineEdit()
        self.nas_path_input.setPlaceholderText("例如: /Volumes/MyNAS/iCloud-Photos")
        self.nas_path_input.setStyleSheet(ModernStyle.get_input_style())
        
        browse_btn = QPushButton("📁 浏览")
        browse_btn.setStyleSheet(ModernStyle.get_button_style('primary', 'small'))
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._on_browse_clicked)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.nas_path_input)
        path_layout.addWidget(browse_btn)
        card_layout.addWidget(path_frame)
        
        # 检测按钮
        self.detect_btn = QPushButton("🔍 检测 NAS 连接")
        self.detect_btn.setStyleSheet(ModernStyle.get_button_style('purple', 'medium'))
        self.detect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.detect_btn.clicked.connect(self._on_detect_clicked)
        card_layout.addWidget(self.detect_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 状态显示
        self.nas_status = QLabel("")
        self.nas_status.setStyleSheet(ModernStyle.get_label_style('tertiary'))
        self.nas_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.nas_status)
        
        layout.addWidget(card)
    
    def _on_browse_clicked(self):
        """点击浏览按钮"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "选择 NAS 挂载路径",
            "/Volumes",
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.nas_path_input.setText(folder)
    
    def _on_detect_clicked(self):
        """点击检测 NAS"""
        nas_path = self.nas_path_input.text().strip()
        
        if not nas_path:
            QMessageBox.warning(self, "提示", "请输入 NAS 路径")
            return
        
        self.nas_path = nas_path
        self.detect_btn.setEnabled(False)
        self.detect_btn.setText("⏳ 检测中...")
        self.nas_status.setText("正在检测 NAS 连接...")
        self.nas_status.setStyleSheet(ModernStyle.get_label_style('warning'))
        
        # 启动 NAS 检测
        if self.nas_detector:
            self.nas_detector.stop()
        
        self.nas_detector = NASDetector(nas_path, check_interval=2)
        self.nas_detector.status_update.connect(self._on_nas_status_update)
        self.nas_detector.nas_ready.connect(self._on_nas_ready)
        self.nas_detector.start()
    
    def _on_nas_status_update(self, status):
        """NAS 状态更新"""
        self.nas_status.setText(status)
        
        if "✅" in status:
            self.nas_status.setStyleSheet(ModernStyle.get_label_style('success'))
        elif "❌" in status:
            self.nas_status.setStyleSheet(ModernStyle.get_label_style('error'))
        else:
            self.nas_status.setStyleSheet(ModernStyle.get_label_style('warning'))
    
    def _on_nas_ready(self, path):
        """NAS 就绪"""
        self.nas_path = path
        self.detect_btn.setEnabled(True)
        self.detect_btn.setText("🔍 检测 NAS 连接")
        self._update_start_button()
    
    def _update_start_button(self):
        """更新开始按钮状态"""
        can_start = bool(self.apple_id) and bool(self.nas_path)
        self.start_btn.setEnabled(can_start)
        
        if can_start:
            self.start_btn.setStyleSheet(ModernStyle.get_button_style('success', 'large'))
        else:
            self.start_btn.setStyleSheet(ModernStyle.get_button_style('primary', 'large'))
    
    def _create_start_button(self, layout):
        """创建开始按钮"""
        btn_container = QFrame()
        btn_container.setStyleSheet("background: transparent; border: none;")
        btn_layout = QVBoxLayout(btn_container)
        btn_layout.setSpacing(ModernStyle.SPACING['md'])
        
        self.start_btn = QPushButton("🚀 开始迁移")
        self.start_btn.setStyleSheet(ModernStyle.get_button_style('primary', 'large'))
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._on_start_clicked)
        btn_layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 底部提示
        tip = QLabel("请确保已完成 iCloud 认证并设置 NAS 路径")
        tip.setStyleSheet(ModernStyle.get_label_style('tertiary'))
        tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(tip)
        
        layout.addWidget(btn_container)
    
    def _on_start_clicked(self):
        """点击开始迁移"""
        if self.qr_login_radio.isChecked():
            self.apple_id = self.qr_apple_id_input.text().strip() or "已认证用户"
        else:
            self.apple_id = self.apple_id_input.text().strip()
        
        self.nas_path = self.nas_path_input.text().strip()
        self.start_migration.emit()
    
    def get_config(self):
        """获取配置"""
        return {
            "apple_id": self.apple_id,
            "nas_path": self.nas_path,
            "total_assets": self.total_assets
        }
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.nas_detector:
            self.nas_detector.stop()
        if self.qr_auth_manager:
            self.qr_auth_manager.stop_polling()
        super().closeEvent(event)
