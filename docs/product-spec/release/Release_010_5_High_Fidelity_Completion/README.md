# Release 010.5 — High Fidelity Completion

## 版本状态

| 项 | 说明 |
|---|---|
| **当前版本** | **候选定稿版（v1.0 Final Candidate）** |
| **状态** | **Candidate Final — 待 git 提交定稿** |
| **验收** | [High_Fidelity_Acceptance_Checklist.md](../../high-fidelity/spec/High_Fidelity_Acceptance_Checklist.md) **17/17** |

## 1. Release 背景

Release **010** 已完成扫描页高保真候选定稿。Release **010.5** 在**不重画扫描页**前提下，补齐设备 / 分析 / 报告三页与四种关键 UI 状态说明，并完成四页框架统一验收。

## 2. 为什么 Release_010 还不能直接进入代码

全产品四页导航 + 多状态 UI 需在设计层闭环；仅扫描页不足以支撑 PySide6 全壳层实现（详见 [ADR-0023](../../decision/ADR-0023-High-Fidelity-Completion-Before-Code.md)）。

## 3. 当前扫描页状态

| 项 | 状态 |
|---|---|
| 原型 | [index.html](../../../../prototypes/high_fidelity/index.html) |
| 010 版本 | Release 010 候选定稿（v2.1）— **010.5 不重画** |

## 4. 本次补全范围（候选定稿修正）

| 修正项 | 说明 |
|---|---|
| 四页框架统一 | 菜单栏、64px 工具栏、设备状态栏、64↔180 导航、360px Dock、40px 状态栏 |
| 分析页 PCB | 复用扫描页 PCB 视觉（芯片/焊盘/走线/过孔/径向热力图） |
| 报告页预览 | PCB + 热力图 SVG 缩略图，PDF 风排版 |
| 设备页 | 状态徽标、回零/测试连接/拍照/校准按钮视觉强化 |
| 无浏览器滚动条 | overflow hidden + 1920×1080 scale |

## 5. 本次不做什么

- ❌ PySide6 代码（**Release 011** 才开始）
- ❌ 重画扫描页整体布局 / 缩小 PCB
- ❌ 真实设备 / 扫描 / PDF 生成
- ❌ 默认显示日志、频谱、统计

## 6. 输出文件列表

```text
prototypes/high_fidelity/index.html
prototypes/high_fidelity/device.html
prototypes/high_fidelity/analysis.html
prototypes/high_fidelity/report.html
prototypes/high_fidelity/styles.css
prototypes/high_fidelity/README.md
docs/product-spec/high-fidelity/pages/device/
docs/product-spec/high-fidelity/pages/analysis/
docs/product-spec/high-fidelity/pages/report/
docs/product-spec/high-fidelity/states/
docs/product-spec/high-fidelity/spec/High_Fidelity_Acceptance_Checklist.md
docs/product-spec/decision/ADR-0023-High-Fidelity-Completion-Before-Code.md
```

## 7. 进入 Release_011 的条件

1. 本 Release **候选定稿** 已 git 提交
2. 验收清单 **17/17**
3. ADR-0022 + ADR-0023 Accepted
4. 011 视觉输入 = **010 + 010.5**

---

**明确声明**：

- **Release_010** 扫描页已定稿；**010.5 不再反复重画扫描页**。
- **Release_010.5** 候选定稿已完成四页统一与状态闭环。
- **下一步**：**Release 011 MainWindow PySide6 Prototype**（`python scripts/run_mock_ui.py`）。

**依赖**：Release 008–010
