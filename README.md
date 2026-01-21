# Gemini-FigExtractor

这是一个基于 **Gemini** API 和 **PyMuPDF** 的智能工具，旨在从学术论文（PDF格式）提取出封面图（如系统架构图、流程图或实验结果图）。

## 🚀 功能特性

- **智能识别**：利用 Gemini 视觉能力理解论文深度语义，寻找最具代表性的视觉内容。
- **精准裁剪**：通过模型返回的归一化坐标，利用 PyMuPDF (fitz) 实现像素级无损裁剪。
- **高分解析度**：支持自定义缩放倍率（默认 3x）以确保导出的图片清晰。

## 🛠️ 环境配置

1. **克隆仓库**：

   ```bash
   git clone https://github.com/fduTristin/Gemini-FigExtractor.git
   cd pdf-image-extractor
   ```

2. **运行安装脚本**： 确保你已安装 Python 3.10+，然后执行：

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   *该脚本将自动创建虚拟环境并安装所需的 Python 包（`google-genai`, `pymupdf` 等）。*

## ⚙️ 配置文件

在运行程序之前，你需要配置你的 API 密钥：

1. 打开 `config.py`。
2. 配置你的 API Key 以及代理（可选）。

## 📖 使用方法

1. **准备 PDF 文件**：将你要处理的论文下载到本地文件夹。

2. **执行程序**：

    ```bash
    # 单文件
    python main.py {filepath} -o images/ # 默认保存到 /images/{PDF_NAME}.png
    # 多文件
    python main.py {filedir}
    ```
