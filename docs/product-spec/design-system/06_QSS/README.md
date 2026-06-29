# 06 QSS — 样式层

Release 009.5 QSS 规范，替代扁平 `../qss/` 目录为权威入口（旧目录保留历史兼容）。

| 文档 | 说明 |
|---|---|
| [token_mapping_qss.md](token_mapping_qss.md) | Design Token → QSS 映射 |
| [main_window_qss.md](main_window_qss.md) | 主窗口、菜单 |
| [navigation_qss.md](navigation_qss.md) | 左侧导航 |
| [toolbar_qss.md](toolbar_qss.md) | 工具栏 |
| [dock_qss.md](dock_qss.md) | Dock |
| [form_qss.md](form_qss.md) | 表单、按钮 |
| [table_qss.md](table_qss.md) | 表格 |
| [statusbar_qss.md](statusbar_qss.md) | 状态栏 |

加载策略见历史 `../15_QSS_Guide.md`；Release 010 合并为 `resources/styles/app.qss`。

## 设计目标

Fusion + 全局 QSS，Token 驱动，objectName 选择器。

## 禁止事项

- 禁止不加载 QSS 用 Win11 原生浅色
- 禁止 per-widget 散落 hex
