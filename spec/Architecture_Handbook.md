# Architecture Handbook — NFS Scanner Pro 架构摘要

> 读完本手册可知全貌与**细节文档入口**；细节以 `docs/product-spec/` 为准。

---

## 1. 产品定位

企业级 **PCB 近场扫描 EMC 测试** 桌面平台：非单纯设备控制或热力图查看器，而是 Project → 设备 → 区域 → 扫描 → 分析 → 报告 全流程。

→ [01_Product_Vision.md](../docs/product-spec/01_Product_Vision.md) · [02_Product_Goals.md](../docs/product-spec/02_Product_Goals.md)

---

## 2. 真实使用流程

打开/新建 Project（文件夹）→ 连接运动+频谱 → 可选拍照 → 建 Region → 对齐（可选）→ Hx/Hy 扫描 → 热力图 → 分析 → 导出报告。

→ [03_Workflow.md](../docs/product-spec/03_Workflow.md) · [workflow/](../docs/product-spec/workflow/README.md)

---

## 3. 一级模块（UI 导航）

| 导航 | 职责 |
|---|---|
| 扫描 | PCB 画布、Region、ScanTask（默认首页） |
| 设备 | DeviceProfile、连接、Motion/Spectrum/Camera/Servo |
| 分析 | Heatmap、Analysis |
| 报告 | Report 导出 |

Project：**文件菜单**，非导航。→ ADR-0013

→ [05_Navigation.md](../docs/product-spec/05_Navigation.md) · [ui-wireframe/02_Left_Navigation.md](../docs/product-spec/ui-wireframe/02_Left_Navigation.md)

---

## 4. 项目文件夹模型

Project = 文件夹；`project.json` + `pcb/` + `regions/` + `reports/` + `logs/`；**复制文件夹 = 备份**（ADR-0018）。

→ [07_File_System.md](../docs/product-spec/07_File_System.md) · [domain/07_Implementation_Guide/Domain_To_File_System_Mapping.md](../docs/product-spec/domain/07_Implementation_Guide/Domain_To_File_System_Mapping.md)

---

## 5. 领域对象关系（摘要）

Project 1—1 PCB；Project 1—N Region；Region 1—N ScanTask；Region 0..1 Alignment；ScanTask 1—1 DeviceSnapshot + Probe；ScanTask → Heatmap → Analysis → Report。

→ [domain/01_Overview/Object_Relationships.md](../docs/product-spec/domain/01_Overview/Object_Relationships.md)

---

## 6. 状态机总览

- **ScanTask 七态**：未就绪 → 准备就绪 → 扫描中 ⇄ 暂停 → 停止中 → 已完成 / 错误
- **Device 七态**：未配置 … 已连接 / 忙碌 / 错误 / 禁用
- **Alignment 五态**：未对齐 … 已对齐 / 需重新确认 / 失效

→ [domain/04_State_Machines/README.md](../docs/product-spec/domain/04_State_Machines/README.md)

---

## 7. UI 主窗口结构（1920×1080）

MenuBar 32 + ToolBar 56 + DeviceStatus 40 + (Nav 56↔180 | Canvas | Dock 340) + StatusBar 32。

→ [ui-wireframe/01_Main_Window_1920x1080.md](../docs/product-spec/ui-wireframe/01_Main_Window_1920x1080.md) · [design-system/03_Patterns/MainWindow_Pattern.md](../docs/product-spec/design-system/03_Patterns/MainWindow_Pattern.md)

---

## 8. Dock 系统

右侧 scanParamDock 默认显示；log/spectrum/statistics/dataTable **默认隐藏**，视图菜单 toggles。

→ [design-system/02_Components/DockPanel.md](../docs/product-spec/design-system/02_Components/DockPanel.md) · [design-system/03_Patterns/View_Menu_Dock_Pattern.md](../docs/product-spec/design-system/03_Patterns/View_Menu_Dock_Pattern.md)

---

## 9. QGraphicsView 画布原则

七层 Scene；PCB Photo + Heatmap(QPixmap) + Region + Path；禁止逐格热力图。

→ [design-system/07_Qt_Implementation/Qt_GraphicsView_Rules.md](../docs/product-spec/design-system/07_Qt_Implementation/Qt_GraphicsView_Rules.md)

---

## 10. 设备系统

必需：Motion + Spectrum。可选：Camera、Servo。DeviceProfile（系统）→ DeviceSnapshot（ScanTask 冻结）。

→ [domain/03_Device_Objects/](../docs/product-spec/domain/03_Device_Objects/MotionSystem.md) · [data/Device_Profile.md](../docs/product-spec/data/Device_Profile.md)

---

## 11. Hx / Hy 策略

V1：**整区 Hx 完成后整区 Hy**；Probe 切换；HxHyCalibration 偏移补偿。

→ [ADR-0004](../docs/product-spec/decision/ADR-0004-HxHy_Strategy.md) · [workflow/Run_Hx_Hy.md](../docs/product-spec/workflow/Run_Hx_Hy.md)

---

## 12. 相机可选策略

相机离线 **不阻止** ScanTask；UI 灰点非 error 红。

→ [ADR-0003](../docs/product-spec/decision/ADR-0003-Camera_Optional.md) · [domain/06_Error_Recovery/Camera_Error_Recovery.md](../docs/product-spec/domain/06_Error_Recovery/Camera_Error_Recovery.md)

---

## 13. 扫描任务模型

ScanTask 绑定 Project+PCB+Region+Probe+DeviceSnapshot；raw 不覆盖；七态状态机驱动 UI。

→ [domain/02_Core_Objects/ScanTask.md](../docs/product-spec/domain/02_Core_Objects/ScanTask.md) · [ADR-0017](../docs/product-spec/decision/ADR-0017-Scan-State-Machine.md)

---

## 14. 数据与热力图模型

ScanPoint + FrequencyData → Heatmap(processed) → 可 regenerate，不改 raw。

→ [ADR-0010](../docs/product-spec/decision/ADR-0010-Heatmap.md) · [domain/02_Core_Objects/Heatmap.md](../docs/product-spec/domain/02_Core_Objects/Heatmap.md)

---

## 15. 报告模型

Report 从 Analysis 派生；PDF/Word/Excel；不反写 raw。

→ [domain/02_Core_Objects/Report.md](../docs/product-spec/domain/02_Core_Objects/Report.md) · [workflow/Export_Report.md](../docs/product-spec/workflow/Export_Report.md)

---

## 16. Qt / PySide6 实现方向

QMainWindow + QStackedWidget(4页) + QDockWidget + QGraphicsView；Fusion + QSS；objectName 见 qt-spec。

→ [qt-spec/01_Qt_Layout_Spec.md](../docs/product-spec/qt-spec/01_Qt_Layout_Spec.md) · [design-system/07_Qt_Implementation/](../docs/product-spec/design-system/07_Qt_Implementation/README.md)

---

## 17. ADR 总览

0001~0010 领域基础；0012~0014 UI；0015~0020 Domain；**0021 AI Index**。

→ [decision/README.md](../docs/product-spec/decision/README.md) · [Context_Pack/Decision_Context.md](Context_Pack/Decision_Context.md)

---

## 18. 后续 Release 路线

008 线框 → 009.5 UI → 009.8 Domain → **009.9 AI Index** → **010 MainWindow Prototype** → 设备/扫描业务。

→ [Registry/Release.yaml](Registry/Release.yaml) · [Task_Guide/Build_MainWindow.md](Task_Guide/Build_MainWindow.md)

---

**下一步：打开 [AI_INDEX.md](AI_INDEX.md) 选择 Registry。**
