# Loading & Progress Animation — 加载与进度动效

## 设计目标

扫描进度清晰；热力图生成有等待指示但不挡画布。

## 规则

- 扫描中：`statusBarProgressBar` 平滑 value 更新，节流 ≥100ms
- 热力图生成：statusBar「正在生成热力图…」+ 可选 indeterminate 小条在 statusBar 内
- 整图热力图 refresh ≤2fps（扫描中）
- 项目打开：statusBar 忙碌指针，非全屏 spinner

## Qt

`QProgressBar.setValue`；`QApplication.setOverrideCursor(WaitCursor)` 短事务。

## objectName

`statusBarProgressBar`、`scanProgressBar`。

## 禁止事项

- 禁止全屏 modal loading
- 禁止 progress 无点数/时间信息

## 相关

- [Scan_State_Interaction.md](../04_Interaction/Scan_State_Interaction.md)
