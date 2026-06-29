# Design Principles — 设计原则

## 设计目标

NFS Scanner Pro 的 UI 必须像 **Keysight / R&S / NI / Altium / Cadence** 类工业软件：深色、紧凑、数据与画布优先，而非通用 SaaS 后台。

## 核心原则

| # | 原则 | 说明 |
|---|---|---|
| 1 | PCB 永远是主角 | 画布 ≥70% 宽；禁止装饰性 UI 抢视觉 |
| 2 | 一页一事 | 左侧四页：扫描、设备、分析、报告 |
| 3 | 项目归文件菜单 | 新建/打开/保存不在导航与工具栏（ADR-0013） |
| 4 | 辅助面板按需显示 | 日志/频谱/统计/表格默认隐藏 |
| 5 | 参数在 Dock | 右侧 340px Accordion，可 auto-hide |
| 6 | 数据可追溯 | 状态栏 + 设备状态栏实时反馈 |
| 7 | 热力图整图渲染 | QPixmap 单层，禁止逐格 Item |
| 8 | Design Token 驱动 | 禁止硬编码 hex 散落代码 |

## 仪器软件 vs 后台管理系统

| 维度 | 仪器软件（目标） | 后台管理（禁止） |
|---|---|---|
| 主区域 | PCB + 热力图画布 | 大表格 / 卡片列表 |
| 导航 | 窄图标轨 | 宽 Sidebar + 多级菜单 |
| 配色 | 深底 + 高对比数据 | 浅灰 + 彩色 card |
| 操作 | 工具栏高频物理动作 | 页面跳转 + 表单 CRUD |

## Qt/PySide6 推荐组件

- 壳层：`QMainWindow` + `QStackedWidget` 四页
- 画布：`QGraphicsView` 占 Central 区最大 stretch
- 样式：Fusion + 全局 QSS（见 `06_QSS/`）

## objectName 命名建议

原则层不绑定具体 objectName，见 `07_Qt_Implementation/Qt_ObjectName_Rules.md`。

## 禁止事项

- 禁止 Dashboard 作为默认首页（默认 **扫描页**）。
- 禁止左侧导航含项目、设置、Dashboard。
- 禁止浅色默认主题。
- 禁止 Web 风格大圆角 card 布局占主区域。

## 相关文档

- [Design_Tokens.md](Design_Tokens.md)
- `../../ui-wireframe/README.md`
