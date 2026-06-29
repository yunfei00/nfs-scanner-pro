# Release 009.8 — Enterprise Domain Model

## 1. Release 背景

Release 008~009.5 已固定 UI 线框、Design System 与 Enterprise UI Foundation，但**产品领域对象**仍分散在 `data/`、`workflow/`、`rules/` 与多份 ADR 中。实现 MainWindow Prototype 前，需要一份可导航、含状态机与异常恢复的**统一领域模型**，避免 UI 与业务对象脱节。

## 2. 为什么在 Release_010 MainWindow 前必须补充领域模型

| 风险 | 无统一 Domain Model 时 |
|---|---|
| Mock UI 字段来源不明 | 表单绑什么 JSON 键不确定 |
| 扫描状态与 UI 不同步 | 无 ScanTask 状态机约束 |
| 设备异常处理各自为政 | 无 Error Recovery 模型 |
| Hx/Hy、Alignment 语义混乱 | Region ≠ ScanTask 边界不清 |
| 文件布局与对象不对应 | project.json / scan.json 缺映射 |

MainWindow Prototype 需要 Mock 数据与状态切换，**必须先有 Domain Model**。

## 3. 本次解决的 6 个问题

1. **对象模型分散** → `domain/02_Core_Objects/` + `03_Device_Objects/`
2. **UI 强、业务关系弱** → `01_Overview/Object_Relationships.md` + Mermaid
3. **缺少状态机** → `04_State_Machines/` 10 篇
4. **缺少生命周期** → `05_Lifecycle/` 6 篇（细化 `data/Life_Cycle.md`）
5. **缺少异常恢复模型** → `06_Error_Recovery/` 8 篇
6. **缺少产品级 ADR 总结** → ADR-0015 ~ **ADR-0020**

## 4. 本次不做什么

- ❌ 不写 PySide6 业务代码
- ❌ 不生成 UI 高保真图片
- ❌ 不实现真实设备驱动
- ❌ 不改已有 `workflow/` 业务流程文字（仅引用对齐）
- ❌ 不删除 `data/` 旧文档
- ❌ 不启动 Release 010 MainWindow Prototype

## 5. 输出文件清单

```text
docs/product-spec/
├── release/Release_009_8_Enterprise_Domain_Model/README.md
├── decision/ADR-0015 ~ ADR-0020
└── domain/
    ├── README.md
    ├── 01_Overview/           (3)
    ├── 02_Core_Objects/       (12)
    ├── 03_Device_Objects/     (5)
    ├── 04_State_Machines/     (11)
    ├── 05_Lifecycle/          (6)
    ├── 06_Error_Recovery/      (9)
    └── 07_Implementation_Guide/ (5)
```

**说明**：`data/` 目录保留；`domain/` 为 Release 009.8 权威领域入口。`Sample` 在领域层统一为 **PCB** 对象（与 ADR-0001 一致）。

## 6. 进入 Release 010 MainWindow Prototype 的条件

1. `domain/` 全部分层文档 Review 完成。
2. `Object_Relationships.md` 与 `07_File_System.md` 无冲突。
3. ScanTask / Region 状态机与 `design-system/04_Interaction/Scan_State_Interaction.md` 对齐。
4. `Domain_To_UI_Mapping.md` 与 Release 009.5 组件 objectName 一致。
5. ADR-0015 ~ **0020** Accepted；与 ADR-0001~0010 无矛盾。
6. Mock 数据 JSON 结构可仅从 Domain 文档推导（Release 010 首 PR 验证）。
7. **Scan 七态状态机**与 **Device/Alignment 状态机**文档 Review 完成。
8. **Release 009.9 AI Knowledge Index** 完成，`python scripts/check_spec_registry_paths.py` 零缺失；实现从 [spec/AI_INDEX.md](../../../../spec/AI_INDEX.md) → [Build_MainWindow.md](../../../../spec/Task_Guide/Build_MainWindow.md) 进入。

## AI 入口（009.9 之后）

| 组件 | 路径 |
|---|---|
| 第一入口 | [spec/AI_INDEX.md](../../../../spec/AI_INDEX.md) |
| Registry | [spec/Registry/](../../../../spec/Registry/README.md) |
| Task Guide | [spec/Task_Guide/](../../../../spec/Task_Guide/README.md) |

---

**状态**：Accepted  
**版本**：Release 009.8（含关系说明、状态机八要素、ADR 0016–0020）  
**依赖**：Release 008、009、009.5、009.9；`data/`；ADR-0001~0021
