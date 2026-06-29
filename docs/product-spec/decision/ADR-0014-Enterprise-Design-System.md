# ADR-0014 Enterprise Design System

## 状态

Accepted

## 背景

Release 008 已通过 `ui-wireframe/` 固定主窗口线框、区域尺寸与核心交互原则（PCB 主角、文件菜单管项目、视图菜单调辅助 Dock）。但实现团队仍缺少：

- 统一颜色、字体、间距令牌
- 各 UI 子系统（菜单、工具栏、导航、Dock、画布、热力图）的可执行规范
- QSS 编写标准与 objectName 映射
- 与 Keysight / R&S / NI / Altium / Cadence 一致的工业仪器视觉约束

若在无 Design System 情况下直接进入 PySide6 编码，将导致样式分裂、线框偏离、热力图错误实现（逐格绘制）等风险。

## 决策

建立 **Release 009 Enterprise Design System**，作为 Release 008 线框之上的权威视觉与组件规范层：

```text
Release 008  ui-wireframe/     布局与尺寸（不变）
Release 009  design-system/    视觉、组件、QSS（本 ADR）
Release 010  components/       可复用 Qt 组件库（待启动）
```

具体决策：

1. 在 `docs/product-spec/design-system/` 发布 01~15 子系统规范及 `qss/` 指南。
2. 所有 PySide6 实现必须引用 Design System，不得仅参考旧版 `ui/` 或 `product-design/` 高保真。
3. 热力图必须整张 QPixmap 渲染（延续 ADR-0010、qt-spec）。
4. 左侧导航维持 4 项（延续 ADR-0013），项目操作维持文件菜单。
5. Design System 文档使用简体中文，每篇含 Qt 可实现性章节（组件、objectName、禁止事项）。

## 后果

### 正面

- 实现前有单一规范来源，减少 Mock UI 返工。
- QSS 令牌化便于 Release 010 统一换肤与维护。
- 文档与 ADR 形成可审计的设计决策链。

### 负面

- 文档维护成本增加，线框变更需同步 Design System。
- 旧版 `02_Typography_Spacing.md`、`03_Component_Rules.md`、`ui/` 部分内容与 Release 009 并存，需读者辨别优先级。

### 中性

- 本 Release 不写代码，Release 010 才验证 QSS 与规范可行性。

## 约束

1. **不修改 Release 008 线框尺寸与结构**；冲突时以 Release 008 为准并更新 Design System。
2. **默认深色主题**；PCB 画布区域视觉优先级最高。
3. **辅助 Dock 默认隐藏**：日志、频谱、统计、数据表格。
4. **禁止 Figma 为本 Release 交付物**；禁止生成图片。
5. **禁止逐格热力图**；禁止项目入口进入左侧导航。
6. 新 UI 决策需新增 ADR 或修订本 ADR，不得仅在实现代码中变更。

## 与 Release 008 的关系

| 维度 | Release 008 | Release 009 |
|---|---|---|
| 文档路径 | `ui-wireframe/` | `design-system/` |
| 内容 | 线框、固定 px、菜单结构草案 | 颜色、字体、QSS、组件行为、状态机 |
| 权威优先级 | 布局尺寸 | 视觉与控件规范 |
| 关系 | 前置依赖 | 扩展，不替换 |

ADR-0012 定义的流程更新为：

```text
Wireframe (008)
  ↓
Enterprise Design System (009)  ← 当前
  ↓
Component Library (010)
  ↓
PySide6 Mock UI
  ↓
High Fidelity（可选，须遵守 008+009）
  ↓
业务实现
```

## 相关文档

- `release/Release_009_Enterprise_Design_System/README.md`
- `design-system/01_Color_System.md` ~ `15_QSS_Guide.md`
- `decision/ADR-0012-UI-Wireframe-First.md`
- `decision/ADR-0013-Project-In-File-Menu.md`
