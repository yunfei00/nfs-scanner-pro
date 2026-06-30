# Product Specification

This folder stores product design documents for NFS Scanner Professional.

## Core Documents

- [00 Introduction](00_Introduction.md)
- [01 Product Vision](01_Product_Vision.md)
- [02 Product Goals](02_Product_Goals.md)
- [03 Workflow](03_Workflow.md)
- [04 Object Model](04_Object_Model.md)
- [05 Navigation](05_Navigation.md)
- [06 Glossary](06_Glossary.md)
- [07 File System](07_File_System.md)

## Releases

| Release | 说明 | 入口 |
|---|---|---|
| Release 008 | UI 线框与固定尺寸 | [ui-wireframe/README.md](ui-wireframe/README.md) |
| Release 009 | Enterprise Design System（扁平文档） | [release/Release_009_Enterprise_Design_System/README.md](release/Release_009_Enterprise_Design_System/README.md) |
| **Release 009.5** | **Enterprise UI Foundation（UI 权威）** | [release/Release_009_5_Enterprise_UI_Foundation/README.md](release/Release_009_5_Enterprise_UI_Foundation/README.md) |
| **Release 009.8** | **Enterprise Domain Model（领域权威）** | [release/Release_009_8_Enterprise_Domain_Model/README.md](release/Release_009_8_Enterprise_Domain_Model/README.md) |
| **Release 009.9** | **AI Knowledge Index（AI 第一入口）** | [release/Release_009_9_AI_Knowledge_Index/README.md](release/Release_009_9_AI_Knowledge_Index/README.md) |
| **Release 010** | **High Fidelity Design（扫描页候选定稿）** | [release/Release_010_High_Fidelity_Design/README.md](release/Release_010_High_Fidelity_Design/README.md) |
| **Release 010.5** | **High Fidelity Completion（四页 + 状态补全）** | [release/Release_010_5_High_Fidelity_Completion/README.md](release/Release_010_5_High_Fidelity_Completion/README.md) |
| Release 011 | MainWindow PySide6 Prototype | [release/Release_011_MainWindow_PySide6_Prototype/README.md](release/Release_011_MainWindow_PySide6_Prototype/README.md) |
| Release 012 | Device Module Mock | [release/Release_012_Device_Module_Mock/README.md](release/Release_012_Device_Module_Mock/README.md) |
| Release 013 | Scan Module Mock | [release/Release_013_Scan_Module_Mock/README.md](release/Release_013_Scan_Module_Mock/README.md) |
| Release 014 | Analysis Module Mock | [release/Release_014_Analysis_Module_Mock/README.md](release/Release_014_Analysis_Module_Mock/README.md) |
| Release 015 | Report Module Mock | [release/Release_015_Report_Module_Mock/README.md](release/Release_015_Report_Module_Mock/README.md) |
| Release 016 | Project File System Mock | [release/Release_016_Project_File_System_Mock/README.md](release/Release_016_Project_File_System_Mock/README.md) |
| Release 017 | Workspace Persistence Mock | [release/Release_017_Workspace_Persistence_Mock/README.md](release/Release_017_Workspace_Persistence_Mock/README.md) |

## 高保真设计（Release 010 / 010.5）

**入口**：[high-fidelity/README.md](high-fidelity/README.md)

| 页面 | 浏览器原型 |
|---|---|
| 扫描 | [prototypes/high_fidelity/index.html](../prototypes/high_fidelity/index.html) |
| 设备 | [prototypes/high_fidelity/device.html](../prototypes/high_fidelity/device.html) |
| 分析 | [prototypes/high_fidelity/analysis.html](../prototypes/high_fidelity/analysis.html) |
| 报告 | [prototypes/high_fidelity/report.html](../prototypes/high_fidelity/report.html) |

状态说明：[high-fidelity/states/](high-fidelity/states/)

## PySide6 Mock UI（Release 011 — 待 010.5 验收）

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

源码：`src/nfs_scanner_pro/` · 启动脚本：`scripts/run_mock_ui.py`

## AI 入口层（Release 009.9）

**所有 AI 任务必须先读** [spec/AI_INDEX.md](../../spec/AI_INDEX.md)，禁止无目标全仓库扫描。

| 组件 | 路径 |
|---|---|
| 第一入口 | [spec/AI_INDEX.md](../../spec/AI_INDEX.md) |
| 架构摘要 | [spec/Architecture_Handbook.md](../../spec/Architecture_Handbook.md) |
| 上下文包 | [spec/Context_Pack/](../../spec/Context_Pack/README.md) |
| Registry | [spec/Registry/](../../spec/Registry/README.md) |
| Task Guide | [spec/Task_Guide/](../../spec/Task_Guide/README.md) |
| 维护 | [spec/Maintenance/](../../spec/Maintenance/README.md) |

校验：`python scripts/check_spec_registry_paths.py`

## Domain Model（Release 009.8）

**入口**：[domain/README.md](domain/README.md)

| 层 | 路径 | 说明 |
|---|---|---|
| Overview | [domain/01_Overview/](domain/01_Overview/Domain_Principles.md) | 原则、关系图 |
| Core Objects | [domain/02_Core_Objects/](domain/02_Core_Objects/Project.md) | Project、PCB、Region、ScanTask… |
| Device Objects | [domain/03_Device_Objects/](domain/03_Device_Objects/MotionSystem.md) | 四类设备 + Snapshot |
| **State Machines** | [domain/04_State_Machines/](domain/04_State_Machines/README.md) | **Scan 七态等** |
| **Lifecycle** | [domain/05_Lifecycle/](domain/05_Lifecycle/ScanTask_Lifecycle.md) | 端到端业务链 |
| **Error Recovery** | [domain/06_Error_Recovery/](domain/06_Error_Recovery/README.md) | Motion/Spectrum/Scan/Data… |
| Implementation | [domain/07_Implementation_Guide/](domain/07_Implementation_Guide/README.md) | UI/Qt/文件映射 |

对象关系 Mermaid：[domain/01_Overview/Object_Relationships.md](domain/01_Overview/Object_Relationships.md)

历史兼容：[data/](data/README.md)（Sample→PCB，Scan→ScanTask 见 domain 命名规则）

## Design System（Release 009.5）

**入口**：[design-system/README.md](design-system/README.md)

| 层 | 路径 | 说明 |
|---|---|---|
| Foundation | [design-system/01_Foundation/](design-system/01_Foundation/README.md) | Design Token、原则 |
| Components | [design-system/02_Components/](design-system/02_Components/README.md) | 组件库 15 件 |
| Patterns | [design-system/03_Patterns/](design-system/03_Patterns/README.md) | 主窗口、扫描工作台等模式 |
| Interaction | [design-system/04_Interaction/](design-system/04_Interaction/README.md) | 鼠标、键盘、扫描状态 |
| Animation | [design-system/05_Animation/](design-system/05_Animation/README.md) | 导航、Dock、进度动效 |
| QSS | [design-system/06_QSS/](design-system/06_QSS/README.md) | 样式与 Token 映射 |
| Qt Implementation | [design-system/07_Qt_Implementation/](design-system/07_Qt_Implementation/README.md) | objectName、GraphicsView |

核心 Token：[design-system/01_Foundation/Design_Tokens.md](design-system/01_Foundation/Design_Tokens.md)

### 历史兼容（Release 009 扁平文档）

`design-system/01_Color_System.md` … `15_QSS_Guide.md` 仍保留，已标注迁移目标。

## Other Modules

- [data/](data/README.md) — 首版数据模型（见 [domain/](domain/README.md) 权威层）
- [decision/](decision/README.md) — ADR（AI Index：[0021](decision/ADR-0021-AI-Knowledge-Index.md)；高保真：[0022](decision/ADR-0022-High-Fidelity-Before-PySide6.md)）
- [rules/](rules/README.md) — 产品规则
- [workflow/](workflow/README.md) — 业务流程
- [pages/](pages/README.md) — 页面规格
- [wireframe/](wireframe/00_Product_Navigation.md) — 旧版文字线框
- [qt-spec/](qt-spec/01_Qt_Layout_Spec.md) — Qt 布局（与 07_Qt_Implementation 同步）

## Visual Design (V1, 部分参考)

- [product-design/](../product-design/README.md) — 高保真 SVG（ADR-0012 起以线框 + Design System 为准）
