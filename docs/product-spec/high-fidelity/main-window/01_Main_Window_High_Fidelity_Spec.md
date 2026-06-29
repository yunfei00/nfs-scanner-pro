# 主窗口高保真规格 — 1920×1080

> Release 010 · 布局权威仍来自 [ui-wireframe/01_Main_Window_1920x1080.md](../../ui-wireframe/01_Main_Window_1920x1080.md)

## 1. 主窗口尺寸

基准尺寸：**1920 × 1080**

浏览器原型：[prototypes/high_fidelity/index.html](../../../../prototypes/high_fidelity/index.html)

SVG 稿：[assets/main_window_high_fidelity.svg](../assets/main_window_high_fidelity.svg)

## 2. 固定区域尺寸

| 区域 | 尺寸 |
|---|---:|
| 顶部菜单栏 | 32 px |
| 顶部工具栏 | 56 px |
| 设备状态栏 | 40 px |
| 左侧导航收起宽度 | 56 px |
| 左侧导航展开宽度 | 180 px |
| 右侧参数 Dock 宽度 | 340 px |
| 底部状态栏 | 32 px |

主画布宽度：1920 − 56 − 340 = **1524 px**（≥70%）

## 3. 顶部菜单栏

全部简体中文：

```text
文件(F)  编辑(E)  视图(V)  工具(T)  设置(S)  帮助(H)
```

**文件**菜单含：新建项目、打开项目、打开最近项目、保存项目、关闭项目、打开项目文件夹、退出。

项目相关 **仅** 出现在文件菜单（ADR-0013）。

## 4. 工具栏

默认显示：

```text
开始扫描 | 停止扫描 | 拍照 | 区域对齐 | 网格 | 测量
```

**不显示**：新建项目、打开项目、保存项目、项目管理器。

- 开始扫描：主按钮（蓝 `#0D6EFD`）
- 停止扫描：危险按钮（红 `#EF4444`）

## 5. 左侧导航

只允许：**扫描 · 设备 · 分析 · 报告**

- 默认 **56px**，仅图标
- 鼠标悬停 **180px**，展开文字（150~200ms）
- 默认选中：**扫描**

**禁止**：项目、设置、帮助

## 6. 设备状态栏（单行）

```text
● 运动平台(COM6)  ● 频谱仪(ZNA67)  ● 相机(USB3.0)  ● 舵机系统
探头：Hx(100 μm)  高度：5.000 mm  区域：CPU_Area  频率：2.450 GHz  点数：6461
```

● 绿色 = 已连接（`color.status.success`）

## 7. 中央画布

必须包含：

| 元素 | 实现方式 |
|---|---|
| PCB 图像区域 | SVG 模拟走线/焊盘/芯片 |
| 热力图叠加 | **整层** linearGradient / 单 rect（禁止逐格） |
| 扫描区域矩形 | 蓝色虚线框 |
| 网格点 | SVG pattern / CSS |
| 坐标轴 X/Y/Z | 文字 + 轴线 |
| 小地图 | 左下角 120×80 |
| 当前坐标浮窗 | 右下角 mm / GHz / dBm |
| 面包屑 | `项目 > CPU_Area > Hx Probe > 2.450 GHz > 6461 pts` |

## 8. 右侧参数 Dock

标题：**扫描参数**

分组：扫描设置 · 区域设置 · 显示设置 · 仪表设置 · 高级设置

| 分组 | 默认 |
|---|---|
| 扫描设置 | 展开 |
| 区域设置 | 展开 |
| 显示 / 仪表 / 高级 | 折叠 |

## 9. 底部状态栏

```text
状态：准备就绪 | 扫描进度：0% | 扫描点：0 / 6461 | 预计剩余时间：00:12:31 | 日期：2025-06-16 | 时间：14:31:10
```

## 10. 默认隐藏（视图菜单）

日志、频谱、统计、数据表格 — **本高保真主屏不渲染**（与线框一致）。

## 11. 相关文档

- [Scan_Workbench_Pattern.md](../../design-system/03_Patterns/Scan_Workbench_Pattern.md)
- [Canvas_Interaction.md](../../design-system/04_Interaction/Canvas_Interaction.md)
- [Navigation_Animation.md](../../design-system/05_Animation/Navigation_Animation.md)
