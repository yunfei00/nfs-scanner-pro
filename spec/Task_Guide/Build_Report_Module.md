# Build Report Module — 报告页

## 任务目标

报告预览与导出 UI；Mock Report 对象。

## 开始前必须阅读

- [spec/AI_INDEX.md](../AI_INDEX.md)
- [spec/Registry/Domain.yaml](../Registry/Domain.yaml)
- [Report.md](../../docs/product-spec/domain/02_Core_Objects/Report.md)
- [Export_Report.md](../../docs/product-spec/workflow/Export_Report.md)

## 不要阅读的内容

- 全量 workflow

## 允许修改的目录

- 报告页 UI、Mock 导出

## 禁止修改的目录

- 报告模板 ADR（若后续单独 Release）

## 实现步骤

1. 报告列表与预览区。
2. Mock 导出路径选择。

## 验收标准

- [ ] Report 生命周期与 domain 一致

## 常见错误

- 报告数据写回 ScanTask raw

## 推荐 commit message

```
feat(ui): add report module with mock export
```
