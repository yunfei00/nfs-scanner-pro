# Build Scan Module — 扫描页

## 任务目标

扫描工作台：区域编辑、对齐入口、扫描控制 UI；Mock ScanTask 状态。

## 开始前必须阅读

- [spec/AI_INDEX.md](../AI_INDEX.md)
- [spec/Registry/Domain.yaml](../Registry/Domain.yaml)
- [spec/Registry/Workflow.yaml](../Registry/Workflow.yaml)
- [Scan_State_Machine.md](../../docs/product-spec/domain/04_State_Machines/Scan_State_Machine.md)
- [05_Scan_Page_Wireframe.md](../../docs/product-spec/ui-wireframe/05_Scan_Page_Wireframe.md)

## 不要阅读的内容

- 运动控制底层协议（除非已实现）

## 允许修改的目录

- 扫描页 UI、Mock ScanTask

## 禁止修改的目录

- ADR 已定 Scan 七态定义

## 实现步骤

1. 画布 + 区域 Mock。
2. 扫描按钮与七态 property。
3. 参数 Dock 联动。

## 验收标准

- [ ] 未就绪态禁用扫描
- [ ] 暂停/停止 UI 与状态机一致

## 常见错误

- 跳过 Alignment 直接扫描

## 推荐 commit message

```
feat(ui): add scan workbench with mock ScanTask states
```
