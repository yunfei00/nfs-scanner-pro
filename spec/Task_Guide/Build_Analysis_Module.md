# Build Analysis Module — 分析页

## 任务目标

分析视图：频率数据、对比、统计面板（Mock 数据）。

## 开始前必须阅读

- [spec/AI_INDEX.md](../AI_INDEX.md)
- [spec/Registry/Domain.yaml](../Registry/Domain.yaml)
- [Analysis.md](../../docs/product-spec/workflow/Analysis.md)

## 不要阅读的内容

- 报告导出实现细节（见 Build_Report）

## 允许修改的目录

- 分析页 UI

## 禁止修改的目录

- `docs/product-spec/domain/02_Core_Objects/Analysis.md`（除非文档任务）

## 实现步骤

1. 分析结果列表 Mock。
2. 与 ScanTask / Heatmap 引用关系展示。

## 验收标准

- [ ] 不修改 raw ScanTask 数据

## 常见错误

- 分析页改写成第二个扫描页

## 推荐 commit message

```
feat(ui): add analysis module shell
```
