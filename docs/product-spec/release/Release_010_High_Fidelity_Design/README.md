# Release 010 — High Fidelity Design Package

## 1. Release 目标

交付 **可本地浏览器打开** 的高保真设计包（HTML / CSS / SVG），在 PySide6 编码前统一视觉与布局认知。

| 产出 | 路径 |
|---|---|
| 交互原型 | [prototypes/high_fidelity/index.html](../../../../prototypes/high_fidelity/index.html) |
| SVG 设计稿 | [high-fidelity/assets/main_window_high_fidelity.svg](../../high-fidelity/assets/main_window_high_fidelity.svg) |
| 规格文档 | [high-fidelity/](../../high-fidelity/README.md) |

## 2. 为什么先做高保真，不直接写 PySide6

| 原因 | 说明 |
|---|---|
| ADR-0012 流程 | Wireframe → Design System → **High Fidelity** → PySide6 |
| 视觉对齐成本 | 先编码易与 Token/线框漂移 |
| Review 效率 | 产品/硬件工程师可直接浏览器验收 |
| 暂停 PySide6 | 已有 Mock 代码不作为本 Release 交付物；011 再实现 |

## 3. 与 Release 008 Wireframe 的关系

- **008 为布局尺寸权威**（1920×1080、56/180 导航、340 Dock）
- 高保真 **不得** 改变区域比例，只增加视觉细节

## 4. 与 Release 009 / 009.5 Design System 的关系

- Token、组件、模式来自 `design-system/`
- 高保真 Token 快照：[high_fidelity_tokens.md](../../high-fidelity/tokens/high_fidelity_tokens.md)

## 5. 与 Release 009.8 Domain Model 的关系

- Mock 文案对齐 Region / ScanTask / Probe（CPU_Area、6461 pts 等）
- 不实现领域逻辑，仅 UI 标签一致

## 6. 与 Release 009.9 AI Knowledge Index 的关系

- 任务入口仍从 `spec/AI_INDEX.md` 开始
- Registry `UI.yaml` 增加 `high_fidelity` 索引

## 7. 本次输出文件清单

```text
docs/product-spec/release/Release_010_High_Fidelity_Design/README.md
docs/product-spec/high-fidelity/          （README、spec、pages、tokens、assets）
docs/product-spec/decision/ADR-0022-High-Fidelity-Before-PySide6.md
prototypes/high_fidelity/index.html
prototypes/high_fidelity/styles.css
prototypes/high_fidelity/README.md
```

## 8. 本次不做什么

- ❌ PySide6 业务代码（暂停 MainWindow 实现）
- ❌ 真实设备 / 扫描 / 热力图算法
- ❌ AI 生成图片作为唯一设计源
- ❌ CDN / 外链资源
- ❌ 删除历史文档或旧 Release
- ❌ 左侧加「项目」；默认显示日志/频谱/统计

## 9. 进入 Release 011 MainWindow Prototype 的条件

1. [High_Fidelity_Acceptance_Checklist.md](../../high-fidelity/spec/High_Fidelity_Acceptance_Checklist.md) 13 项通过
2. ADR-0022 Accepted
3. 原型与 SVG 与 `01_Main_Window_High_Fidelity_Spec.md` 一致
4. PySide6 实现须同时参考：**high-fidelity + ui-wireframe + design-system**

---

**状态**：Accepted  
**依赖**：Release 008、009、009.5、009.8、009.9  
**下一步**：Release 011 MainWindow Prototype（PySide6 Mock）
