# Release 036 — Analysis Page ScanTask Selection Integration

## 1. Release 目标

在 Release_035 完成 ScanTask 与 Project/Workspace 绑定后，锁住分析页数据源联动：ScanTask 下拉按当前项目隔离、默认加载最新任务、切换任务/项目后 Breadcrumb、光标读数、热力图 Mock 状态同步。

## 2. 为什么需要分析页 ScanTask 选择联动

- 切换项目后若仍显示旧项目 ScanTask，分析/报告数据会错位。
- `resolve_project_and_tasks()` 曾回退到其他有数据的项目，导致空项目误加载他人扫描结果。
- 需要在 UI 层验收 ScanTask QComboBox 与 `AnalysisDataSourceMock` 的一致性。

## 3. 覆盖范围

| 区域 | 检查项 |
|---|---|
| 数据准备 | 项目 A 两个 ScanTask、项目 B 一个 ScanTask |
| AnalysisDataSource | 按项目 list_scan_tasks / build_dataset |
| 分析页默认加载 | 当前项目任务列表、默认最新任务 |
| ScanTask 切换 | Breadcrumb、光标读数、状态栏 |
| 项目切换 | 分析页刷新、不显示旧项目任务 |
| 空项目 | 空状态、无旧任务泄漏 |
| 控件回归 | Trace / 频率 / LUT / 透明度 |
| 隔离 | `runtime/verification/R036/` |

## 4. 本次不做什么

- ❌ 不接真实设备 / 不实现真实热力图或频谱分析
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局 / 左侧导航

## 5. verify_release_036.py 检查项

```
compileall / runtime_isolation / prepare_multi_project_scan_tasks / mainwindow_boot
analysis_data_source_project_isolation / analysis_default_load_current_project
scantask_dropdown_switching / project_switch_analysis_refresh / empty_project_state
cursor_readout_dataset_binding / trace_frequency_lut_controls / page_switch_regression
workspace_state_saved / no_real_device_access / no_high_fidelity_changes
```

## 6. 与 project_mock.py 的关系

`AnalysisPage.refresh_data_source()` 通过 `project_mock.get_scan_project_name()` 获取当前项目，仅列举该项目的 ScanTask；`MainWindow._refresh_project_ui()` 在项目切换时触发刷新。

## 7. 与 AnalysisDataSourceMock 的关系

从 `get_mock_projects_dir()` 列举项目与 scans 子目录；`list_scan_tasks(project)` 与 `build_dataset(project, task_id)` 提供分析页数据。

## 8. 与 AnalysisDatasetMock 的关系

`build_dataset()` 构造带 `project_name`、`task_id`、`source_path` 的数据集；`cursor_readout()` 供 UI 光标面板绑定。

## 9. 与 ScanResultPersistenceMock 的关系

验收脚本直接写入 `scan_result.json` / `scan_summary.json` / `scan_points_preview.csv` 到 R036 隔离目录，模拟扫描完成后的持久化结构。

## 10. 与 runtime/verification/R036 的关系

验收脚本调用 `verification_runtime.enter_release_runtime("R036")`；所有 mock_projects 与 workspace JSON 仅写入该目录。

## 11. 本地运行方式

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_036.py
python scripts/verify_all.py --only 036
```

## 12. CI 运行方式

GitHub Actions 执行全量 `python scripts/verify_all.py`。

## 13. 后续 Release 约束

1. 分析页 ScanTask 列表必须严格绑定当前项目，禁止跨项目回退。
2. 项目切换必须刷新分析页数据源（即使未重新进入分析页）。
3. 新 Release 验收写入 `runtime/verification/Rxxx/`。
