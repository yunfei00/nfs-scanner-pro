# Domain To UI Mapping — 领域对象到 UI 映射

> 与 Release 009.5 Design System objectName 一致。Project **无**左侧导航入口（ADR-0013 / ADR-0018）。

## 总表

| 领域对象 | UI 显示位置 | objectName / 组件 |
|---|---|---|
| **Project** | 文件菜单；Breadcrumb 首段；最近项目列表 | `actionNewProject`, `actionOpenProject`, `actionSaveProject` |
| **PCB** | 扫描画布 Photo Layer | `scanCanvasView`, `scanScene` |
| **Region** | 画布矩形 regionLayer；参数 Dock；Breadcrumb 第二段 | `regionSettingsGroup`, `fieldRegionName`, `regionLayer` |
| **Alignment** | 工具栏「区域对齐」；画布矩形样式 | `toolbarAlignButton` |
| **DeviceProfile** | 设备页；新建项目 Dialog；设置 | `devicePage`, `fieldDeviceProfile` |
| **DeviceSnapshot** | 扫描记录详情；报告内只读块 | `devicePage` 详情区；报告页 |
| **ScanTask** | 工具栏开始/停止；底部状态栏进度；Breadcrumb 点数 | `toolbarStartScanButton`, `toolbarStopScanButton`, `statusBarProgressBar` |
| **ScanPoint** | 路径层；数据表格 Dock（默认隐藏） | `pathLayer`, `dataTableView` |
| **Probe** | 参数 Dock 通道选择；Breadcrumb | `fieldProbeChannel` |
| **Heatmap** | 画布 heatmapLayer 单 QPixmap | `heatmapLayer` |
| **Analysis** | 分析页 | `analysisPage`, `navAnalysisButton` |
| **Report** | 报告页 | `reportPage`, `navReportButton` |
| **Motion/Spectrum/…** | 设备状态栏 40px 条 | `deviceStatusMotionIndicator` 等 |

## 按 UI 页聚合

| UI 页 | 主要 Domain |
|---|---|
| 扫描（默认） | PCB, Region, ScanTask, Heatmap, Alignment |
| 设备 | DeviceProfile, Motion, Spectrum, Camera, Servo |
| 分析 | Analysis, Heatmap, ScanTask 引用 |
| 报告 | Report, Analysis |

## 会话态（非 Domain 持久化）

| UI | 说明 |
|---|---|
| 当前选中 RegionId | 内存 + 可选写入 ui.session.json（V2） |
| 当前 ScanTask 状态机 | ScanTaskController |

## 禁止

- Project 作为 `navProjectButton`
- ScanTask 进度只用 Dialog 无 statusBar

## 相关

[../../design-system/03_Patterns/Scan_Workbench_Pattern.md](../../design-system/03_Patterns/Scan_Workbench_Pattern.md)
