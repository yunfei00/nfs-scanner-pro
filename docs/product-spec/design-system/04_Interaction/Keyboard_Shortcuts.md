# Keyboard Shortcuts — 键盘快捷键

## 设计目标

高频操作可键盘完成，符合 Windows 工业软件习惯。

## 使用场景

文件、视图、扫描控制。

## 快捷键表

| 动作 | 快捷键 | 组件 |
|---|---|---|
| 保存项目 | Ctrl+S | MenuBar |
| 打开项目 | Ctrl+O | MenuBar |
| 新建项目 | Ctrl+N | MenuBar |
| 开始扫描 | F5 | ToolBar |
| 停止扫描 | Esc / Shift+F5 | ToolBar |
| 全屏 | F11 | 视图菜单 |
| 重置布局 | — | 视图菜单（无默认键，可 Settings 配置） |
| 画布放大 | Ctrl++ | Canvas |
| 画布缩小 | Ctrl+- | Canvas |
| 画布适应 | Ctrl+0 | Canvas |

## Qt

`QAction.setShortcut(QKeySequence)`；`QShortcut` 在 Canvas focus 时。

## 禁止事项

- 禁止 Esc 仅关闭 Dialog 而扫描中忽略停止
- 禁止与系统全局冲突未文档化

## 相关

- [Scan_State_Interaction.md](Scan_State_Interaction.md)
