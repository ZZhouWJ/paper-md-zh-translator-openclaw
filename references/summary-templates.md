# Summary Templates

Use Simplified Chinese. Keep English method, dataset, gene/protein, software, benchmark, metric, DOI, URL, and citation names when they are canonical.

## Research Article Template

```markdown
# <论文标题>：中文技术总结

**论文信息**：<作者；期刊/会议；年份；DOI/URL>
**论文类型**：研究型论文
**一句话概括**：<用 1-2 句话说明核心贡献>

## 1. 输入输出

| 模型/方法/任务 | 输入 | 输出 | 关键预处理或约束 | 备注 |
|---|---|---|---|---|
| <name> | <input> | <output> | <preprocess> | <notes> |

## 2. 训练 / 验证 / 测试数据集

| 模型/任务 | 训练集 | 验证集 | 测试集/留出集 | 划分策略 | 数据规模 | 数据来源 |
|---|---|---|---|---|---|---|
| <name> | <train> | <validation> | <test> | <split> | <size> | <source> |

## 3. 损失函数

| 模型/任务 | 损失函数 | 公式/符号 | 优化目标含义 | 论文是否明确给出 |
|---|---|---|---|---|
| <name> | <loss> | <formula> | <meaning> | <yes/no> |

## 4. 训练目标

| 模型/任务 | 训练目标 | 监督信号 | 评价指标 | 主要结论 |
|---|---|---|---|---|
| <name> | <objective> | <signal> | <metrics> | <findings> |
```

## Review / Survey / Perspective Template

```markdown
# <论文标题>：中文综述总结

**论文信息**：<作者；期刊/会议；年份；DOI/URL>
**论文类型**：综述/调查/观点论文
**一句话概括**：<用 1-2 句话说明综述范围和核心判断>

## 1. 研究领域划分

| 子领域 | 研究问题 | 典型输入/输出 | 代表任务 |
|---|---|---|---|
| <area> | <problem> | <io> | <tasks> |

## 2. 代表性方法对比与演进

| 阶段/方法族 | 代表方法 | 核心思想 | 优点 | 局限 | 演进关系 |
|---|---|---|---|---|---|
| <stage> | <methods> | <idea> | <pros> | <cons> | <evolution> |

## 3. 数据资源与评价标准

| 数据集/资源/基准 | 覆盖范围 | 常用指标 | 适用任务 | 注意事项 |
|---|---|---|---|---|
| <dataset> | <scope> | <metrics> | <tasks> | <notes> |

## 4. 当前痛点与挑战

| 挑战 | 原因 | 对研究/应用的影响 | 论文提到的缓解方向 |
|---|---|---|---|
| <challenge> | <cause> | <impact> | <direction> |

## 5. 未来趋势

| 趋势 | 可能方向 | 需要解决的问题 | 预期影响 |
|---|---|---|---|
| <trend> | <direction> | <open problems> | <impact> |
```

## Detail Policy

- Prefer faithful technical detail over broad paraphrase.
- If a required field is absent, write `论文未明确说明` rather than guessing.
- For multiple models, tasks, datasets, or experimental settings, use one row per item.
- Include section/page hints when they help verification.
- The summary PDF must be black text on white background and searchable.
