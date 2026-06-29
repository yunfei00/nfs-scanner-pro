# MenuBar — 菜单栏组件

## 设计目标

系统级入口：文件管项目、视图调 Dock、设置/帮助在顶栏。

## 使用场景

全局菜单；项目 CRUD；视图面板 toggles。

## 尺寸/颜色/状态规则

高 32px；背景 `color.bg.app`；项 padding 6×12；分隔线 `color.border.divider`。结构见 `05_Menu_System` 历史文档。

```text
文件  编辑  视图  工具  设置  帮助
```

## Qt/PySide6 推荐组件

`QMenuBar`、`QMenu`、`QAction`（checkable 用于视图）；快捷键 `QKeySequence`。

## objectName 命名建议

```text
menuBar
menuFile
menuView
actionNewProject
actionSaveProject
actionShowLogDock
actionResetLayout
```

## 禁止事项

- 禁止项目/扫描页切换放菜单
- 禁止新建/打开项目放工具栏
- 禁止设置进左侧导航

## 相关文档

- [../03_Patterns/View_Menu_Dock_Pattern.md](../03_Patterns/View_Menu_Dock_Pattern.md)
- 历史：`../05_Menu_System.md`
