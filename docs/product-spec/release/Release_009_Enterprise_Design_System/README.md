# Release 009 — Enterprise Design System

## Release 目标

Release 009 将 NFS Scanner Pro 的 UI 规范从 Release 008 的**线框与尺寸约束**，升级为**可落地的企业级 Design System**，供 PySide6 实现阶段统一引用。

本 Release 产出：

- 完整的颜色、字体、间距、布局令牌体系
- 菜单、工具栏、导航、Dock、状态栏、表单、表格、画布、热力图、对话框等子系统规范
- QSS 主题令牌与样式编写指南
- ADR-0014 架构决策记录

## 为什么需要 Design System

Release 008 已固定主窗口线框、区域尺寸与导航结构，但尚不足以支撑一致的 PySide6 实现：

| 问题 | Design System 如何解决 |
|---|---|
| 颜色、字号散落在多份文档 | 统一令牌表，一处定义、全局引用 |
| 工业仪器 UI 与普通后台管理混淆 | 明确参考 Keysight、R&S、NI、Altium、Cadence 风格 |
| Qt 组件选型无统一约定 | 每份规范给出推荐组件与 objectName |
| QSS 样式无编写标准 | 提供 dark theme tokens 与分组件 QSS 指南 |
| 实现者自由发挥导致偏离线框 | 禁止事项清单 + 与 ADR-0012/0013 对齐 |

**Design first, Code later** — 在写 Mock UI 或业务代码之前，先让所有人引用同一套规范。

## 与 Release 008 Wireframe 的关系

```text
Release 008（ui-wireframe/）
  ├── 固定 1920×1080 布局
  ├── 区域尺寸（菜单 32 / 工具栏 56 / 导航 56↔180 / Dock 340）
  └── 产品交互原则（PCB 主角、文件菜单管项目、视图菜单调辅助面板）

Release 009（design-system/）  ← 本 Release
  ├── 在 Release 008 尺寸之上补充视觉与组件规范
  ├── 不修改线框结构与导航决策
  └── 为 Release 010 Component Library 提供规范来源

Release 010（计划）
  └── MainWindow Prototype（基于 Release 009.5 分层规范）

Release 009.5（design-system/ 七层结构）  ← 当前权威 UI Foundation
  ├── 01_Foundation（Design Token）
  ├── 02_Components（Component Library）
  ├── 03_Patterns / 04_Interaction / 05_Animation
  └── 06_QSS / 07_Qt_Implementation
```

**权威层级**：Release 008 线框尺寸 > Release 009 Design System > 旧版 `ui/` 与 `product-design/` 文档。

## 本阶段不做什么

- ❌ 不写 PySide6 业务代码或 Mock UI 实现
- ❌ 不修改已有 UI 实现（当前仓库尚无应用源码）
- ❌ 不生成 Figma 或高保真图片
- ❌ 不创建 `src/`、`tests/` 等工程目录
- ❌ 不删除或覆盖 Release 008 线框文档
- ❌ 不启动 Release 010 组件库编码

## 输出文件清单

### Release 入口

| 文件 | 说明 |
|---|---|
| `release/Release_009_Enterprise_Design_System/README.md` | 本文件 |

### Design System 核心规范

| 文件 | 说明 |
|---|---|
| `design-system/01_Color_System.md` | 颜色令牌（扩展） |
| `design-system/02_Typography.md` | 字体与排版 |
| `design-system/03_Spacing_And_Layout.md` | 间距与布局栅格 |
| `design-system/04_Icon_System.md` | 图标体系 |
| `design-system/05_Menu_System.md` | 菜单栏规范 |
| `design-system/06_Toolbar_System.md` | 工具栏规范 |
| `design-system/07_Navigation_System.md` | 左侧导航规范 |
| `design-system/08_Dock_System.md` | Dock 面板规范 |
| `design-system/09_Status_System.md` | 状态栏与设备状态栏 |
| `design-system/10_Form_System.md` | 表单与 Accordion |
| `design-system/11_Table_System.md` | 数据表格 |
| `design-system/12_GraphicsView_System.md` | 主画布 QGraphicsView |
| `design-system/13_Heatmap_System.md` | 热力图渲染 |
| `design-system/14_Dialog_System.md` | 对话框与向导 |
| `design-system/15_QSS_Guide.md` | QSS 总指南 |

### QSS 子目录

| 文件 | 说明 |
|---|---|
| `design-system/qss/dark_theme_tokens.qss.md` | 深色主题 CSS 变量令牌 |
| `design-system/qss/main_window_qss_guide.md` | 主窗口 QSS |
| `design-system/qss/dock_widget_qss_guide.md` | Dock QSS |
| `design-system/qss/button_qss_guide.md` | 按钮 QSS |
| `design-system/qss/form_qss_guide.md` | 表单控件 QSS |

### 预留目录（Release 010）

| 目录 | 说明 |
|---|---|
| `design-system/components/` | 可复用 Qt 组件规格（Release 010 填充） |
| `design-system/patterns/` | 复合交互模式（Release 010 填充） |

### 架构决策

| 文件 | 说明 |
|---|---|
| `decision/ADR-0014-Enterprise-Design-System.md` | 本 Release 架构决策 |

## 后续进入 Release 010 Component Library 的条件

满足以下全部条件后，方可启动 Release 010：

1. **规范完整**：Design System 01~15 与 QSS 指南均已 Review 并通过 ADR-0014 约束。
2. **线框对齐**：Release 008 `ui-wireframe/` 与 Design System 无尺寸/导航冲突。
3. **objectName 冻结**：`qt-spec/02_Qt_Object_Names.md` 与本 Release 各文档 objectName 建议一致。
4. **Mock UI 范围明确**：Release 010 仅实现主窗口骨架 + 4 页切换 + Mock 数据，不接真实设备。
5. **QSS 令牌验证**：至少完成 dark theme 在 QMainWindow 级别的样式试应用（可在 Release 010 首 PR 中验证）。
6. **components/ 清单就绪**：Release 010 启动前，在 `design-system/components/` 列出首批组件（MainWindow、LeftNav、ScanCanvas、ScanParamDock 等）的接口规格。

---

**状态**：Accepted  
**版本**：Release 009  
**依赖**：Release 008 UI Wireframe、ADR-0012、ADR-0013
