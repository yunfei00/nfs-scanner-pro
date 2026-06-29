# Alignment State Machine — 对齐状态机

> Alignment **属于 Region**（ADR-0019），非独立一级对象。状态存于 `alignment.json.status`。

## 1. 状态列表

| 内部 ID | 中文名 | 说明 |
|---|---|---|
| `NotAligned` | 未对齐 | 无有效映射 |
| `CoarseAligned` | 粗对齐 | 用户初步框选，未确认 |
| `Aligned` | 已对齐 | 已确认，可叠加热力图 |
| `ReconfirmRequired` | 需重新确认 | Hx/Hy 切换或 PCB 图变更后待确认 |
| `Invalid` | 失效 | 变换不可用，仅普通热力图 |

---

## 2. 状态说明

### 未对齐
可 ScanTask（普通热力图）；画布无叠加矩形或矩形未绑定坐标。

### 粗对齐
编辑中（Draft）。允许保存草稿，不可用于正式 Report 叠加。

### 已对齐
Valid。热力图与 PCB 图对齐显示。Report 可用叠加图。

### 需重新确认
**Hx / Hy 切换**：若存在有效 **HxHyCalibration** 且偏移在阈值内 → 可**保持已对齐**；若无补偿或 **offset 超阈值** → 本状态，须用户点「确认对齐」回到已对齐。

PCB 照片更新、Region 起终点大改 → 亦进入本状态。

### 失效
用户禁用对齐或矩阵奇异。回退普通热力图模式。

---

## 3. 状态转换表

| 从 | 事件 | 到 |
|---|---|---|
| 未对齐 | 开始编辑 | 粗对齐 |
| 粗对齐 | 用户确认 | 已对齐 |
| 粗对齐 | 放弃 | 未对齐 |
| 已对齐 | Hy切换且补偿OK | 已对齐 |
| 已对齐 | Hy切换且无补偿/超阈 | 需重新确认 |
| 需重新确认 | 用户确认 | 已对齐 |
| 已对齐 | PCB图变更 | 需重新确认 |
| * | 用户禁用 | 失效 |
| 失效 | 重新标定 | 粗对齐 |

---

## 4. 允许动作

| 状态 | 允许 |
|---|---|
| 未对齐 | 扫描、粗标定 |
| 粗对齐 | 拖矩形、保存草稿、确认 |
| 已对齐 | 叠加显示、分析、报告 |
| 需重新确认 | 预览、确认、重新标定 |
| 失效 | 普通热力图、重新对齐 |

---

## 5. 禁止动作

- 未确认粗对齐用于 signed Report
- 静默忽略 Hx/Hy 超阈偏移
- 在 Project 级保存 Alignment 替代 Region

---

## 6. UI 表现

| 状态 | 画布 | 工具栏对齐 |
|---|---|---|
| 未对齐 | 无叠加或虚线框 | 可用 |
| 粗对齐 | 虚线矩形 | 高亮 |
| 已对齐 | 实线+叠加 | 可用 |
| 需重新确认 | 黄框+提示 | 高亮+Badge |
| 失效 | 无叠加 | 可用 |

statusBar 可选：`对齐：需重新确认（Hy 偏移未校准）`

---

## 7. 日志记录

`AlignmentUpdated` 事件；`logs/alignment_{regionId}.log`

---

## 8. 错误恢复

[Alignment_Error_Recovery.md](../06_Error_Recovery/Alignment_Error_Recovery.md)

---

## 相关 ADR

[ADR-0019](../../decision/ADR-0019-Region-Alignment-Ownership.md)

## Hx/Hy 与偏移补偿（摘要）

```text
切换 Hy 前读取 HxHyCalibration
  ├─ valid 且 |offset| ≤ threshold → 保持「已对齐」
  └─ 否则 → 「需重新确认」
```

阈值字段：`hxhy_calibration.json.thresholdMm`（Release 010 实现常量）
