# Image Evidence Policy

Status: Active baseline

## Principle

ITR 附件中的图片可能是 Knowledge 的关键 Evidence，不能只处理文字字段。

例如硬件版本差异、接口/线缆位置、主板区别、烧录步骤、部件外观识别等知识，仅靠文字可能不足以让 PIE 正确理解和复用。

## Handling modes

当图片对知识有实际价值时，至少采用以下一种方式：

1. 在 Knowledge 的参考图片字段中保留可追溯图片；或
2. 对图片中可稳定验证的关键差异做文字事实描述；
3. 在合适情况下两者同时保留。

## Image description rule

图片文字描述必须限制在图片实际可观察内容，不应从外观直接推断未被 Evidence 支持的电气功能、兼容性、根因或维修结论。

## Missing image

如果原 ITR 明确依赖图片才能理解，而 KB 的参考图片为空：

- 应视为潜在知识完整性问题；
- 优先回溯 ITR 附件；
- 无法安全带入图片时，可以保存准确的视觉差异描述，并记录来源；
- 不应凭空生成“参考图”。

## Batch processing

图片分析不应只针对某一个案例做特例。批量 Knowledge 沉淀时，应识别哪些条目需要图像 Evidence，并统一进入相同审核规则。