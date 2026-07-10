#!/bin/bash

# ============================================
# iCloud 照片迁移助手 - 启动脚本
# 版本: 2.0.0
# ============================================

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到脚本目录
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印欢迎信息
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}                                                            ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}    ${GREEN}iCloud 照片迁移助手${NC}                                    ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}    ${YELLOW}版本: 2.0.0${NC}                                            ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}                                                            ${BLUE}║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查 Python 版本
echo -e "${BLUE}[1/3]${NC} 检查 Python 版本..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "  ${GREEN}✅${NC} $PYTHON_VERSION"
else
    echo -e "  ${RED}❌${NC} Python 未安装"
    echo ""
    echo "请安装 Python 3.9 或更高版本:"
    echo "  https://www.python.org/downloads/"
    echo ""
    read -p "按回车键退出..."
    exit 1
fi

# 检查依赖
echo ""
echo -e "${BLUE}[2/3]${NC} 检查依赖..."
if python3 -c "import PySide6" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} PySide6 已安装"
else
    echo -e "  ${YELLOW}⚠️${NC} PySide6 未安装，正在安装..."
    pip3 install PySide6 --quiet
    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✅${NC} PySide6 安装成功"
    else
        echo -e "  ${RED}❌${NC} PySide6 安装失败"
        echo ""
        echo "请手动运行: pip3 install -r requirements.txt"
        echo ""
        read -p "按回车键退出..."
        exit 1
    fi
fi

if python3 -c "import yaml" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} PyYAML 已安装"
else
    echo -e "  ${YELLOW}⚠️${NC} PyYAML 未安装，正在安装..."
    pip3 install pyyaml --quiet
fi

if python3 -c "import qrcode" 2>/dev/null; then
    echo -e "  ${GREEN}✅${NC} qrcode 已安装"
else
    echo -e "  ${YELLOW}⚠️${NC} qrcode 未安装，正在安装..."
    pip3 install qrcode --quiet
fi

# 启动应用
echo ""
echo -e "${BLUE}[3/3]${NC} 启动应用..."
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""

# 运行主程序
python3 main.py

# 如果出错，显示错误信息
if [ $? -ne 0 ]; then
    echo ""
    echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║${NC}                                                            ${RED}║${NC}"
    echo -e "${RED}║${NC}    ${RED}程序出错${NC}                                               ${RED}║${NC}"
    echo -e "${RED}║${NC}                                                            ${RED}║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "请检查以下信息："
    echo "  1. 是否已安装 Python 3.9+"
    echo "  2. 是否已安装依赖: pip3 install -r requirements.txt"
    echo "  3. 查看日志: cat logs/app_*.log"
    echo ""
    read -p "按回车键退出..."
fi
