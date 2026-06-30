# Release 028 — Report Page UI Interaction Verification

## 1. Release 目标

补齐 **报告页 UI 层自动验收**：验证 MainWindow 左侧「报告」导航、ReportPage、ReportDataSourceMock、ReportPersistenceMock、右侧「报告设置」Dock、报告列表、报告预览、新建报告、预览、导出 PDF/Word/Excel Mock、状态栏之间的联动。

## 2. 为什么需要报告页 UI 自动验收

- Release 022/024 验证了报告数据源与全链路，但未专门验证 **导航 click → 报告工具栏 → 列表/预览 → 草稿持久化**。
- 报告页依赖 Release 020 扫描结果与 Release 022 草稿持久化，UI 回归应独立于人工点击。

## 3. 覆盖范围

| 检查项 | 内容 |
|---|---|
| compileall | 编译与模块 import |
| mock_scan_result_ready | ST-VERIFY-028 三文件 fixture |
| mainwindow_boot | offscreen MainWindow、单 Dock |
| report_navigation | 点击「报告」→ 报告设置 Dock、报告工具栏、状态栏 |
| report_toolbar | 五项报告按钮 + 切回扫描工具栏恢复 |
| report_settings_dock | 模板/导出/内容/高级分组与控件 |
| report_data_source | ReportDataSourceMock 上下文与默认报告名 |
| report_list_ui | 报告列表存在、点击联动 |
| report_preview_ui | PDF Mock 预览字段完整性 |
| create_report_draft | 新建报告 → report_draft.json |
| preview_mock_action | 预览按钮 Mock 状态 |
| export_mock_actions | PDF/Word/Excel 仅状态栏 |
| report_settings_interaction | 模板/质量/内容勾选 → 草稿读取 |
| page_switch_regression | 六步切页 Dock/工具栏回归 |
| no_real_device_access | 禁止外设字符串 + runtime 无导出文件 |

## 4. 本次不做什么

- ❌ 不接真实设备 / 不读取真实设备数据
- ❌ 不生成真实 PDF / Word / Excel
- ❌ 不实现真实报告引擎
- ❌ 不改 high_fidelity HTML / 主窗口布局
- ❌ 不把「项目」加入左侧导航

## 5. verify_release_028.py 检查项

见上表；优先通过 **左侧导航按钮 `.click()`** 与 **工具栏按钮 `.click()`** 触发，辅以 `QApplication.processEvents()` 驱动导出 Mock 定时器。

## 6. 与 ReportDataSourceMock 的关系

- 复用 `AnalysisDataSourceMock` 从 `runtime/mock_projects/` 加载扫描结果。
- `build_report_context()` / `default_report_name()` 提供 Mock 报告上下文与中文报告名。

## 7. 与 ReportPersistenceMock 的关系

- `save_draft()` 写入 `runtime/mock_projects/{project}/reports/{report_id}/report_draft.json`。
- 验收验证新建报告草稿路径与设置字段，runtime 不进入 Git。

## 8. 与 verify_all.py 的集成

`verify_all.py` 串行执行 022~028，028 不递归调用 verify_all。

## 9. 本地运行

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_028.py
python scripts/verify_all.py
```

## 10. CI 运行方式

GitHub Actions `NFS Scanner Verification` 工作流执行 `verify_all.py`，自动包含 Release 028。

## 11. 后续 Release 约束

1. 每个 Release 新增 `verify_release_XXX.py` 并注册到 `verify_all.py`。
2. 只有 `verify_all.py` PASS 才 commit / push。
3. UI 交互类 Release 优先 offscreen 按钮触发，避免绕过绑定。
