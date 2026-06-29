# 06 工具栏规范

> **历史兼容**：该文档已迁移到 `02_Components/ToolBar.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Toolbar System

## 设计目标

工具栏只承载**扫描工作流高频动作**，保持 56px 固定高度，不重复菜单与导航职能，风格紧凑如 R&S / Keysight 仪器顶部快捷区。

## 使用场景

- 扫描页默认可见的全局快捷操作
- 画布辅助：网格、测量
- 扫描控制：开始、停止

## 默认按钮（固定顺序）

```text
开始扫描 | 停止扫描 | 拍照 | 区域对齐 | 网格 | 测量
```

| 按钮 | 默认显示 | 类型 | 说明 |
|---|---|---|---|
| 开始扫描 | 是 | 主操作 | 主蓝强调 |
| 停止扫描 | 是 | 危险 | 红/灰，扫描中激活 |
| 拍照 | 是 | 普通 | 相机可选 |
| 区域对齐 | 是 | 普通 | 扫描前常用 |
| 网格 | 是 | 切换 | checkable |
| 测量 | 是 | 切换 | checkable |
| 连接设备 | 否 | — | 经设备状态栏或工具菜单 |
| 新建/打开/保存项目 | 否 | — | 文件菜单 |

## 尺寸规则

| 属性 | 值 |
|---|---|
| 工具栏高度 | 56 px |
| 按钮可点区域 | 36 × 36 |
| 图标 | 20 × 20 |
| 按钮间距 | 8 px |
| 组间距 | 16 px（`|` 分隔组） |
| 背景 | `--color-toolbar-bg` |
| 底部分隔线 | 1px `--color-divider` |

## 状态规则

| 按钮 | 启用条件 |
|---|---|
| 开始扫描 | 项目已打开、Region 已选、设备就绪、未在扫描 |
| 停止扫描 | 扫描运行中或暂停 |
| 拍照 | 项目已打开（相机可选） |
| 区域对齐 | 项目已打开、有样品图或 Region |
| 网格 / 测量 | 始终可用（画布模式） |

## Qt/PySide6 推荐组件

- `QToolBar` + `QToolButton`（`Qt.ToolButtonTextBesideIcon` 仅当需要文字，默认仅图标）
- 分隔：`QToolBar.addSeparator()`
- 危险按钮：独立 objectName + QSS `danger` 属性或 class
- 切换：`setCheckable(True)` 同步画布 Overlay 层

## objectName 命名建议

```text
mainToolBar
toolbarStartScanButton
toolbarStopScanButton
toolbarCaptureButton
toolbarAlignButton
toolbarGridButton
toolbarMeasureButton
```

## 禁止事项

- 禁止工具栏高度随内容换行增长。
- 禁止在工具栏显示项目名称或 Breadcrumb（Breadcrumb 在画布区顶部）。
- 禁止工具栏按钮超过 8 个默认可见项（扩展功能进菜单）。
- 禁止用工具栏替代左侧页面导航。

## 相关文档

- 线框：`ui-wireframe/03_Top_Menu_And_Toolbar.md`
- 图标：`04_Icon_System.md`
