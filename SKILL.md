---
name: paper-md-zh-translator
description: Translate extractable-text English biology/biomedical/bioinformatics papers into searchable Simplified Chinese PDF with summary. Use when user provides a PDF path and wants a Chinese paper PDF.
---

# Paper Markdown Chinese Translator

将可提取文本的英文生物医学论文翻译为中文 PDF 和技术总结 PDF。

## 依赖安装

首次使用时需安装依赖：
```bash
pip install pypdf pillow reportlab
```

macOS 需安装 poppler（pdftoppm）：
```bash
brew install poppler
```

Linux：
```bash
sudo apt install poppler-utils
```

## 工作流程

对于每个输入的 PDF，最终交付 **3 个文件**：
- `<basename>.pdf` — 原 PDF（不变）
- `<basename>_zh.pdf` — 可搜索的中文重排版 PDF
- `<basename>_summary.pdf` — 中文技术总结 PDF

## 核心步骤

### 1. 创建工作目录
```bash
mkdir -p <workspace>/papers/<pdf-basename>/
cp <原始PDF路径> <workspace>/papers/<pdf-basename>/<basename>.pdf
```

### 2. 文本提取检测
```bash
python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/extract_pdf_structure.py \
  --pdf "<workspace>/papers/<basename>/<basename>.pdf" \
  --out "<workspace>/papers/<basename>/work/extracted_text.json" \
  --references-out "<workspace>/papers/<basename>/work/references.txt" \
  --back-matter-out "<workspace>/papers/<basename>/work/untranslated_back_matter.md"
```

**如果脚本输出 `ok: false`（PDF 是扫描件或文本量不足），立即告知用户不适合此流程。**

### 3. 读取翻译规则
读取 `~/.openclaw/workspace/skills/paper-md-zh-translator/references/translation-rules.md`

### 4. 裁剪图表区域
使用 `extracted_text.json` 和 PDF 预览，定位 figure、table、display equation 的页面和坐标：

```bash
python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/crop_region.py \
  --pdf "<workspace>/papers/<basename>/<basename>.pdf" \
  --page <页码> \
  --bbox "x0,y0,x1,y1" \
  --out "<workspace>/papers/<basename>/assets/figure_001.png"
```

坐标为 PDF points（左下坐标系）。

### 5. 翻译正文
只翻译：标题、摘要、关键词、正文章节、图注表注。

**不翻译**：References、Acknowledgements、Funding、Data availability、Supplementary information 等 back matter。

### 6. 生成预览 HTML
```bash
python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/markdown_to_black_white_html.py \
  --md "<workspace>/papers/<basename>/<basename>_zh.md" \
  --out "<workspace>/papers/<basename>/work/<basename>_zh.html"
```

### 7. 渲染 PDF
```bash
python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/render_black_white_markdown_pdf.py \
  --md "<workspace>/papers/<basename>/<basename>_zh.md" \
  --out "<workspace>/papers/<basename>/<basename>_zh.pdf"

python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/render_black_white_markdown_pdf.py \
  --md "<workspace>/papers/<basename>/<basename>_summary.md" \
  --out "<workspace>/papers/<basename>/<basename>_summary.pdf"
```

### 8. 生成技术总结
读取 `~/.openclaw/workspace/skills/paper-md-zh-translator/references/summary-templates.md`

研究论文用固定格式：
- 输入输出
- 训练/验证/测试数据集
- 损失函数
- 训练目标

综述用：
- 研究领域划分
- 代表性方法对比与演进
- 数据资源与评价标准
- 当前痛点与挑战
- 未来趋势

### 9. 验证与清理
```bash
python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/validate_outputs.py \
  --folder "<workspace>/papers/<basename>" \
  --basename "<basename>" \
  --stage working

python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/finalize_outputs.py \
  --folder "<workspace>/papers/<basename>" \
  --basename "<basename>" \
  --confirm-delete-intermediates

python ~/.openclaw/workspace/skills/paper-md-zh-translator/scripts/validate_outputs.py \
  --folder "<workspace>/papers/<basename>" \
  --basename "<basename>" \
  --stage final
```

## 输出格式

最终文件夹必须只包含：
```
<pdf-basename>/
  <basename>.pdf
  <basename>_zh.pdf
  <basename>_summary.pdf
```

## 风格要求

- A4
- 单栏
- 白底黑字
- 无彩色标题/背景/边框
- 图表/公式图片可保留原色

## 触发方式

用户发送论文 PDF 路径并要求翻译时自动触发，例如：
- "翻译这篇论文：/path/to/paper.pdf"
- "把这个 PDF 翻译成中文"
- 用户直接提供 PDF 文件
