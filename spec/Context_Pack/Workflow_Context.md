# Workflow Context — 流程上下文

## 流程链

| 步骤 | 文档 |
|---|---|
| 新建项目 | workflow/Create_Project.md |
| 打开项目 | workflow/Open_Project.md |
| 连接设备 | workflow/Connect_Devices.md |
| 准备样品/拍照 | workflow/Prepare_Sample.md |
| 建 Region | workflow/Create_Region.md |
| 区域对齐 | workflow/Alignment.md |
| 扫描 | workflow/Run_Scan.md |
| Hx/Hy | workflow/Run_Hx_Hy.md |
| 分析 | workflow/Analysis.md |
| 导出报告 | workflow/Export_Report.md |
| 恢复项目 | workflow/Resume_Project.md |

## 前置条件（扫描）

Project 打开 · Region 选中 · 起终点 · Motion+Spectrum 就绪 · Camera **非必须**

## 异常恢复（摘要）

- 运动/频谱：Pause ScanTask
- 相机：降级，不阻断
- 数据损坏：见 Data_Error_Recovery

→ [domain/06_Error_Recovery/README.md](../../docs/product-spec/domain/06_Error_Recovery/README.md)

## 细节入口

- [workflow/README.md](../../docs/product-spec/workflow/README.md)
- [03_Workflow.md](../../docs/product-spec/03_Workflow.md)

## Registry

[spec/Registry/Workflow.yaml](../Registry/Workflow.yaml)
