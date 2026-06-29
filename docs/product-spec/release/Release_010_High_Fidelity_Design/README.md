# Release 010 — High Fidelity Design Package

## 版本状态

| 项 | 说明 |
|---|---|
| **当前版本** | **候选定稿版（v2.1 Final Candidate）** |
| **状态** | **Candidate Final — 待 git 提交定稿** |
| **验收** | [High_Fidelity_Acceptance_Checklist.md](../../high-fidelity/spec/High_Fidelity_Acceptance_Checklist.md) **18/18** |

本版为 Release 010 **候选定稿**：布局与 v2.1 一致，仅做最终验收修正（无浏览器滚动条、Dock 内部滚动、Dock 字号 +1px）。**不重做整体布局，不缩小 PCB。**

## 1. Release 目标

交付 **可本地浏览器打开** 的高保真设计包（HTML / CSS / SVG），在 PySide6 编码前统一视觉与布局认知。

| 产出 | 路径 |
|---|---|
| 交互原型 | [prototypes/high_fidelity/index.html](../../../../prototypes/high_fidelity/index.html) |
| SVG 设计稿 | [high-fidelity/assets/main_window_high_fidelity.svg](../../high-fidelity/assets/main_window_high_fidelity.svg) |
| 规格文档 | [high-fidelity/](../../high-fidelity/README.md) |
| 验收清单 | [High_Fidelity_Acceptance_Checklist.md](../../high-fidelity/spec/High_Fidelity_Acceptance_Checklist.md) |

## 2. 为什么先做高保真，不直接写 PySide6

| 原因 | 说明 |
|---|---|
| ADR-0012 流程 | Wireframe → Design System → **High Fidelity** → PySide6 |
| 视觉对齐成本 | 先编码易与 Token/线框漂移 |
| Review 效率 | 产品/硬件工程师可直接浏览器验收 |
| 暂停 PySide6 | Mock 代码不作为本 Release 交付物；011 再实现 |

## 3. 与 Release 008 Wireframe 的关系

- **008 为布局尺寸权威**（1920×1080、64/180 导航、360 Dock）
- 高保真 **不得** 改变区域比例，只增加视觉细节

## 4. 与 Release 009 / 009.5 Design System 的关系

- Token、组件、模式来自 `design-system/`
- 高保真 Token 快照：[high_fidelity_tokens.md](../../high-fidelity/tokens/high_fidelity_tokens.md)

## 5. 与 Release 009.8 Domain Model 的关系

- Mock 文案对齐 Region / ScanTask / Probe（CPU_Area、6461 pts 等）
- 不实现领域逻辑，仅 UI 标签一致

## 6. 与 Release 009.9 AI Knowledge Index 的关系

- 任务入口仍从 `spec/AI_INDEX.md` 开始
- Registry `UI.yaml` 含 `high_fidelity` 索引

## 7. 候选定稿修正摘要（v2.1 Final Candidate）

| 修正项 | 说明 |
|---|---|
| 无浏览器滚动条 | `body`/`html` `overflow: hidden` + 视口 scale |
| Dock 底部 | 参数区 **内部独立滚动**，间距微调 |
| Dock 可读性 | 标签字号整体 +1px |
| PCB | **保持当前尺寸**，未缩小 |
| 顶部 X | 页面内无灰色 X 元素（浏览器预览浮层除外） |

## 8. 本次输出文件清单

```text
docs/product-spec/release/Release_010_High_Fidelity_Design/README.md
docs/product-spec/high-fidelity/
docs/product-spec/decision/ADR-0022-High-Fidelity-Before-PySide6.md
prototypes/high_fidelity/index.html
prototypes/high_fidelity/styles.css
prototypes/high_fidelity/README.md
```

## 9. 本次不做什么

- ❌ PySide6 业务代码
- ❌ 真实设备 / 扫描 / 热力图算法
- ❌ 重做整体布局或缩小 PCB
- ❌ CDN / 外链资源
- ❌ 左侧加「项目」；默认显示日志/频谱/统计

## 10. 进入 Release 011 MainWindow Prototype 的条件

1. 本 Release **候选定稿** 已 git 提交
2. [High_Fidelity_Acceptance_Checklist.md](../../high-fidelity/spec/High_Fidelity_Acceptance_Checklist.md) **18/18**
3. ADR-0022 Accepted
4. PySide6 须同时参考：**high-fidelity + ui-wireframe + design-system**

---

**依赖**：Release 008、009、009.5、009.8、009.9  
**下一步**：提交 Release 010 定稿 → Release 011 MainWindow Prototype（PySide6 Mock）
