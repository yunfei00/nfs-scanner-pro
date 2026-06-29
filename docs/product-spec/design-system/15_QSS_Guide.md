# 15 QSS 样式总指南

> **历史兼容**：该文档已迁移到 `06_QSS/README.md`，保留用于历史兼容。请参阅 [design-system/README.md](README.md)。

> Release 009 Enterprise Design System · QSS Guide

## 设计目标

通过 Qt Style Sheets 统一深色工业主题，使 PySide6 实现不依赖系统原生浅色控件，样式可维护、可令牌化，便于 Release 010 组件库复用。

## 使用场景

- 应用启动时加载全局 QSS
- 按组件类型分文件维护（见 `qss/` 子目录）
- 与 C++ / Python 常量表共享颜色令牌名

## 文件组织

```text
design-system/qss/
├── dark_theme_tokens.qss.md    # 令牌定义（文档化，非直接加载）
├── main_window_qss_guide.md
├── dock_widget_qss_guide.md
├── button_qss_guide.md
└── form_qss_guide.md
```

Release 010 实现时合并为：

```text
resources/styles/
├── tokens.qss
├── main_window.qss
├── dock.qss
├── buttons.qss
├── forms.qss
└── app.qss          # @import 汇总
```

## 加载策略

1. `QApplication.setStyle("Fusion")`
2. 设置全局 `QFont`（见 `02_Typography.md`）
3. 读取 `app.qss` 字符串 `app.setStyleSheet(...)`
4. 禁止对单个控件散落硬编码 hex，优先 objectName 选择器

## 选择器约定

| 模式 | 示例 |
|---|---|
| 全局 | `QWidget { background: #07111D; color: #EAF2FF; }` |
| objectName | `QWidget#scanParamDock { ... }` |
| 属性 | `QPushButton[danger="true"] { ... }` |
| 状态 | `QPushButton:disabled { ... }` |
| 子控件 | `QDockWidget::title { ... }` |

## 与令牌关系

所有颜色、圆角、高度优先引用 `dark_theme_tokens.qss.md` 中 `--token` 名；QSS 不支持 CSS 变量时，Release 010 用 Python 生成 QSS 或使用 `@替换` 预处理。

## Qt/PySide6 推荐实践

- Fusion + 自定义 QSS 覆盖
- `QWidget.setAttribute(Qt.WA_StyledBackground, True)` 用于自定义 panel
- 避免 `setStyleSheet` 在热路径重复调用
- 大控件树变更后无需 unpolish，初始加载一次即可
- 测试高 DPI：`QT_ENABLE_HIGHDPI_SCALING=1`

## objectName 与 QSS 映射

objectName 是 QSS 主锚点，完整清单见 `qt-spec/02_Qt_Object_Names.md` 与各子系统规范。

## 禁止事项

- 禁止不加载 QSS 依赖 Windows 11 浅色原生样式。
- 禁止在每个 `__init__` 内联 50 行 setStyleSheet。
- 禁止 QSS 中使用 `url()` 引用未打包资源。
- 禁止为修复单个按钮复制整份 global stylesheet。
- 禁止 QSS 中写业务逻辑（仅视觉）。

## 子文档索引

| 文档 | 内容 |
|---|---|
| `qss/dark_theme_tokens.qss.md` | 颜色/尺寸令牌 |
| `qss/main_window_qss_guide.md` | 菜单、工具栏、状态栏 |
| `qss/dock_widget_qss_guide.md` | Dock 标题与内容 |
| `qss/button_qss_guide.md` | 主/次/危险/工具按钮 |
| `qss/form_qss_guide.md` | 输入框、下拉、复选 |

## 相关文档

- 颜色：`01_Color_System.md`
- ADR：`decision/ADR-0014-Enterprise-Design-System.md`
