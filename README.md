# paper-md-zh-translator (OpenClaw)

将可提取文本的英文生物医学论文自动翻译为简体中文 PDF 的 OpenClaw Skill。

## 功能特点

- 🇨🇳 **简体中文 PDF** — 可搜索、可复制的黑白重排版 PDF
- 📊 **技术总结 PDF** — 结构化的中文论文总结，包含输入输出、数据集、损失函数、训练目标
- 🔬 **学科覆盖** — 适合 biology、biomedical、bioinformatics、computational biology、genomics、protein engineering、omics 等生命科学论文
- 🎯 **智能翻译** — 保留英文专有名词（模型名、数据集名、软件名、基因名等），图注表注保留原始标签
- 🧹 **自动清理** — 翻译完成后自动删除临时文件，只保留最终 3 个 PDF

## 输出文件

对于每个输入 PDF，最终交付：

| 文件 | 说明 |
|------|------|
| `<basename>.pdf` | 原 PDF（不变） |
| `<basename>_zh.pdf` | 可搜索的中文重排版 PDF |
| `<basename>_summary.pdf` | 中文技术总结 PDF |

## 翻译范围

**翻译：**
- 标题、摘要、关键词
- 正文（引言、方法、结果、讨论、结论）
- Figure/Table 标签和图注

**不翻译：**
- References / Bibliography
- Acknowledgements、Funding
- Data availability、Code availability
- Author contributions、Competing interests
- Supplementary information

## 安装

### 1. 安装依赖

```bash
pip install pypdf pillow reportlab
```

macOS 还需要：
```bash
brew install poppler
```

Linux（Debian/Ubuntu）：
```bash
sudo apt install poppler-utils
```

### 2. 安装 Skill

```bash
# 克隆到 OpenClaw workspace skills 目录
git clone https://github.com/ZZhouWJ/paper-md-zh-translator-openclaw.git \
  ~/.openclaw/workspace/skills/paper-md-zh-translator
```

### 3. 重启 OpenClaw

```bash
openclaw gateway restart
```

## 使用方法

在 OpenClaw 中直接提供论文 PDF 路径并要求翻译，例如：

```
帮我翻译这篇论文：/path/to/paper.pdf
```

或上传 PDF 文件后说：
```
用 paper-md-zh-translator 处理这个文件
```

## 工作原理

1. **文本提取** — 使用 `pypdf` 提取 PDF 中的可读文本，检测是否为扫描件
2. **结构分析** — 识别标题、段落、图表引用位置
3. **图表裁剪** — 使用 `pdftoppm` 裁剪 Figure、Table、Equation 区域为图片
4. **正文翻译** — 调用 LLM（默认 DeepSeek）将英文正文翻译为中文
5. **渲染 PDF** — 使用 ReportLab 将 Markdown 渲染为黑白 PDF
6. **生成总结** — 根据论文类型（研究论文/综述）生成结构化技术总结
7. **清理文件** — 删除所有中间文件，只保留最终 3 个 PDF

## 项目结构

```
paper-md-zh-translator/
├── SKILL.md                          # OpenClaw Skill 定义
├── README.md
├── LICENSE
├── scripts/
│   ├── extract_pdf_structure.py       # PDF 文本和结构提取
│   ├── crop_region.py                # 裁剪图表区域
│   ├── markdown_to_black_white_html.py
│   ├── render_black_white_markdown_pdf.py
│   ├── validate_outputs.py           # 验证 PDF 可搜索性
│   └── finalize_outputs.py          # 清理临时文件
└── references/
    ├── translation-rules.md          # 翻译风格规则
    └── summary-templates.md          # 技术总结模板
```

## 配置

如需修改默认 LLM 或翻译参数，可编辑 `SKILL.md` 中的 prompt 模板。

## License

MIT
