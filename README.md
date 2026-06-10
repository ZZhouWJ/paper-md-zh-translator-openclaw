# paper-md-zh-translator (OpenClaw)

OpenClaw 版本的论文 Markdown 中文翻译 Skill。

## 功能

将可提取文本的英文生物医学论文翻译为可搜索的简体中文 PDF 和技术总结 PDF。

适合处理 biology、biomedical、bioinformatics、computational biology、genomics、protein engineering、omics 等生命科学论文。

## 工作流程

对于每个输入 PDF，最终交付 3 个文件：
- `<basename>.pdf` — 原 PDF（不变）
- `<basename>_zh.pdf` — 可搜索的中文重排版 PDF
- `<basename>_summary.pdf` — 中文技术总结 PDF

## 依赖

```bash
pip install pypdf pillow reportlab
```

macOS:
```bash
brew install poppler
```

Linux:
```bash
sudo apt install poppler-utils
```

## 使用方法

将此 skill 目录放入 OpenClaw workspace skills 目录：

```bash
cp -r paper-md-zh-translator ~/.openclaw/workspace/skills/
```

然后在 OpenClaw 中提供 PDF 路径并要求翻译即可。

## 目录结构

```
paper-md-zh-translator/
├── SKILL.md                    # OpenClaw skill 定义
├── scripts/
│   ├── crop_region.py          # 裁剪图表区域
│   ├── extract_pdf_structure.py # 提取 PDF 结构和文本
│   ├── finalize_outputs.py     # 清理临时文件
│   ├── markdown_to_black_white_html.py
│   ├── render_black_white_markdown_pdf.py
│   └── validate_outputs.py
└── references/
    ├── summary-templates.md      # 总结模板
    └── translation-rules.md     # 翻译规则
```

## 论文结构

翻译时保留：
- 标题、摘要、关键词
- 正文（引言、方法、结果、讨论、结论）
- Figure/Table 标签和图注

不翻译：
- References
- Acknowledgements、Funding
- Data availability、Code availability
- Supplementary information 等 back matter

## License

MIT
