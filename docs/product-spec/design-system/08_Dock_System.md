# 08 Dock 面板规范

> **历史兼容**：该文档已迁移到 `02_Components/DockPanel.md` 与 `03_Patterns/Parameter_Dock_Pattern.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Dock System

## 设计目标

右侧参数 Dock 为扫描配置主入口；底部辅助 Dock 默认隐藏，通过视图菜单按需调出，避免频谱/日志常驻挤占 PCB 画布。

## 使用场景

- 扫描参数 Accordion（右侧，默认显示）
- 日志、频谱、统计、数据表格（底部，默认隐藏）
- 色带、小地图（画布内嵌，非 QDockWidget）

## Dock 清单

| Dock | objectName | 默认 | 位置 | 默认宽度/高度 |
|---|---|---|---|---|
| 扫描参数 | `scanParamDock` | 显示 | 右侧 | 340 px |
| 日志 | `logDock` | 隐藏 | 底部 | 200 px 高 |
| 频谱 | `spectrumDock` | 隐藏 | 底部 | 240 px 高 |
| 统计 | `statisticsDock` | 隐藏 | 底部 | 180 px 高 |
| 数据表格 | `dataTableDock` | 隐藏 | 底部 | 220 px 高 |

## 行为规则

- **固定**：用户钉住面板，不自动隐藏。
- **自动隐藏**：鼠标离开后面板收至 40px 条（仅右侧参数 Dock 可选）。
- **关闭**：用户点 × 关闭；经视图菜单可再次打开。
- **拖动停靠**：允许左右/底部停靠；**禁止**停靠到顶部覆盖菜单栏。
- **重置布局**：视图菜单「重置布局」恢复 Release 008 默认。

## 扫描参数 Dock 内部结构

Accordion 分组（见 `10_Form_System.md`）：

```text
扫描设置     [展开]
区域设置     [展开]
显示设置     [折叠]
仪表设置     [折叠]
高级设置     [折叠]
```

## 样式规则

| 属性 | 值 |
|---|---|
| 标题栏高 | 32 px |
| 标题背景 | `--color-dock-title-bg` |
| 内容背景 | `--color-bg-panel` |
| 边框 | 1px `--color-border` |
| 标题字号 | 14 px, 600 |

## Qt/PySide6 推荐组件

- `QDockWidget` + `QMainWindow.addDockWidget(Qt.RightDockWidgetArea, ...)`
- 底部 Dock：`Qt.BottomDockWidgetArea`，`setVisible(False)` 初始化
- Accordion：自定义 widget 或 `QToolBox`
- 视图联动：`QAction.toggled` ↔ `dock.setVisible`
- 自动隐藏：自定义 `QDockWidget` 子类或 event filter（Release 010 实现）

## objectName 命名建议

```text
scanParamDock
logDock
spectrumDock
statisticsDock
dataTableDock
scanSettingsGroup
regionSettingsGroup
displaySettingsGroup
instrumentSettingsGroup
advancedSettingsGroup
```

## 禁止事项

- 禁止日志/频谱/统计/数据表格默认 visible。
- 禁止右侧同时堆叠多个全高 Dock 挤占画布低于 70%。
- 禁止在 Dock 内嵌套第二个 QMainWindow。
- 禁止参数 Dock 宽度小于 280px 导致表单不可读（默认 340px）。
- 禁止将项目树或 Region 树放在永久 Dock 替代画布交互（Region 选择走画布 + Breadcrumb）。

## 相关文档

- 线框：`ui-wireframe/06_Dock_System.md`
- 表单：`10_Form_System.md`
- QSS：`qss/dock_widget_qss_guide.md`
