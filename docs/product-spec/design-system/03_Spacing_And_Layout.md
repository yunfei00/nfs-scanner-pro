# 03 间距与布局规范

> **历史兼容**：该文档已迁移到 `01_Foundation/Spacing_Tokens.md` 与 `03_Patterns/MainWindow_Pattern.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Spacing & Layout

## 设计目标

以 8px 栅格统一全产品间距，确保 PCB 画布占据 ≥70% 主区域宽度，辅助面板不挤压工作区，布局行为与 Release 008 线框完全一致。

## 使用场景

- 主窗口各区域尺寸与边距
- Dock 内 Accordion 分组间距
- 表单字段、工具栏按钮、导航项 padding
- 对话框内容与按钮区布局

## 8px 栅格令牌

| 令牌 | 值 | 典型用途 |
|---|---:|---|
| `--space-1` | 4px | 图标与文字间距、紧凑列表 |
| `--space-2` | 8px | 表单项内边距、导航项 padding |
| `--space-3` | 12px | Dock 分组间距 |
| `--space-4` | 16px | 面板内边距、对话框边距 |
| `--space-5` | 24px | 区块分隔 |
| `--space-6` | 32px | 大区块、对话框按钮区上间距 |

## 主窗口固定尺寸（继承 Release 008）

| 区域 | 尺寸 |
|---|---:|
| 窗口基准 | 1920 × 1080 |
| 顶部菜单栏 | 32 px |
| 顶部工具栏 | 56 px |
| 设备状态栏 | 40 px |
| 左侧导航收起 | 56 px |
| 左侧导航展开 | 180 px |
| 右侧参数 Dock 默认宽 | 340 px |
| 右侧参数 Dock 收起 | 40 px |
| 底部状态栏 | 32 px |
| 主画布最小宽度占比 | ≥ 70% |

## 布局结构

```text
QMainWindow
├── QMenuBar                    (fixed 32)
├── QToolBar                    (fixed 56)
├── CentralWidget
│   ├── DeviceStatusBar         (fixed 40, full width)
│   └── ContentRow
│       ├── LeftNavigationBar   (56 ↔ 180)
│       ├── GraphicsWorkspace   (stretch, min 70%)
│       └── RightDockArea       (340 / auto-hide 40)
├── QDockWidget (bottom, hidden by default)
└── QStatusBar                  (fixed 32)
```

## 间距规则

- 工具栏图标按钮：36×36 可点区域，图标 20×20，间距 `--space-2`。
- 左侧导航项：高度 48px，图标 24×24，展开后左 padding `--space-4`。
- Dock Accordion 组标题：高度 40px，内容区 padding `--space-4`。
- 表单行：标签与控件垂直间距 `--space-1`，行间距 `--space-3`。
- 对话框：最小宽 480px，内容 margin `--space-5`，按钮区距内容 `--space-6`。

## Qt/PySide6 推荐组件

| 区域 | 组件 | 布局 |
|---|---|---|
| 主窗口 | `QMainWindow` | 内置 dock 区域 |
| 中央区 | `QWidget` + `QHBoxLayout` | 导航 + 画布 + Dock 占位 |
| 导航 | 自定义 `QWidget` | `QVBoxLayout` |
| 画布 | `QGraphicsView` | `setSizePolicy(Expanding, Expanding)` |
| Dock | `QDockWidget` | `QMainWindow.addDockWidget` |
| 间距 | `QLayout.setContentsMargins` / `setSpacing` | 引用栅格常量 |

## objectName 命名建议

```text
mainWindow
centralWidget
leftNavigationBar
graphicsWorkspace
rightDockArea
deviceStatusBar
scanParamDock
```

## 禁止事项

- 禁止用固定像素宽度挤压画布低于 70%（Dock 展开时允许临时缩小，但默认布局必须满足）。
- 禁止在 CentralWidget 外再套多层装饰性 margin 浪费空间。
- 禁止左侧导航默认展开为 180px（必须默认 56px 图标模式）。
- 禁止将项目入口或设置放入左侧导航占用宽度。
- 禁止底部 Dock 默认全部显示（日志/频谱/统计/数据表格默认隐藏）。

## 相关文档

- 线框：`ui-wireframe/01_Main_Window_1920x1080.md`
- Dock：`08_Dock_System.md`
- 导航：`07_Navigation_System.md`
