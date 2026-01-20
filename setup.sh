#!/bin/bash

# =================================================================
# Project Setup Script (Conda Edition)
# =================================================================

# 1. 配置参数
ENV_NAME="gemini_ocr"
PYTHON_VERSION="3.10"
CONDA_PATH=$(which conda)

# 颜色输出
GREEN='\033[0;32m'
NC='\033[0m' # No Color
echo -e "${GREEN}[*] Starting environment setup for: ${ENV_NAME}${NC}"

# 2. 检查 Conda 是否安装
if [ -z "$CONDA_PATH" ]; then
    echo "Error: Conda is not installed. Please install Miniconda or Anaconda first."
    exit 1
fi

# 3. 初始化 Shell (确保可以在脚本中使用 'conda activate')
# 这一步对于在脚本内切换环境至关重要
source "$(conda info --base)/etc/profile.d/conda.sh"

# 4. 创建 Conda 环境
if conda info --envs | grep -q "$ENV_NAME"; then
    echo -e "${GREEN}[*] Environment '${ENV_NAME}' already exists. Skipping creation.${NC}"
else
    echo -e "${GREEN}[*] Creating conda environment: ${ENV_NAME}...${NC}"
    conda create -n "$ENV_NAME" python="$PYTHON_VERSION" -y
fi

# 5. 激活环境并安装依赖
echo -e "${GREEN}[*] Activating environment and installing dependencies...${NC}"
conda activate "$ENV_NAME"

# 安装核心依赖
# google-generativeai: Gemini API 官方库
# pymupdf: PDF 处理与图片裁剪
pip install --upgrade pip
pip install -r requirements.txt

# 6. 检查 API Key 环境变量 (可选但推荐)
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "\033[0;33m[!] Warning: GEMINI_API_KEY environment variable is not set.${NC}"
    echo "    You can set it by running: export GEMINI_API_KEY='your_key_here'"
fi

echo -e "${GREEN}====================================================${NC}"
echo -e "${GREEN}[DONE] Setup complete!${NC}"
echo -e "To start working, run:"
echo -e "    conda activate ${ENV_NAME}"
echo -e "===================================================="