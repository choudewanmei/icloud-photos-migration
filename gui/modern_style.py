"""
现代UI样式定义
遵循 macOS Human Interface Guidelines 和现代设计规范
"""

from core.constants import (
    FONT_SIZE_TITLE_LARGE, FONT_SIZE_TITLE, FONT_SIZE_TITLE_SMALL,
    FONT_SIZE_BODY, FONT_SIZE_BODY_SMALL, FONT_SIZE_CAPTION,
    SPACING_XS, SPACING_SM, SPACING_MD, SPACING_LG, SPACING_XL, SPACING_XXL, SPACING_XXXL,
    BORDER_RADIUS_SM, BORDER_RADIUS_MD, BORDER_RADIUS_LG, BORDER_RADIUS_XL, BORDER_RADIUS_XXL,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_PRIMARY_PRESSED,
    COLOR_SUCCESS, COLOR_SUCCESS_HOVER, COLOR_SUCCESS_PRESSED,
    COLOR_WARNING, COLOR_WARNING_HOVER, COLOR_WARNING_PRESSED,
    COLOR_ERROR, COLOR_ERROR_HOVER, COLOR_ERROR_PRESSED,
    COLOR_PURPLE, COLOR_PURPLE_HOVER, COLOR_PURPLE_PRESSED,
    COLOR_BG_PRIMARY, COLOR_BG_SECONDARY, COLOR_BG_TERTIARY, COLOR_BG_CARD,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_TERTIARY, COLOR_TEXT_QUATERNARY,
    COLOR_BORDER, COLOR_BORDER_LIGHT, COLOR_SEPARATOR,
    PROGRESS_BAR_HEIGHT, STAT_CARD_PADDING, LOG_AREA_HEIGHT,
    BUTTON_HEIGHT_SMALL, BUTTON_HEIGHT_MEDIUM, BUTTON_HEIGHT_LARGE
)


class ModernStyle:
    """现代UI样式类"""
    
    # 颜色方案
    COLORS = {
        'primary': COLOR_PRIMARY,
        'primary_hover': COLOR_PRIMARY_HOVER,
        'primary_pressed': COLOR_PRIMARY_PRESSED,
        'success': COLOR_SUCCESS,
        'success_hover': COLOR_SUCCESS_HOVER,
        'success_pressed': COLOR_SUCCESS_PRESSED,
        'warning': COLOR_WARNING,
        'warning_hover': COLOR_WARNING_HOVER,
        'warning_pressed': COLOR_WARNING_PRESSED,
        'error': COLOR_ERROR,
        'error_hover': COLOR_ERROR_HOVER,
        'error_pressed': COLOR_ERROR_PRESSED,
        'purple': COLOR_PURPLE,
        'purple_hover': COLOR_PURPLE_HOVER,
        'purple_pressed': COLOR_PURPLE_PRESSED,
        'bg_primary': COLOR_BG_PRIMARY,
        'bg_secondary': COLOR_BG_SECONDARY,
        'bg_tertiary': COLOR_BG_TERTIARY,
        'bg_card': COLOR_BG_CARD,
        'text_primary': COLOR_TEXT_PRIMARY,
        'text_secondary': COLOR_TEXT_SECONDARY,
        'text_tertiary': COLOR_TEXT_TERTIARY,
        'text_quaternary': COLOR_TEXT_QUATERNARY,
        'border': COLOR_BORDER,
        'border_light': COLOR_BORDER_LIGHT,
        'separator': COLOR_SEPARATOR,
    }
    
    # 字体大小
    FONT_SIZES = {
        'title_large': FONT_SIZE_TITLE_LARGE,
        'title': FONT_SIZE_TITLE,
        'title_small': FONT_SIZE_TITLE_SMALL,
        'body': FONT_SIZE_BODY,
        'body_small': FONT_SIZE_BODY_SMALL,
        'caption': FONT_SIZE_CAPTION,
    }
    
    # 间距
    SPACING = {
        'xs': SPACING_XS,
        'sm': SPACING_SM,
        'md': SPACING_MD,
        'lg': SPACING_LG,
        'xl': SPACING_XL,
        'xxl': SPACING_XXL,
        'xxxl': SPACING_XXXL,
    }
    
    # 圆角
    BORDER_RADIUS = {
        'sm': BORDER_RADIUS_SM,
        'md': BORDER_RADIUS_MD,
        'lg': BORDER_RADIUS_LG,
        'xl': BORDER_RADIUS_XL,
        'xxl': BORDER_RADIUS_XXL,
    }
    
    @classmethod
    def get_button_style(cls, color: str = 'primary', size: str = 'medium') -> str:
        """获取按钮样式"""
        colors = {
            'primary': (cls.COLORS['primary'], cls.COLORS['primary_hover'], cls.COLORS['primary_pressed']),
            'success': (cls.COLORS['success'], cls.COLORS['success_hover'], cls.COLORS['success_pressed']),
            'warning': (cls.COLORS['warning'], cls.COLORS['warning_hover'], cls.COLORS['warning_pressed']),
            'error': (cls.COLORS['error'], cls.COLORS['error_hover'], cls.COLORS['error_pressed']),
            'purple': (cls.COLORS['purple'], cls.COLORS['purple_hover'], cls.COLORS['purple_pressed']),
        }
        
        bg, bg_hover, bg_pressed = colors.get(color, colors['primary'])
        
        sizes = {
            'small': {'height': BUTTON_HEIGHT_SMALL, 'font_size': FONT_SIZE_BODY_SMALL, 'padding': '0 16px'},
            'medium': {'height': BUTTON_HEIGHT_MEDIUM, 'font_size': FONT_SIZE_BODY, 'padding': '0 20px'},
            'large': {'height': BUTTON_HEIGHT_LARGE, 'font_size': FONT_SIZE_TITLE_SMALL, 'padding': '0 30px'},
        }
        
        size_config = sizes.get(size, sizes['medium'])
        
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: {BORDER_RADIUS_MD}px;
                padding: {size_config['padding']};
                font-size: {size_config['font_size']}px;
                font-weight: 600;
                min-height: {size_config['height']}px;
            }}
            QPushButton:hover {{
                background-color: {bg_hover};
            }}
            QPushButton:pressed {{
                background-color: {bg_pressed};
            }}
            QPushButton:disabled {{
                background-color: {COLOR_BG_TERTIARY};
                color: {COLOR_TEXT_QUATERNARY};
            }}
        """
    
    @classmethod
    def get_input_style(cls) -> str:
        """获取输入框样式"""
        return f"""
            QLineEdit {{
                padding: 10px 14px;
                border: 2px solid {COLOR_BORDER};
                border-radius: {BORDER_RADIUS_MD}px;
                background: {COLOR_BG_PRIMARY};
                font-size: {FONT_SIZE_BODY}px;
                color: {COLOR_TEXT_PRIMARY};
                selection-background-color: {COLOR_PRIMARY};
            }}
            QLineEdit:focus {{
                border-color: {COLOR_PRIMARY};
                outline: none;
            }}
            QLineEdit:hover {{
                border-color: {COLOR_TEXT_TERTIARY};
            }}
            QLineEdit:disabled {{
                background: {COLOR_BG_SECONDARY};
                color: {COLOR_TEXT_TERTIARY};
            }}
        """
    
    @classmethod
    def get_card_style(cls) -> str:
        """获取卡片样式"""
        return f"""
            QFrame {{
                background: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: {BORDER_RADIUS_LG}px;
                padding: {SPACING_LG}px;
            }}
        """
    
    @classmethod
    def get_progress_bar_style(cls) -> str:
        """获取进度条样式"""
        return f"""
            QProgressBar {{
                border: none;
                border-radius: {PROGRESS_BAR_HEIGHT // 2}px;
                background: {COLOR_BG_TERTIARY};
                text-align: center;
                font-size: {FONT_SIZE_BODY_SMALL}px;
                font-weight: 600;
                color: {COLOR_TEXT_PRIMARY};
                min-height: {PROGRESS_BAR_HEIGHT}px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLOR_PRIMARY}, stop:1 {COLOR_PURPLE});
                border-radius: {PROGRESS_BAR_HEIGHT // 2}px;
            }}
        """
    
    @classmethod
    def get_label_style(cls, color: str = 'primary', size: str = 'body') -> str:
        """获取标签样式"""
        colors = {
            'primary': COLOR_TEXT_PRIMARY,
            'secondary': COLOR_TEXT_SECONDARY,
            'tertiary': COLOR_TEXT_TERTIARY,
            'accent': COLOR_PRIMARY,
            'success': COLOR_SUCCESS,
            'warning': COLOR_WARNING,
            'error': COLOR_ERROR,
        }
        
        text_color = colors.get(color, colors['primary'])
        font_size = cls.FONT_SIZES.get(size, FONT_SIZE_BODY)
        
        return f"""
            QLabel {{
                color: {text_color};
                font-size: {font_size}px;
            }}
        """
    
    @classmethod
    def get_title_style(cls, size: str = 'title') -> str:
        """获取标题样式"""
        font_size = cls.FONT_SIZES.get(size, FONT_SIZE_TITLE)
        
        return f"""
            QLabel {{
                color: {COLOR_TEXT_PRIMARY};
                font-size: {font_size}px;
                font-weight: 700;
            }}
        """
    
    @classmethod
    def get_subtitle_style(cls) -> str:
        """获取副标题样式"""
        return f"""
            QLabel {{
                color: {COLOR_TEXT_SECONDARY};
                font-size: {FONT_SIZE_BODY}px;
                font-weight: 400;
            }}
        """
    
    @classmethod
    def get_table_style(cls) -> str:
        """获取表格样式"""
        return f"""
            QTableWidget {{
                background: {COLOR_BG_PRIMARY};
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: {BORDER_RADIUS_MD}px;
                gridline-color: {COLOR_BORDER_LIGHT};
                font-size: {FONT_SIZE_BODY_SMALL}px;
            }}
            QTableWidget::item {{
                padding: {SPACING_SM}px;
                border-bottom: 1px solid {COLOR_BORDER_LIGHT};
            }}
            QTableWidget::item:selected {{
                background: {COLOR_PRIMARY};
                color: white;
            }}
            QHeaderView::section {{
                background: {COLOR_BG_SECONDARY};
                padding: {SPACING_SM}px;
                border: none;
                border-bottom: 2px solid {COLOR_BORDER};
                font-weight: 600;
                color: {COLOR_TEXT_SECONDARY};
            }}
        """
    
    @classmethod
    def get_scroll_area_style(cls) -> str:
        """获取滚动区域样式"""
        return f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                background: {COLOR_BG_SECONDARY};
                width: {SPACING_SM}px;
                border-radius: {SPACING_SM // 2}px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLOR_BORDER};
                border-radius: {SPACING_SM // 2}px;
                min-height: {SPACING_XL}px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLOR_TEXT_TERTIARY};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """

    @classmethod
    def get_radio_style(cls) -> str:
        """获取单选按钮样式"""
        return f"""
            QRadioButton {{
                font-size: {FONT_SIZE_BODY}px;
                color: {COLOR_TEXT_PRIMARY};
                spacing: {SPACING_SM}px;
                padding: {SPACING_SM}px;
            }}
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid {COLOR_BORDER};
                background: {COLOR_BG_PRIMARY};
            }}
            QRadioButton::indicator:checked {{
                background: {COLOR_PRIMARY};
                border-color: {COLOR_PRIMARY};
            }}
            QRadioButton::indicator:hover {{
                border-color: {COLOR_PRIMARY};
            }}
        """
    
    @classmethod
    def get_group_box_style(cls) -> str:
        """获取分组框样式"""
        return f"""
            QGroupBox {{
                background: {COLOR_BG_CARD};
                border: 1px solid {COLOR_BORDER_LIGHT};
                border-radius: {BORDER_RADIUS_LG}px;
                margin-top: 10px;
                padding-top: 20px;
                font-size: {FONT_SIZE_BODY}px;
                font-weight: 600;
                color: {COLOR_TEXT_PRIMARY};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                margin-left: 10px;
            }}
        """
