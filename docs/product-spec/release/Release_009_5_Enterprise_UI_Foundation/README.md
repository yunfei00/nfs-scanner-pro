# Release 009.5 — Enterprise UI Foundation

## 1. Release 背景

Release 009 首次建立了 NFS Scanner Pro 的企业级 Design System，覆盖颜色、菜单、Dock、画布、QSS 等 15 篇扁平规范。团队在 Review 中发现：规范**可引用但不可导航**，实现者仍需在多篇文档间自行拼凑 Component、Interaction、Token 与 Qt 映射关系。

Release 009.5 在不推翻 Release 009 内容的前提下，将 Design System **重构为企业级分层结构**，补齐 Component Library、Interaction、Animation 与正式 Design Token 体系，作为 Release 010 MainWindow Prototype 的唯一 UI 规范入口。

## 2. 为什么 Release 009 还不够

| 缺口 | 影响 |
|---|---|
| 文档扁平散乱（01~15 同级） | 找不到「按钮规范在哪」 |
| Component Library 仅有占位 README | 无法实现一致控件 |
| 无 Interaction 专章 | 画布缩放、Dock、Hx/Hy 切换行为不一致 |
| 无 Animation 专章 | 导航 150ms 等约定散落，易遗漏 |
| Token 命名不统一（`--color-primary` vs 实现常量） | QSS 与代码难以同步 |

## 3. 本次解决的 5 个问题

### 3.1 目录结构

建立七层目录：`01_Foundation` → `07_Qt_Implementation`，见 [design-system/README.md](../../design-system/README.md)。

### 3.2 Component Library

在 `02_Components/` 发布 15 个组件规格：Button、Input、MenuBar、NavigationBar、DockPanel、Table、Dialog 等。

### 3.3 Interaction

在 `04_Interaction/` 发布鼠标、键盘、Dock、画布、Region 编辑、Hx/Hy 切换、扫描状态交互规范。

### 3.4 Animation

在 `05_Animation/` 发布原则、导航、Dock、反馈、加载进度动效规范。

### 3.5 Design Token

在 `01_Foundation/Design_Tokens.md` 建立点分命名令牌（`color.bg.app`）及 Qt/QSS 映射。

## 4. 本次不做什么

- ❌ 不写 PySide6 业务代码
- ❌ 不生成高保真图片或 Figma
- ❌ 不重写产品需求（`pages/`、`workflow/`、`data/` 不变）
- ❌ 不删除 Release 009 扁平文档（仅加迁移提示）
- ❌ 不修改 Release 008 线框尺寸

## 5. 输出目录清单

```text
docs/product-spec/
├── release/Release_009_5_Enterprise_UI_Foundation/README.md
└── design-system/
    ├── README.md
    ├── 01_Foundation/          (8 文件)
    ├── 02_Components/          (16 文件)
    ├── 03_Patterns/            (8 文件)
    ├── 04_Interaction/         (8 文件)
    ├── 05_Animation/           (6 文件)
    ├── 06_QSS/                 (9 文件)
    └── 07_Qt_Implementation/ (6 文件)
```

## 6. 与 Release 008 Wireframe 的关系

Release 008（`ui-wireframe/`）继续作为 **布局与尺寸的最高权威**：

- 1920×1080、菜单 32、工具栏 56、导航 56↔180、Dock 340
- PCB 主角、文件菜单管项目、视图菜单调辅助 Dock

Release 009.5 **不修改**上述尺寸，仅在 `03_Patterns/MainWindow_Pattern.md` 等文档中引用并细化。

## 7. 与 Release 009 Design System 的关系

```text
Release 009   扁平 01~15 + qss/     → 内容已吸收至 009.5 分层文档，原文件保留
Release 009.5 七层 Enterprise UI Foundation  → 当前权威入口
Release 010   MainWindow Prototype   → 下一步
```

**阅读优先级**：`design-system/README.md` > 分层子目录 > 旧扁平 01~15。

## 8. 进入 Release 010 MainWindow Prototype 的前置条件

1. Release 009.5 全部分层文档 Review 完成。
2. `01_Foundation/Design_Tokens.md` 令牌表与 `06_QSS/token_mapping_qss.md` 一致。
3. `02_Components/` 15 组件 objectName 与 `07_Qt_Implementation/Qt_ObjectName_Rules.md` 对齐。
4. `04_Interaction/` 与 `05_Animation/` 无与 Release 008 线框冲突。
5. Release 008 `ui-wireframe/` 仍无结构变更需求。
6. ADR-0014 仍然有效；若架构变更需新 ADR。

---

**状态**：Accepted  
**版本**：Release 009.5  
**依赖**：Release 008、Release 009、ADR-0012、ADR-0013、ADR-0014
