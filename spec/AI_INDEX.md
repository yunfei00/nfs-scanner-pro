# AI_INDEX — NFS Scanner Pro 第一入口

> **Cursor / ChatGPT / Codex：任何任务必须先读本文，再读 Registry 与 Task_Guide。**

---

## 1. 项目一句话定义

NFS Scanner Pro 是一套面向 **PCB 近场电磁扫描** 的桌面工作台软件，通过运动平台、频谱仪、相机（可选）和舵机（可选）完成 **区域扫描 → 热力图叠加 → 分析 → 报告** 全流程；Project 以**文件夹**形式组织数据，UI 以 **PCB 画布** 为视觉中心。

---

## 2. 当前产品原则（不可违反）

| # | 原则 |
|---|---|
| 1 | **PCB 永远是主角**（画布 ≥70% 宽） |
| 2 | **Project 是文件夹**，是数据容器，**不是**左侧一级页面 |
| 3 | 左侧一级导航只有：**扫描、设备、分析、报告** |
| 4 | 项目新建、打开、保存放在 **「文件」菜单** |
| 5 | **设置、帮助** 放在顶级菜单栏 |
| 6 | 右侧参数区使用 **Dock**（可固定 / 自动隐藏 / 关闭） |
| 7 | **日志、频谱、统计、数据表格** 默认隐藏，经 **「视图」** 菜单打开 |
| 8 | 热力图必须 **整张 QImage / QPixmap** 绘制，**禁止逐格** Item |
| 9 | **Camera 可选**，不能影响扫描数据采集（ADR-0003） |
| 10 | **Hx / Hy** 整区切换；切换后须看 **偏移补偿** 与 **Alignment 状态**（ADR-0004/0019） |

权威：ADR-0012、0013、0014、0018~0020 · [Decision_Context.md](Context_Pack/Decision_Context.md)

---

## 3. AI 工作规则

1. **不要**一次性读取整个仓库或 `docs/` 全树。
2. **先读** 本文件 `spec/AI_INDEX.md`。
3. **根据任务类型** 读 `spec/Registry/{UI|Domain|Workflow|Data|Decision|Qt|Release}.yaml`。
4. **读** 对应 `spec/Context_Pack/*_Context.md`。
5. **若有现成任务** 读 `spec/Task_Guide/*.md`。
6. **最后** 仅打开 Registry 列出的 **相关** `docs/product-spec/...` 原文。
7. **不要** 重复创建已有规范目录（如再造一套 design-system）。
8. **不要** 自由发挥目录结构；新文档走 [Maintenance/How_To_Add_New_Document.md](Maintenance/How_To_Add_New_Document.md)。
9. **不要** 在无 ADR 情况下推翻核心决策（Project 文件夹、Alignment 属 Region 等）。
10. 任务完成后：若新增文档，**必须**更新 Registry（见 Maintenance）。

---

## 4. 仓库导航（摘要）

```text
spec/                          ← 你在这里（AI 层）
docs/product-spec/
  ui-wireframe/                Release 008 线框尺寸（最高 UI 布局权威）
  high-fidelity/               Release 010 高保真设计包
  design-system/               Release 009.5 UI 规范
  domain/                      Release 009.8 领域模型
  workflow/  data/  rules/     流程与首版数据（data 历史兼容）
  decision/                    ADR
  qt-spec/                     Qt 布局 / objectName
  release/                     Release 说明
```

更深架构摘要：[Architecture_Handbook.md](Architecture_Handbook.md)

---

## 5. 任务入口

### 5.1 做 UI / 主窗口 / Dock / QSS

```text
spec/AI_INDEX.md
→ spec/Context_Pack/UI_Context.md
→ spec/Registry/UI.yaml
→ spec/Task_Guide/Build_MainWindow.md（Release 011 PySide6 壳层）
→ docs/product-spec/high-fidelity/main-window/01_Main_Window_High_Fidelity_Spec.md
→ prototypes/high_fidelity/index.html（视觉对照）
→ docs/product-spec/ui-wireframe/01_Main_Window_1920x1080.md
→ docs/product-spec/design-system/（按需子文档）
→ src/nfs_scanner_pro/main.py · scripts/run_mock_ui.py
```

### 5.1b 做设备页 Mock（Release 012）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_012_Device_Module_Mock/README.md
→ docs/product-spec/high-fidelity/pages/device/Device_Page_High_Fidelity.md
→ src/nfs_scanner_pro/ui/pages/device_page.py
```

### 5.1c 做扫描页 Mock（Release 013）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_013_Scan_Module_Mock/README.md
→ docs/product-spec/domain/04_State_Machines/Scan_State_Machine.md
→ src/nfs_scanner_pro/ui/pages/scan_page.py
→ src/nfs_scanner_pro/ui/scan_task_mock.py
```

### 5.1d 做分析页 Mock（Release 014）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_014_Analysis_Module_Mock/README.md
→ docs/product-spec/high-fidelity/pages/analysis/Analysis_Page_High_Fidelity.md
→ src/nfs_scanner_pro/ui/pages/analysis_page.py
→ src/nfs_scanner_pro/ui/analysis_mock.py
```

### 5.1e 做报告页 Mock（Release 015）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_015_Report_Module_Mock/README.md
→ docs/product-spec/high-fidelity/pages/report/Report_Page_High_Fidelity.md
→ src/nfs_scanner_pro/ui/pages/report_page.py
→ src/nfs_scanner_pro/ui/report_mock.py
```

### 5.1f 做项目文件菜单 Mock（Release 016）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_016_Project_File_System_Mock/README.md
→ docs/product-spec/decision/ADR-0018-Project-As-Folder-Domain.md
→ docs/product-spec/domain/02_Core_Objects/Project.md
→ src/nfs_scanner_pro/project_mock.py
→ src/nfs_scanner_pro/ui/main_window.py
```

### 5.1g 做工作区持久化 Mock（Release 017）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_017_Workspace_Persistence_Mock/README.md
→ src/nfs_scanner_pro/workspace_state_mock.py
→ src/nfs_scanner_pro/app_paths.py
→ src/nfs_scanner_pro/ui/main_window.py
```

### 5.1h 做设备抽象层 Mock（Release 018）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_018_Device_Abstraction_Mock/README.md
→ docs/product-spec/domain/04_State_Machines/Device_State_Machine.md
→ src/nfs_scanner_pro/devices/device_manager_mock.py
→ src/nfs_scanner_pro/ui/pages/device_page.py
```

### 5.1i 做扫描引擎抽象 Mock（Release 019）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_019_Scan_Engine_Abstraction_Mock/README.md
→ docs/product-spec/domain/04_State_Machines/Scan_State_Machine.md
→ src/nfs_scanner_pro/scan/scan_engine_mock.py
→ src/nfs_scanner_pro/ui/pages/scan_page.py
```

### 5.1j 做扫描结果持久化 Mock（Release 020）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_020_Scan_Result_Persistence_Mock/README.md
→ src/nfs_scanner_pro/scan/scan_result_persistence_mock.py
→ src/nfs_scanner_pro/scan/scan_engine_mock.py
→ src/nfs_scanner_pro/app_paths.py
```

### 5.1k 做分析数据源 Mock（Release 021）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_021_Analysis_Data_Source_Mock/README.md
→ src/nfs_scanner_pro/analysis/analysis_data_source_mock.py
→ src/nfs_scanner_pro/ui/pages/analysis_page.py
```

### 5.1l 做报告数据源 Mock（Release 022）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_022_Report_Data_Source_Mock/README.md
→ src/nfs_scanner_pro/report/report_data_source_mock.py
→ src/nfs_scanner_pro/ui/pages/report_page.py
→ src/nfs_scanner_pro/ui/report_mock.py
```

### 5.1m 做端到端自动验收（Release 023）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_023_End_to_End_Mock_Verification/README.md
→ scripts/verify_release_023.py
→ scripts/verify_all.py
```

### 5.1n 做全流程冒烟验收（Release 024）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_024_Full_Workflow_Smoke_Test/README.md
→ scripts/verify_release_024.py
→ scripts/verify_all.py
```

### 5.1o 做 CI 自动验收集成（Release 025）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_025_CI_Verification_Integration/README.md
→ .github/workflows/verify.yml
→ scripts/verify_release_025.py
→ scripts/verify_all.py
```

### 5.1p 做扫描页 UI 交互验收（Release 026）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_026_Scan_Page_UI_Interaction_Verification/README.md
→ scripts/verify_release_026.py
→ src/nfs_scanner_pro/ui/pages/scan_page.py
```

### 5.1q 做分析页 UI 交互验收（Release 027）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_027_Analysis_Page_UI_Interaction_Verification/README.md
→ scripts/verify_release_027.py
→ src/nfs_scanner_pro/ui/pages/analysis_page.py
→ src/nfs_scanner_pro/analysis/analysis_data_source_mock.py
```

### 5.1r 做报告页 UI 交互验收（Release 028）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_028_Report_Page_UI_Interaction_Verification/README.md
→ scripts/verify_release_028.py
→ src/nfs_scanner_pro/ui/pages/report_page.py
→ src/nfs_scanner_pro/report/report_data_source_mock.py
→ src/nfs_scanner_pro/report/report_persistence_mock.py
```

### 5.1s 做设备页 UI 交互验收（Release 029）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_029_Device_Page_UI_Interaction_Verification/README.md
→ scripts/verify_release_029.py
→ src/nfs_scanner_pro/ui/pages/device_page.py
→ src/nfs_scanner_pro/devices/device_manager_mock.py
→ src/nfs_scanner_pro/ui/device_status_bar.py
```

### 5.1t 做跨页面工作流 UI 验收（Release 030）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_030_Cross_Page_Workflow_UI_Verification/README.md
→ scripts/verify_release_030.py
→ src/nfs_scanner_pro/ui/main_window.py
→ src/nfs_scanner_pro/scan/scan_engine_mock.py
→ src/nfs_scanner_pro/analysis/analysis_data_source_mock.py
→ src/nfs_scanner_pro/report/report_data_source_mock.py
```

### 5.1u 做验收性能与隔离（Release 031）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_031_Verification_Performance_Isolation/README.md
→ scripts/verification_runtime.py
→ scripts/verification_report.py
→ scripts/verify_all.py
→ scripts/verify_release_031.py
```

### 5.1v 迁移旧验收脚本到隔离 runtime（Release 032）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_032_Migrate_Legacy_Verify_Scripts_To_Isolated_Runtime/README.md
→ scripts/verification_runtime.py
→ scripts/verify_all.py
→ scripts/verify_release_032.py
→ src/nfs_scanner_pro/app_paths.py  # NFS_SCANNER_RUNTIME_DIR
→ runtime/verification/Rxxx/
```

### 5.1w 做 Release 验收脚手架（Release 033）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_033_Release_Verification_Script_Generator/README.md
→ scripts/scaffold_verify_release.py
→ scripts/verify_release_033.py
→ scripts/verify_all.py
```














































































### 5.1 做 Project Workspace UI Verification（Release 034）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_034_Project_Workspace_UI_Verification/README.md
→ scripts/verify_release_034.py
→ scripts/scaffold_verify_release.py
```












































### 5.1 做 Scan Task Workspace Integration（Release 035）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_035_Scan_Task_Workspace_Integration/README.md
→ scripts/verify_release_035.py
→ scripts/scaffold_verify_release.py
```
















### 5.1 做 Real Device Adapter Inventory And Bridge（Release 036）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_036_Real_Device_Adapter_Inventory_And_Bridge/README.md
→ src/nfs_scanner_pro/devices/real/
→ scripts/check_real_devices_safe.py
→ scripts/verify_release_036.py
```

（历史：Analysis Page ScanTask Selection 验收见 Release_036_Analysis_Page_ScanTask_Selection_Integration/）






























### 5.1 做 Real Motion Platform Safe Connect And Position Read（Release 037）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_037_Real_Motion_Platform_Safe_Connect_And_Position_Read/README.md
→ scripts/verify_release_037.py
→ scripts/scaffold_verify_release.py
```
















### 5.1 做 Real Motion Manual Safe Jog Unlock（Release 038）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_038_Real_Motion_Manual_Safe_Jog_Unlock/README.md
→ scripts/verify_release_038.py
→ scripts/scaffold_verify_release.py
```




### 5.1 做 Real Spectrum Analyzer Safe Connect And Read（Release 039）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_039_Real_Spectrum_Analyzer_Safe_Connect_And_Read/README.md
→ scripts/verify_release_039.py
→ scripts/scaffold_verify_release.py
```




### 5.1 做 Real Spectrum Single Point Amplitude Read（Release 040）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_040_Real_Spectrum_Single_Point_Amplitude_Read/README.md
→ scripts/verify_release_040.py
→ scripts/scaffold_verify_release.py
```




### 5.1 做 Real Joint Single Point Sample（Release 041）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_041_Real_Joint_Single_Point_Sample/README.md
→ scripts/verify_release_041.py
→ scripts/scaffold_verify_release.py
```




### 5.1 做 Real Small Area 3x3 Scan Dry Run Planner（Release 042）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_042_Real_Small_Area_3x3_Scan_Dry_Run_Planner/README.md
→ scripts/verify_release_042.py
→ scripts/scaffold_verify_release.py
```




### 5.1 做 Manual Step By Step 3x3 Point Sampling（Release 043）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_043_Manual_Step_By_Step_3x3_Point_Sampling/README.md
→ scripts/verify_release_043.py
→ scripts/scaffold_verify_release.py
```




### 5.1 做 Real Hardware Functional Layer Offline Complete（Release 044）

```text
spec/AI_INDEX.md
→ docs/product-spec/release/Release_044_Real_Hardware_Functional_Layer_Offline_Complete/README.md
→ scripts/verify_release_044.py
→ scripts/scaffold_verify_release.py
```



### 5.2 做领域模型 / Mock JSON / 状态机

```text
spec/AI_INDEX.md
→ spec/Context_Pack/Domain_Context.md
→ spec/Registry/Domain.yaml
→ docs/product-spec/domain/01_Overview/Object_Relationships.md
→ docs/product-spec/domain/04_State_Machines/Scan_State_Machine.md（若涉及扫描）
```

### 5.3 做扫描 / 设备 / 业务流程

```text
spec/AI_INDEX.md
→ spec/Context_Pack/Workflow_Context.md
→ spec/Registry/Workflow.yaml
→ docs/product-spec/workflow/Run_Scan.md 等
```

### 5.4 做 Qt / PySide6 实现

```text
spec/AI_INDEX.md
→ spec/Context_Pack/Qt_Context.md
→ spec/Registry/Qt.yaml
→ docs/product-spec/qt-spec/
→ docs/product-spec/design-system/07_Qt_Implementation/
```

### 5.5 做架构 / ADR / 文档审查

```text
spec/AI_INDEX.md
→ spec/Context_Pack/Decision_Context.md
→ spec/Registry/Decision.yaml
→ spec/Task_Guide/Review_Documentation.md 或 Review_Code.md
```

### 5.6 了解 Release 历程

```text
spec/Registry/Release.yaml
→ docs/product-spec/release/
```

---

## 6. Release 路线图（摘要）

| Release | 内容 | 状态 |
|---|---|---|
| 008 | UI Wireframe 尺寸 | ✅ 已交付 |
| 009 | Design System 扁平 | ✅ 历史 |
| 009.5 | UI Foundation 分层 | ✅ 已交付 |
| 009.8 | Domain Model | ✅ 已交付 |
| **009.9** | **AI Knowledge Index** | ✅ 本 Release |
| **010** | **High Fidelity Design** | ✅ 扫描页候选定稿 |
| **010.5** | **High Fidelity Completion** | ⏳ 本 Release |
| 011 | MainWindow Prototype (PySide6) | 🔒 待 010.5 验收 |

---

## 7. 关键对象命名（避免读错旧 doc）

| 旧 (data/) | 新 (domain/) |
|---|---|
| Sample | **PCB** |
| Scan | **ScanTask** |

---

## 8. 常用链接速查

| 主题 | 文档 |
|---|---|
| 主窗口线框 | [ui-wireframe/01_Main_Window_1920x1080.md](../docs/product-spec/ui-wireframe/01_Main_Window_1920x1080.md) |
| Design Token | [design-system/01_Foundation/Design_Tokens.md](../docs/product-spec/design-system/01_Foundation/Design_Tokens.md) |
| Scan 七态 | [domain/04_State_Machines/Scan_State_Machine.md](../docs/product-spec/domain/04_State_Machines/Scan_State_Machine.md) |
| Domain→UI | [domain/07_Implementation_Guide/Domain_To_UI_Mapping.md](../docs/product-spec/domain/07_Implementation_Guide/Domain_To_UI_Mapping.md) |
| ADR 列表 | [decision/README.md](../docs/product-spec/decision/README.md) |

---

## 9. 校验 Registry 路径

```bash
python scripts/check_spec_registry_paths.py
```

失败则修复 YAML 或补文档，**不得**带缺失路径进入 Release 010。

---

## 10. 维护

- 新增文档 → [Maintenance/How_To_Add_New_Document.md](Maintenance/How_To_Add_New_Document.md)
- 更新 YAML → [Maintenance/How_To_Update_Registry.md](Maintenance/How_To_Update_Registry.md)
- AI 行为 → [Maintenance/AI_Context_Rules.md](Maintenance/AI_Context_Rules.md)

---

**读完本文件后，打开对应 Registry YAML，不要跳过。**
