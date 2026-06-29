# ADR-0022 高保真先于 PySide6

## 状态

已接受

## 背景

Release 008 线框、009.5 Design System、009.9 AI Index 已就绪。团队曾启动 PySide6 MainWindow Mock，但 **视觉细节、热力图叠加、工业仪器气质** 在线框与代码之间仍存在理解偏差。ADR-0012 规定流程须在 PySide6 前完成 High Fidelity 阶段。

## 问题

1. 直接写 PySide6 易出现布局/色值与 Design Token 漂移
2. AI 图片不可版本化、不可浏览器验收
3. 产品 Review 缺少单一静态设计源
4. 热力图「整层叠加」在代码中易被误实现为逐格绘制

## 决策

**Release 010 交付 High Fidelity Design Package**，采用：

- `prototypes/high_fidelity/` — HTML + CSS 静态原型（1920×1080，全中文）
- `docs/product-spec/high-fidelity/` — 规格、Token 快照、SVG 设计稿、验收清单
- **暂停** Release 010 PySide6 MainWindow 作为正式交付（已有代码可保留，不以本 ADR 删除）

**PySide6 MainWindow Prototype 移至 Release 011**，且必须参考三层：

1. `docs/product-spec/high-fidelity/`
2. `docs/product-spec/ui-wireframe/`
3. `docs/product-spec/design-system/`

## 后果

### 正面

- 设计与开发有共同视觉基准
- 浏览器/SVG 可 PR Review
- 符合 ADR-0012 流程

### 负面

- 多一层文档维护（HTML/SVG 与 Token 同步）
- PySide6 交付延后一个 Release 编号

## 替代方案

| 方案 | 未采纳 |
|---|---|
| 继续 PySide6 边写边定视觉 | 漂移风险高 |
| 仅用 AI 图片 | 不可交互、难版本化 |
| 跳过线框直接高保真 | 违反 ADR-0012 |

## 约束

- 高保真 **无外链、无 CDN**
- 界面 **简体中文** 主文案
- **禁止** 左侧「项目」导航；辅助 Dock 默认隐藏
- 热力图 **整层** gradient/Pixmap，禁止逐格
- 不删除历史文档

## 与 Release_011 MainWindow Prototype 的关系

Release 011 从 `spec/Task_Guide/Build_MainWindow.md` 启动 PySide6，**必须先通过** 高保真验收清单。实现者顺序：

```text
spec/AI_INDEX.md
→ high-fidelity/01_Main_Window_High_Fidelity_Spec.md
→ prototypes/high_fidelity/index.html（视觉对照）
→ ui-wireframe + design-system
→ PySide6 编码
```

## 相关

- [Release 010 README](../release/Release_010_High_Fidelity_Design/README.md)
- [ADR-0012 UI Wireframe First](ADR-0012-UI-Wireframe-First.md)
- [ADR-0021 AI Knowledge Index](ADR-0021-AI-Knowledge-Index.md)
