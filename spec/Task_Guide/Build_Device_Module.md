# Build Device Module — 设备页

## 任务目标

设备模块 UI：连接状态、DeviceProfile 展示、Mock 连接/断开。

## 开始前必须阅读

- [spec/AI_INDEX.md](../AI_INDEX.md)
- [spec/Registry/Domain.yaml](../Registry/Domain.yaml)
- [spec/Registry/Workflow.yaml](../Registry/Workflow.yaml)
- [Device_State_Machine.md](../../docs/product-spec/domain/04_State_Machines/Device_State_Machine.md)
- [04_Device_Status_Bar.md](../../docs/product-spec/ui-wireframe/04_Device_Status_Bar.md)

## 不要阅读的内容

- 真实 SDK 文档

## 允许修改的目录

- 设备页 UI 与 Mock service

## 禁止修改的目录

- 硬件驱动（本阶段 Mock）

## 实现步骤

1. 设备列表与状态指示。
2. Mock Connect_Devices 流程。
3. 状态栏与页面联动。

## 验收标准

- [ ] 状态与 Device 状态机 UI 映射一致
- [ ] Camera 可选，离线有明确提示

## 常见错误

- Camera 离线禁用整个扫描入口

## 推荐 commit message

```
feat(ui): add device module with mock connectivity
```
