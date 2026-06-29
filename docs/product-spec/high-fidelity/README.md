# 高保真设计包 — 总说明

Release 010 · 1920×1080 · 深色工业仪器软件

## 1. 高保真设计原则

- **遵守线框尺寸**：以 Release 008 `ui-wireframe` 为布局权威，高保真只做视觉细化，不改结构。
- **PCB 永远是主角**：中央画布占主内容区 ≥70% 宽度。
- **静态可验收**：HTML / CSS / SVG 本地打开即可 Review，不依赖 AI 图片或 PySide6。
- **与 Design Token 对齐**：色彩、间距、圆角来自 `design-system/01_Foundation/Design_Tokens.md`。

## 2. 目标分辨率

**1920 × 1080**（与线框一致）

## 3. 设计风格

深色工业仪器软件（Keysight / R&S / NI / Altium 类）：低饱和背景、高对比文字、状态色明确、面板分隔清晰。

## 4. 界面语言

- **全部界面文字必须使用简体中文**
- 不使用英文作为主界面文案（菜单快捷键 `(F)` 等括号标注除外）

## 5. 核心 UI 约束

| 约束 | 说明 |
|---|---|
| PCB 主角 | 画布为视觉中心 |
| 左侧导航 | 默认 **56px 图标模式**，Hover **180px** 展开 |
| 右侧参数 | **Dock** 340px，标题「扫描参数」 |
| 默认隐藏 | 日志、频谱、统计、数据表格 **不默认显示** |
| 项目入口 | **不在**左侧导航；新建/打开/保存在 **文件** 菜单 |

## 6. 目录结构

```text
docs/product-spec/high-fidelity/
├── README.md
├── main-window/01_Main_Window_High_Fidelity_Spec.md
├── pages/01~04_*.md
├── assets/main_window_high_fidelity.svg
├── tokens/high_fidelity_tokens.md
└── spec/High_Fidelity_Acceptance_Checklist.md

prototypes/high_fidelity/
├── index.html
├── styles.css
└── README.md
```

## 7. 打开原型

浏览器打开：[prototypes/high_fidelity/index.html](../../../prototypes/high_fidelity/index.html)

## 8. 相关 Release

- 线框：Release 008
- Design System：Release 009 / 009.5
- Domain：Release 009.8
- AI Index：Release 009.9
- 本包：Release 010 High Fidelity

## 9. Registry

高保真任务扩展见 [spec/Registry/UI.yaml](../../../spec/Registry/UI.yaml) `high_fidelity` 段。
