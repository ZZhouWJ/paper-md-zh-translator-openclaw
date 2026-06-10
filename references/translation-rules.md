# Translation Rules

## Body Segmentation

Treat the main body as the translatable part of the paper. It usually includes:

- Title
- Abstract
- Keywords
- Introduction / Background
- Methods / Materials and methods
- Results
- Discussion
- Conclusion
- Limitations when it is part of the paper's main argument

Stop translating when the paper enters back matter or references. Keep these sections in English:

- Acknowledgements / Acknowledgments
- Funding
- Data availability
- Code availability
- Materials availability
- Author contributions
- Competing interests / Conflict of interest
- Ethics declarations
- Supplementary information
- References / Bibliography

Append the English back matter and References after the Chinese body.

## Chinese Translation Style

- Use faithful Simplified Chinese academic prose.
- Preserve section numbers from the paper, such as `1`, `2.1`, or `3.2.4`.
- Keep canonical English names for models, datasets, software, genes, proteins, databases, benchmarks, metrics, URLs, DOIs, and citation keys.
- Translate figure/table references naturally, but preserve source labels when they appear as labels. Example: `Figure 1 shows...` can become `Figure 1 显示...`.
- Preserve citation forms such as `(Smith et al., 2024)` and `[12]`.
- Preserve inline formulas and variables as symbol text.
- Do not invent missing details or expand beyond the source paper.

## Markdown Layout

Use this structure for translated paper Markdown:

```markdown
# <中文标题>

**原文标题**：<English title>
**论文类型**：<研究型论文 / 综述 / 调查 / 观点 / 其他>

## 摘要

<Chinese abstract>

## 关键词

<Chinese keywords, if present>

## 1 引言

<translated body>

![Figure 1](assets/figure_001.png)

**Figure 1. <中文图注，保留 Figure 1 标签>**

## Untranslated Back Matter

<English back matter>

## References

<English references>
```

If an image crop already contains the original English caption, still write the translated Chinese caption in Markdown.

## Captions

Translate captions, but keep the original English label:

- `Figure 1. CodonMPNN overview.` -> `Figure 1. CodonMPNN 概览。`
- `Table 2. Benchmark results.` -> `Table 2. 基准测试结果。`

Do not translate text inside the figure/table image itself.

## Figure and Table Placement

Place each figure/table at the first translated paragraph that cites it. Detect references such as:

- `Figure 1`, `Fig. 1`, `Figures 1 and 2`
- `Table 1`, `Tables 1-3`

If no citation exists, place it near the original section by source order. Record this in `work/figure_table_map.json`.

## Display Equations

- Inline formulas stay as text.
- Display equations on their own line are cropped as images and inserted near the source location.
- Use `assets/equation_001.png`, `assets/equation_002.png`, etc.

## Black-On-White Constraint

Markdown and rendered PDFs must use only white backgrounds and black text. Do not use colored headings, colored tables, colored highlights, tinted boxes, or decorative elements.
