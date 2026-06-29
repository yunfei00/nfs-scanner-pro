# 扫描页 — 高保真设计说明

## 1. 页面目标

PCB 近场扫描的 **主工作台**：展示 PCB、扫描区域、热力图叠加、实时坐标与扫描参数，支撑「对齐 → 扫描 → 预览热力图」操作链。

## 2. 使用场景

- 工程师打开项目后默认进入 **扫描** 页
- 调整区域、预览热力图、启动/停止扫描（高保真为静态 Mock）

## 3. 页面结构

```text
面包屑
├── 中央画布（PCB + 热力图 + 区域框 + 网格 + 坐标轴 + 小地图 + 坐标浮窗）
├── 设备状态栏（全局，位于主内容区上方）
└── 右侧 scanParamDock（扫描参数 Accordion）
```

## 4. 显示内容

| 区域 | 内容 |
|---|---|
| 面包屑 | 项目 > CPU_Area > Hx Probe > 2.450 GHz > 6461 pts |
| 画布 | PCB SVG、整层热力图 gradient、扫描矩形、网格点 |
| 小地图 | 左下角视口框 |
| 坐标浮窗 | X/Y/Z mm、频率、幅度 dBm |
| 参数 Dock | 扫描设置 + 区域设置（展开） |

## 5. 默认隐藏内容

- 日志 / 频谱 / 统计 / 数据表格 Dock
- 色带图例（视图菜单可选，本稿主屏未展开）

## 6. 与 Dock 的关系

- **scanParamDock** 默认显示、宽 340px
- 辅助 Dock 经 **视图** 菜单打开（高保真 HTML 未渲染）

## 7. 与菜单栏的关系

- **文件**：项目 CRUD（不在本页 UI 内）
- **视图**：参数/日志/频谱/统计/色带/小地图/重置布局
- **工具栏**：开始/停止扫描、拍照、对齐、网格、测量

## 8. 与领域对象的关系

| UI | Domain |
|---|---|
| CPU_Area | Region |
| Hx Probe | Probe / HxHyCalibration |
| 6461 pts | ScanTask 网格点数 |
| 热力图层 | Heatmap（整图叠加） |
| 扫描设置表单 | ScanTask 参数 |

## 9. 后续 PySide6 实现建议

- `QGraphicsView` + 单 `QGraphicsPixmapItem` 热力图
- 参数 Dock 绑定 Mock ScanTask JSON
- 遵循 [spec/Task_Guide/Build_MainWindow.md](../../../../spec/Task_Guide/Build_MainWindow.md)（Release 011）

## 10. 高保真参考

- HTML：[prototypes/high_fidelity/index.html](../../../../prototypes/high_fidelity/index.html)
- SVG：[assets/main_window_high_fidelity.svg](../assets/main_window_high_fidelity.svg)
