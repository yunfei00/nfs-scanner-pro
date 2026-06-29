# Domain Context — 领域上下文

## 核心领域对象

Project · PCB · Region · Alignment · ScanTask · ScanPoint · Probe · FrequencyData · Heatmap · Analysis · Report · DeviceProfile · DeviceSnapshot · Motion/Spectrum/Camera/Servo

## 关键关系（摘要）

| 关系 | 说明 |
|---|---|
| Project — PCB | 1:1 文件夹工程 |
| Project — Region | 1:N |
| Region — Alignment | 1:0..1，**属 Region** |
| Region — ScanTask | 1:N，**不相等** |
| ScanTask — DeviceSnapshot | 1:1 开始时冻结 |
| ScanTask — Heatmap | 派生，可重算 |
| Analysis — Report | 1:N，只读引用 |

## Hx / Hy

同一 Region 下不同 ScanTask；整区 Hx 后整区 Hy；HxHyCalibration 影响 Alignment 是否「需重新确认」。

## DeviceProfile vs DeviceSnapshot

- **Profile**：系统级模板，Settings 管理
- **Snapshot**：ScanTask 时刻冻结，报告审计用

## Scan 七态（UI 须对齐）

未就绪 → 准备就绪 → 扫描中 ⇄ 暂停 → 停止中 → 已完成 / 错误

## 命名

Sample→**PCB**，Scan→**ScanTask**

## 细节入口

- [domain/README.md](../../docs/product-spec/domain/README.md)
- [domain/01_Overview/Object_Relationships.md](../../docs/product-spec/domain/01_Overview/Object_Relationships.md)
- [domain/04_State_Machines/Scan_State_Machine.md](../../docs/product-spec/domain/04_State_Machines/Scan_State_Machine.md)

## Registry

[spec/Registry/Domain.yaml](../Registry/Domain.yaml)
