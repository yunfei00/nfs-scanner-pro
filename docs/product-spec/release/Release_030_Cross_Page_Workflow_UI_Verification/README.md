# Release 030 — Cross-Page Workflow UI Verification

## 1. Release 目标

补齐 **跨页面完整 UI 工作流自动验收**：在一个 offscreen 脚本中串联扫描页 → 设备页 → 分析页 → 报告页 → 扫描页，验证从用户角度的一条完整 Mock 工作流。

## 2. 为什么需要跨页面工作流自动验收

- Release 024~029 分别验证了模块与单页 UI，但缺少 **单脚本内端到端 UI 路径** 回归。
- 扫描完成 → 分析加载 → 报告草稿 是核心用户旅程，应在一次运行中验证 Dock / 工具栏 / 状态栏 / runtime 产物联动。

## 3. 覆盖范围

| 检查项 | 内容 |
|---|---|
| compileall | 编译与模块 import |
| mainwindow_boot | offscreen MainWindow、项目就绪 |
| initial_scan_page | 扫描页 Dock / 工具栏 / Breadcrumb |
| device_mock_ready | 设备页四类设备 + 状态栏 + 切回扫描 |
| scan_ui_workflow | 开始扫描 → tick 完成 → UI 状态 |
| scan_result_files | runtime 三文件、CSV ≤200 行 |
| analysis_loads_scan_task | 加载刚完成 ScanTask + 数据集字段 |
| analysis_mock_interactions | Trace/频率/LUT/透明度/导出 Mock |
| report_creates_draft | 新建报告 → report_draft.json + 预览 |
| report_export_mock | 预览/PDF/Word/Excel 仅状态栏 |
| cross_page_regression | 九步切页 Dock/工具栏回归 |
| workspace_state_saved | workspace_state_mock.json |
| no_real_device_access | 禁止外设字符串 + 无导出文件 |

## 4. 本次不做什么

- ❌ 不接真实设备 / 串口 / SCPI / 相机 / 舵机
- ❌ 不实现真实扫描 / 热力图 / 报告引擎
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局
- ❌ 不把「项目」加入左侧导航

## 5. verify_release_030.py 检查项

见上表；扫描优先 **工具栏「开始扫描」`.click()`**，分析/报告通过导航与工具栏按钮触发真实 UI 绑定。

## 6. 与四页 UI 的关系

- **扫描页**：Release 026 工具栏与完成持久化
- **设备页**：Release 029 设备 Mock 就绪检查
- **分析页**：Release 027 数据源与参数控件
- **报告页**：Release 028 草稿与导出 Mock

## 7. 与 ScanEngineMock 的关系

- UI QTimer 驱动 `tick()` 至 6461 点完成；`ScanResultPersistenceMock` 写入 runtime 三文件。

## 8. 与 AnalysisDataSourceMock 的关系

- 读取刚完成 ScanTask 的 `build_dataset()` 与 `cursor_readout()`。

## 9. 与 ReportDataSourceMock 的关系

- `build_report_context()` 供报告页；`ReportPersistenceMock.save_draft()` 写入 `report_draft.json`。

## 10. 与 verify_all.py 的集成

`verify_all.py` 串行执行 022~030，030 不递归调用 verify_all。

## 11. 本地运行

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_030.py
python scripts/verify_all.py
```

## 12. CI 运行方式

GitHub Actions `NFS Scanner Verification` 工作流执行 `verify_all.py`，自动包含 Release 030。

## 13. 后续 Release 约束

1. 每个 Release 新增 `verify_release_XXX.py` 并注册到 `verify_all.py`。
2. 只有 `verify_all.py` PASS 才 commit / push。
3. 跨页工作流类 Release 应优先真实按钮 click，必要时记录 fallback。
