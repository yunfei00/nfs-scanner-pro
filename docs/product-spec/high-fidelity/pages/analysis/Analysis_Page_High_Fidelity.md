# 分析页高保真 — Analysis Page

Release 010.5 · 原型：[analysis.html](../../../../prototypes/high_fidelity/analysis.html)

## 1. 页面定位

分析一级导航：在 **PCB + 热力图** 仍为视觉中心的前提下，调整 Trace/频率/LUT 等分析参数。

## 2. 框架一致性

- 与扫描页相同主窗口壳层
- 左侧导航选中 **分析**
- 设备状态栏单行；扩展 ScanTask / Trace 上下文

## 3. 中央内容

| 元素 | 说明 |
|---|---|
| Breadcrumb | 项目 > 区域 > ScanTask > Trace > 频率 |
| PCB + 热力图 | 整图 radial 叠加（非逐格） |
| 色带 | 幅度(dBm) |
| 光标读数浮窗 | X/Y、幅度、相位 |

## 4. 右侧 Dock — 分析参数

- Trace 选择、频率选择
- 显示模式：幅度 / 相位 / 实部 / 虚部
- LUT、vmin/vmax、透明度
- 光标读数统计卡片

## 5. 默认隐藏

- 日志、频谱、统计 Dock **不默认显示**
- 页面内占位说明经「视图」菜单打开

## 6. 进入 Release 011

| 011 实现 | 说明 |
|---|---|
| `analysisPage` | 复用 ScanCanvasView + 分析 Dock |
| 分析参数 Dock | QDockWidget 壳层 |
| LUT / vmin / vmax | Mock 控件，无真实计算 |
| 频谱/统计 Dock | 仍默认隐藏 |

**不实现**：Heatmap 重算、FFT、真实 LUT 引擎。

## 7. 验收要点

- [ ] PCB/热力图仍占视觉中心
- [ ] 分析 Dock 360px 风格与扫描 Dock 一致
- [ ] 全部简体中文
