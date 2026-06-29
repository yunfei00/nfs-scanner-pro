# ADR-0023 — High Fidelity Completion Before Code

| 项 | 值 |
|---|---|
| 状态 | Accepted |
| 日期 | 2025-06-29 |
| 关联 | ADR-0012、ADR-0022、Release 010、Release 010.5、Release 011 |

## 1. 背景

Release **010** 交付了扫描页高保真候选定稿（`prototypes/high_fidelity/index.html`），通过 18 项验收。产品导航包含 **扫描、设备、分析、报告** 四页，且 ScanTask 存在多种 UI 状态（准备就绪、扫描中、完成、设备异常）。

若在仅扫描页高保真的情况下启动 PySide6 全壳层，将导致：

- 设备/分析/报告页在编码阶段「自由发挥」，与 010 视觉漂移；
- 状态机与工具栏 enabled 矩阵缺乏设计共识；
- 违背 ADR-0022「高保真先于 PySide6」的完整意图。

## 2. 为什么 Release_010 不能直接进入代码

| 原因 | 说明 |
|---|---|
| 页面缺口 | 010 仅覆盖扫描页 ~25% 导航面 |
| 状态缺口 | 无扫描中/异常等状态的高保真说明 |
| Review 闭环 | 产品/硬件无法浏览器验收全流程 UI |
| 011 范围失控 | 开发易将未设计页面临时 Mock，后续返工 |

**010 扫描页可定稿，但不等于全产品高保真完成。**

## 3. 决策

引入 **Release 010.5 High Fidelity Completion**：

1. **冻结** Release 010 扫描页布局，010.5 **不重画**扫描页。
2. 补齐 **device / analysis / report** 三页静态 HTML 高保真 + 规格文档。
3. 补齐 **四种关键 UI 状态** 说明文档。
4. 更新验收清单，明确 **010 + 010.5** 为 Release 011 的视觉输入。
5. **Release 011** 才开始 PySide6 代码；011 **暂停**直至 010.5 验收通过。

## 4. 后果

### 正面

- 四页 + 状态在设计层闭环，011 可按页实现 QStackedWidget。
- 扫描页不再反复修改，降低 010 回归成本。
- 浏览器可验收全产品 UI，无需 PySide6 环境。

### 负面

- 增加一个 Release 周期；011 代码交付后移。
- 三页 HTML 需与 010 共用 `styles.css`，样式变更需回归四页。

## 5. 替代方案

| 方案 | 拒绝原因 |
|---|---|
| 010 后直接 PySide6，页面边写边设计 | 视觉漂移、返工高 |
| 用 AI 图片代替 HTML 高保真 | 不可交互、尺寸不准、违背 ADR-0022 |
| 在 010 内无限扩展扫描页 | 扫描页已候选定稿，违反冻结策略 |
| 仅写 Markdown 不写 HTML | 产品无法像素级验收 |

## 6. 与 Release_011 的关系

| Release | 职责 |
|---|---|
| **010** | 扫描页高保真候选定稿 |
| **010.5** | 设备/分析/报告页 + 状态说明 + 验收扩展 |
| **011** | PySide6 MainWindow Mock，视觉输入 = **010 + 010.5** |

011 实现时：

- 扫描页以 `index.html` 为准，**禁止缩小 PCB**。
- 设备/分析/报告以 010.5 对应 HTML 为准。
- 状态行为以 `high-fidelity/states/` 为准。
- **不再使用 AI 图片作为唯一设计依据**。

---

**参考**：[Release_010_5_High_Fidelity_Completion/README.md](../release/Release_010_5_High_Fidelity_Completion/README.md)
