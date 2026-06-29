# NFS Scanner Pro — Enterprise UI Foundation

> **Release 009.5** · 企业级 UI 设计系统分层索引  
> 权威层级：Release 008 线框尺寸 > **本 Design System** > 旧版扁平文档（01~15，历史兼容）

## 目录结构

```text
design-system/
├── README.md                    ← 本文件
├── 01_Foundation/               设计原则与 Design Token
├── 02_Components/               组件库规格（Component Library）
├── 03_Patterns/                 复合布局与业务模式
├── 04_Interaction/              交互规范
├── 05_Animation/                动效规范
├── 06_QSS/                      样式与 Token 映射
└── 07_Qt_Implementation/        Qt/PySide6 实现规则
```

## 产品 UI 原则（全局）

1. **PCB 永远是主角**，画布 ≥70% 宽度。
2. 左侧导航默认 **56px 图标**，悬停展开 **180px** 文字。
3. **项目**操作仅在「文件」菜单，非一级页面（ADR-0013）。
4. **设置 / 帮助**在顶部菜单栏。
5. 日志、频谱、统计、数据表格 **默认隐藏**，经「视图」菜单调出。
6. 右侧参数 **Dock**：可固定、自动隐藏、关闭。
7. 主画布 **QGraphicsView / QGraphicsScene**。
8. 热力图 **整张 QPixmap**，禁止逐格绘制。
9. 风格参考 Keysight、R&S、NI、Altium、Cadence。

## 分层说明

| 层 | 路径 | 回答的问题 |
|---|---|---|
| Foundation | `01_Foundation/` | 用什么颜色、字号、间距、动效令牌？ |
| Components | `02_Components/` | 每个 Qt 控件长什么样、叫什么 objectName？ |
| Patterns | `03_Patterns/` | 多个组件如何组成主窗口、扫描工作台？ |
| Interaction | `04_Interaction/` | 用户如何点击、快捷键、Dock、画布操作？ |
| Animation | `05_Animation/` | 导航展开、Dock 收起多快、用什么曲线？ |
| QSS | `06_QSS/` | Token 如何写成 QSS？ |
| Qt Implementation | `07_Qt_Implementation/` | 类结构、objectName、状态属性规则 |

## Release 入口

- [Release 009](../release/Release_009_Enterprise_Design_System/README.md) — 首版 Design System（扁平文档）
- [Release 009.5](../release/Release_009_5_Enterprise_UI_Foundation/README.md) — 本版分层重构

## 历史兼容文档

以下扁平文件 **保留不删**，顶部已标注迁移目标：

`01_Color_System.md` … `15_QSS_Guide.md`、`qss/`、`components/README.md`、`patterns/README.md`

## 相关 ADR

- [ADR-0012](../decision/ADR-0012-UI-Wireframe-First.md)
- [ADR-0013](../decision/ADR-0013-Project-In-File-Menu.md)
- [ADR-0014](../decision/ADR-0014-Enterprise-Design-System.md)
