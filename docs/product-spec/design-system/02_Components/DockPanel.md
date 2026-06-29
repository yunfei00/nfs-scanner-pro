# DockPanel — Dock 面板组件

## 设计目标

右侧参数默认显示；底部日志/频谱/统计/表格默认隐藏。

## 使用场景

scanParamDock、logDock、spectrumDock、statisticsDock、dataTableDock。

## 尺寸/颜色/状态规则

参数 Dock 宽 340px，收起 40px；标题高 32px；背景 `color.bg.panel`。行为：固定 / auto-hide / 关闭 / 拖放停靠（禁顶栏）。

| Dock | 默认 | 区域 |
|---|---|---|
| scanParamDock | 显示 | 右 |
| log/spectrum/statistics/dataTable | 隐藏 | 底 |

## Qt/PySide6 推荐组件

`QDockWidget`；`addDockWidget`；`setVisible(False)` 初始化隐藏 Dock。

## objectName 命名建议

```text
scanParamDock
logDock
spectrumDock
statisticsDock
dataTableDock
```

## 禁止事项

- 禁止辅助 Dock 默认 visible
- 禁止 dock 顶栏停靠
- 禁止宽 < 280px

## 相关文档

- [../04_Interaction/Dock_Interaction.md](../04_Interaction/Dock_Interaction.md)
- [../05_Animation/Dock_Animation.md](../05_Animation/Dock_Animation.md)
- 历史：`../08_Dock_System.md`
