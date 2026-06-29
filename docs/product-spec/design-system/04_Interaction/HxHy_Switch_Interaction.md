# Hx/Hy Switch Interaction — Hx/Hy 切换交互

## 设计目标

V1 整区域 Hx 完成后切 Hy（ADR-0004），UI 清晰标示当前通道。

## 使用场景

扫描前选通道；Hy 前探头 offset 补偿确认。

## 规则

1. PropertyPanel `fieldProbeChannel`：Hx / Hy / Hx+Hy 顺序模式
2. Breadcrumb 显示当前通道
3. Hx+Hy 模式：Hx 完成后 Dialog 或 statusBar 提示切换 Hy
4. 工具菜单「Hx/Hy 校准」独立流程
5. 分析页可切换查看 Hx/Hy/Total pixmap

## Qt

ComboBox + 扫描 scheduler 状态；heatmapLayer 切换 pixmap。

## objectName

`fieldProbeChannel`、`channelSelectorHx`、`channelSelectorHy`。

## 禁止事项

- 禁止 V1 每点切换 Hx/Hy
- 禁止切换通道不更新 Breadcrumb

## 相关

- `../../decision/ADR-0004-HxHy_Strategy.md`
