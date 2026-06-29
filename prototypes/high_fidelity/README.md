# 高保真静态原型 — Release 010 / 010.5 候选定稿

## 页面入口

浏览器直接打开（**无需网络**）：

| 页面 | 文件 | Release |
|---|---|---|
| **扫描** | [index.html](index.html) | 010 定稿（不重画） |
| **设备** | [device.html](device.html) | 010.5 |
| **分析** | [analysis.html](analysis.html) | 010.5 |
| **报告** | [report.html](report.html) | 010.5 |

四页通过**左侧导航**（64px 图标 / Hover 180px）互相链接。

## 统一框架

四页共享：

- 顶部菜单栏 · 64px 工具栏 · 48px 设备状态栏
- 左侧四级导航（扫描/设备/分析/报告 — **无「项目」**）
- 右侧 360px Dock · 40px 底部状态栏
- `styles.css` · 1920×1080 · `overflow: hidden` 无浏览器滚动条

## 要求

- 全部 **简体中文** · 无 CDN/外链
- 日志、频谱、统计 **不默认显示**
- 分析页 PCB 与扫描页视觉一致
- 报告预览含 PCB + 热力图缩略 SVG

## 验收

[High_Fidelity_Acceptance_Checklist.md](../../docs/product-spec/high-fidelity/spec/High_Fidelity_Acceptance_Checklist.md) · **17/17**

## Release 011

候选定稿验收通过后，进入 **Release 011 MainWindow PySide6 Prototype**。

视觉输入 = **Release 010 + Release 010.5**（见 [Release README](../../docs/product-spec/release/Release_010_5_High_Fidelity_Completion/README.md)）
