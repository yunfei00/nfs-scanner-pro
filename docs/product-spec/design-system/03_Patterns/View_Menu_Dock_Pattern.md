# View Menu Dock Pattern — 视图菜单与 Dock 联动

## 设计目标

辅助面板经视图菜单 checkable 动作显隐，与 Dock visible 双向同步。

## 使用场景

显示参数/日志/频谱/统计/数据表格/色带/小地图；重置布局。

## 规则

| 菜单项 | Dock/Overlay | 默认 |
|---|---|---|
| 显示参数面板 | scanParamDock | 勾选 |
| 显示日志面板 | logDock | 未勾选 |
| 显示频谱面板 | spectrumDock | 未勾选 |
| 显示统计面板 | statisticsDock | 未勾选 |
| 显示数据表格 | dataTableDock | 未勾选 |

重置布局 → 恢复 Release 008 默认。

## Qt

`QAction.toggled` ↔ `QDockWidget.setVisible`。

## 禁止事项

- 禁止辅助 Dock 启动时 visible=True

## 相关

- `../02_Components/MenuBar.md`
