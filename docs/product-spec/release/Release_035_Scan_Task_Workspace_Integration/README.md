# Release 035 — Scan Task Workspace Integration

## 1. Release 目标

验证 ScanTask 与当前项目 / 工作区状态的联动：项目切换后扫描页 Breadcrumb、`ScanTaskConfig`、扫描结果路径、分析/报告数据源均按项目隔离，产物写入 `runtime/verification/R035/`。

## 2. 为什么需要 ScanTask 与 Workspace 集成验收

- Release_034 锁定了项目 / 工作区 UI，但扫描结果仍可能写入错误项目目录。
- `ScanTaskConfig` 若硬编码项目名，切换项目后分析/报告页会读到错误 ScanTask。
- 需要确保 **项目 A / 项目 B 扫描结果互不覆盖**，且 workspace JSON 保存当前项目。

## 3. 覆盖范围

| 区域 | 检查项 |
|---|---|
| 项目切换 | Breadcrumb、ScanTaskConfig、状态栏、workspace 保存 |
| 扫描持久化 | iPhone16_Mainboard / RF_Module_Test 独立 scans 目录 |
| ScanTaskConfig | `from_current_project()` 绑定 name + default_region |
| AnalysisDataSource | 按项目 list_scan_tasks / build_dataset |
| ReportDataSource | build_report_context + report_draft.json 按项目 |
| Workspace | current_project / recent_projects 恢复 |
| 隔离 | `runtime/verification/R035/` |

## 4. 本次不做什么

- ❌ 不接真实设备 / 不打开串口 / 不发送 SCPI
- ❌ 不实现真实扫描 / 热力图算法
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局 / 左侧导航

## 5. verify_release_035.py 检查项

```
compileall / runtime_isolation / mainwindow_boot / current_project_init
project_switch_scan_sync / project_a_scan_result_path / project_b_scan_result_path
scantask_config_project_binding / analysis_data_source_project_isolation
report_data_source_project_isolation / workspace_project_restore
page_switch_regression / no_real_device_access / no_high_fidelity_changes
```

## 6. 与 project_mock.py 的关系

当前项目由 `project_mock` 内存态维护；`get_scan_project_name()` 与 `ScanTaskConfig.from_current_project()` 读取 `project.name` 作为扫描持久化目录名。

## 7. 与 workspace_state_mock.py 的关系

`workspace_state_mock.json` 保存 `current_project` 与 `recent_projects`；在 `NFS_SCANNER_RUNTIME_DIR=R035` 下写入隔离目录。

## 8. 与 ScanTaskConfig 的关系

`ScanTaskConfig.from_current_project()` 从 `project_mock.get_current_project()` 读取 `name` 与 `default_region`；ScanPage 启动扫描前调用该方法。

## 9. 与 ScanResultPersistenceMock 的关系

扫描完成时 `save_result()` 使用 `result.config.project_name` 构造 `mock_projects/{project}/scans/{task_id}/` 路径。

## 10. 与 AnalysisDataSourceMock / ReportDataSourceMock 的关系

两者通过 `get_mock_projects_dir()` 列举项目，并按项目名隔离 `list_scan_tasks` / `build_dataset` / `build_report_context`。

## 11. 与 runtime/verification/R035 的关系

验收脚本调用 `verification_runtime.enter_release_runtime("R035")`；所有 mock_projects 与 workspace JSON 仅写入该目录。

## 12. 本地运行方式

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_035.py
python scripts/verify_all.py --only 035
```

## 13. CI 运行方式

GitHub Actions 执行全量 `python scripts/verify_all.py`。

## 14. 后续 Release 约束

1. 扫描/分析/报告 Mock 数据必须跟随当前项目名，禁止硬编码单一项目。
2. 新 Release 验收写入 `runtime/verification/Rxxx/`。
3. 左侧导航禁止加入「项目」入口。
