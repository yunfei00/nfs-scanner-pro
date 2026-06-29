# 02 字体与排版规范

> **历史兼容**：该文档已迁移到 `01_Foundation/Typography_Tokens.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · Typography

## 设计目标

在工业测试软件场景下保证简体中文可读性、数值对齐精度与信息层级清晰，风格接近 Keysight / R&S 仪器界面而非通用 SaaS 后台。

## 使用场景

- 菜单栏、工具栏、Dock 标题、表单标签
- 状态栏与设备状态栏实时数值
- 画布浮窗（坐标、频率、探头通道）
- 表格中的扫描点数据与频谱读数

## 字体栈

按优先级 fallback：

```text
HarmonyOS Sans SC
Microsoft YaHei UI
Microsoft YaHei
Noto Sans CJK SC
Sans Serif
```

等宽数值（坐标、频率、点数）额外 fallback：

```text
Consolas
Cascadia Mono
Microsoft YaHei UI
monospace
```

## 字号与字重

| 用途 | 字号 | 字重 | 行高 |
|---|---:|---|---:|
| 窗口标题 / 品牌 | 16 | 600 | 24 |
| Dock / 面板标题 | 16 | 600 | 24 |
| 顶部菜单 | 14 | 400 | 20 |
| 工具栏按钮 | 14 | 500 | 20 |
| 左侧导航展开文字 | 14 | 500 | 20 |
| 表单标签 | 13 | 400 | 20 |
| 表单内容 / 输入 | 13 | 400 | 20 |
| 状态栏 | 13 | 400 | 20 |
| 设备状态栏 | 13 | 500 | 20 |
| 画布浮窗 | 13 | 400 | 18 |
| 表格表头 | 13 | 600 | 20 |
| 表格内容 | 13 | 400 | 20 |
| 辅助说明 / 占位 | 12 | 400 | 18 |

## 颜色规则

| 层级 | 颜色令牌 |
|---|---|
| 主文字 | `--color-text-primary` |
| 次级 / 标签 | `--color-text-secondary` |
| 禁用 | `--color-status-idle` |
| 链接 / 可点击 | `--color-primary` |
| 错误提示 | `--color-status-error` |
| 数值高亮（扫描中） | `--color-status-running` |

## 排版规则

- 中文与英文、数字混排时，数字使用等宽字体族显示坐标与频率。
- 长标签在 Dock 内优先省略号截断，不自动换行占用画布空间。
- Breadcrumb 使用 `>` 分隔，单项不超过 24 字符，超出省略。
- 禁止在 PCB 画布中央区域放置大段文字说明。

## Qt/PySide6 推荐组件

| 场景 | 组件 |
|---|---|
| 全局字体 | `QApplication.setFont(QFont(...))` |
| 菜单 / 工具栏 | 继承应用字体，`QMenuBar` / `QToolBar` |
| 表单标签 | `QLabel`，右对齐或顶对齐 |
| 数值显示 | `QLabel` + 等宽 font family |
| 表格 | `QTableView` + 自定义 `QStyledItemDelegate` 对齐数值 |
| 富文本（帮助） | `QTextBrowser`，仅用于帮助对话框 |

## objectName 命名建议

```text
breadcrumbBar
statusBarMessageLabel
statusBarProgressLabel
deviceStatusBar
scanCoordOverlayLabel
dockTitleLabel
formLabel_*
```

## 禁止事项

- 禁止使用小于 12px 的正文（高 DPI 缩放除外，由 Qt 逻辑像素统一处理）。
- 禁止在工具栏使用全大写英文标题风格（非仪器软件惯例）。
- 禁止混用多种无 fallback 的 decorative 字体。
- 禁止在热力图图层上直接绘制大量文字标注，浮窗应放在 Overlay UI Layer。

## 相关文档

- 间距：`03_Spacing_And_Layout.md`
- 旧版合并文档（保留）：`02_Typography_Spacing.md`
