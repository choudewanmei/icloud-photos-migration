"""
常量定义模块
集中管理所有魔法数字和配置常量
"""

# ==================== 数据库相关 ====================

# 连接池配置
DB_MAX_CONNECTIONS = 5
DB_WAL_MODE = True
DB_SYNC_MODE = "NORMAL"

# 数据库文件
DB_FILE = "migration_state.db"

# ==================== 下载相关 ====================

# 线程配置
DEFAULT_THREADS_NUM = 20
MIN_THREADS_NUM = 1
MAX_THREADS_NUM = 20

# 重试配置
DEFAULT_MAX_RETRIES = 3
MAX_RETRIES_LIMIT = 10
RETRY_BASE_DELAY = 2  # 秒
RETRY_MAX_DELAY = 60  # 秒

# 磁盘空间
MIN_DISK_SPACE_GB = 1  # GB
BYTES_PER_GB = 1024 * 1024 * 1024

# 进程超时
PROCESS_TIMEOUT = 120  # 秒

# ==================== UI 相关 ====================

# 窗口尺寸
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 700

# 字体大小
FONT_SIZE_TITLE_LARGE = 28
FONT_SIZE_TITLE = 22
FONT_SIZE_TITLE_SMALL = 17
FONT_SIZE_BODY = 15
FONT_SIZE_BODY_SMALL = 13
FONT_SIZE_CAPTION = 11

# 间距
SPACING_XS = 4
SPACING_SM = 8
SPACING_MD = 12
SPACING_LG = 16
SPACING_XL = 20
SPACING_XXL = 24
SPACING_XXXL = 32

# 圆角
BORDER_RADIUS_SM = 6
BORDER_RADIUS_MD = 8
BORDER_RADIUS_LG = 10
BORDER_RADIUS_XL = 12
BORDER_RADIUS_XXL = 16

# 进度条高度
PROGRESS_BAR_HEIGHT = 24

# 统计卡片
STAT_CARD_PADDING = 16

# 日志区域高度
LOG_AREA_HEIGHT = 150

# 二维码尺寸
QRCODE_SIZE = 300

# 按钮尺寸
BUTTON_HEIGHT_SMALL = 32
BUTTON_HEIGHT_MEDIUM = 40
BUTTON_HEIGHT_LARGE = 50

# ==================== 颜色相关 ====================

# 主色调
COLOR_PRIMARY = '#007AFF'
COLOR_PRIMARY_HOVER = '#0056CC'
COLOR_PRIMARY_PRESSED = '#004099'

# 成功色
COLOR_SUCCESS = '#34C759'
COLOR_SUCCESS_HOVER = '#2DA44E'
COLOR_SUCCESS_PRESSED = '#248A3D'

# 警告色
COLOR_WARNING = '#FF9500'
COLOR_WARNING_HOVER = '#E08600'
COLOR_WARNING_PRESSED = '#CC7700'

# 错误色
COLOR_ERROR = '#FF3B30'
COLOR_ERROR_HOVER = '#D63029'
COLOR_ERROR_PRESSED = '#B3261E'

# 紫色
COLOR_PURPLE = '#5856D6'
COLOR_PURPLE_HOVER = '#4240B0'
COLOR_PURPLE_PRESSED = '#36349A'

# 背景色
COLOR_BG_PRIMARY = '#FFFFFF'
COLOR_BG_SECONDARY = '#F2F2F7'
COLOR_BG_TERTIARY = '#E5E5EA'
COLOR_BG_CARD = '#FFFFFF'

# 文本色
COLOR_TEXT_PRIMARY = '#000000'
COLOR_TEXT_SECONDARY = '#3C3C43'
COLOR_TEXT_TERTIARY = '#8E8E93'
COLOR_TEXT_QUATERNARY = '#C7C7CC'

# 边框色
COLOR_BORDER = '#C6C6C8'
COLOR_BORDER_LIGHT = '#E5E5EA'

# 分隔线
COLOR_SEPARATOR = '#C6C6C8'

# ==================== 日志相关 ====================

# 日志配置
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5
LOG_DIR = "logs"
LOG_FORMAT_CONSOLE = '%(asctime)s [%(levelname)s] %(message)s'
LOG_FORMAT_FILE = '%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s'
LOG_DATE_FORMAT_CONSOLE = '%H:%M:%S'
LOG_DATE_FORMAT_FILE = '%Y-%m-%d %H:%M:%S'

# ==================== 文件夹格式 ====================

DEFAULT_FOLDER_FORMAT = "%Y/%Y-%m/%Y-%d"

# ==================== Cookie 配置 ====================

DEFAULT_COOKIE_DIR = "./cookies"

# ==================== 错误消息 ====================

ERROR_MESSAGES = {
    "Invalid credentials": "Apple ID 或密码错误，请检查后重试",
    "Two-factor authentication": "需要两步验证，请在 iPhone 上确认",
    "2FA code": "验证码错误或已过期，请重新获取",
    "Account locked": "账户已被锁定，请稍后再试或联系 Apple 支持",
    "Network error": "网络连接失败，请检查网络设置",
    "Timeout": "连接超时，请检查网络或稍后再试",
    "Rate limit": "请求过于频繁，请稍后再试",
    "Disk full": "磁盘空间不足，请清理空间后重试",
    "Permission denied": "权限不足，请检查文件夹权限",
}

# ==================== 网络错误模式 ====================

RETRYABLE_ERRORS = [
    "network", "timeout", "connection", "reset", "refused",
    "unreachable", "ECONNRESET", "ETIMEDOUT", "ENETUNREACH",
    "503", "502", "429",
]

FATAL_ERRORS = [
    "authentication", "invalid credentials", "2fa", "password",
    "account locked", "401", "403",
]

# ==================== 文件大小格式 ====================

SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB']
