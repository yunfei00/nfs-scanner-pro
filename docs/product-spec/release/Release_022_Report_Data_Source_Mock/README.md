# Release 022 — Report Data Source Mock

## 1. Release 目标

报告页从 **Release 015 纯静态 Mock** 升级为可基于 **Release 020 扫描结果 / Release 021 分析数据源** 生成 **Mock 报告草稿** 的报告入口。**不生成真实 PDF / Word / Excel。**

## 2. 为什么报告页需要数据源层

- 报告应引用已完成的 ScanTask，而非硬编码 `mock_data.REPORTS`。
- 扫描 → 持久化 → 分析 → **报告** 是核心交付链路。
- 后续真实报告引擎应替换 `ReportDataSource` / `ReportDraft` 层，而非重写报告页 UI。

## 3. 本次实现范围

- `ReportDataSourceMock` — 复用 `AnalysisDataSourceMock`，列出/加载 ScanTask，构建报告上下文
- `ReportDraftMock` — 报告草稿内存模型 + `from_analysis_dataset`
- `ReportPreviewModel` — UI 预览数据（白色 PDF 风页面 Mock）
- `ReportPersistenceMock` — 保存/加载 `report_draft.json`
- 报告列表：虚拟默认报告 + runtime 草稿
- 新建报告 → 保存 `runtime/mock_projects/.../reports/.../report_draft.json`
- 报告设置 Dock 选项影响草稿字段（不生成真实文件）
- 导出 PDF / Word / Excel 仅状态栏 Mock 提示

## 4. 本次不做什么

- ❌ 真实 PDF / Word / Excel 生成
- ❌ 真实报告引擎 / 模板渲染
- ❌ 读取真实项目目录或设备数据
- ❌ 修改扫描页状态机、设备页、分析页结构
- ❌ 修改主窗口 rightDock 架构 / frameless / 左侧导航

## 5. ReportDataSourceMock 架构

```text
report/
  report_data_source_mock.py   list/load/build_report_context
  report_draft_mock.py         ReportDraftMock
  report_preview_model.py      ReportPreviewModel
  report_persistence_mock.py   save/load/list drafts
```

复用 `AnalysisDataSourceMock` 只读 Release 020 三文件：

```text
runtime/mock_projects/{project}/scans/{task_id}/
  scan_result.json
  scan_summary.json
  scan_points_preview.csv
```

## 6. ReportDraftMock

字段：report_id、report_name、project_name、region_name、scan_task_id、probe_name、frequency、created_at、模板/Logo/质量、内容开关、summary、peak_amplitude、peak_position、source_path。

默认报告名称示例：`CPU_Area_Hx_2.45GHz_报告`

## 7. ReportPersistenceMock

```text
runtime/mock_projects/{project_name}/reports/{report_id}/report_draft.json
```

- 只保存 Mock 草稿 JSON
- runtime 不进入 Git

## 8. 与 Release_020 / 021 的关系

| 层级 | 目录 | 读写 |
|---|---|---|
| 扫描结果 (020) | `.../scans/{task_id}/` | 只读 |
| 分析数据源 (021) | 同上 | 只读 |
| 报告草稿 (022) | `.../reports/{report_id}/` | 读写 JSON |

不重复保存扫描结果。

## 9. 空状态处理

- 无 ScanTask：预览 overlay「未发现 Mock 扫描结果，请先完成一次 Mock 扫描。」
- 状态栏：「报告就绪，未发现 Mock 扫描结果」
- 新建报告：「Mock：未发现扫描结果，请先完成一次 Mock 扫描」
- JSON/CSV 损坏：返回错误信息，不崩溃

## 10. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

1. 扫描页完成一次 Mock 扫描（或已有 `runtime/mock_projects/.../scans/`）
2. 左侧 **报告** → 查看列表与预览
3. 点击 **新建报告** → 检查 `runtime/.../reports/.../report_draft.json`

## 11. 验收标准

- [ ] 能识别 runtime 中 ScanTask
- [ ] 报告列表显示默认报告名 + 草稿
- [ ] 预览含 ScanTask、峰值幅度/位置
- [ ] 新建报告生成 report_draft.json
- [ ] 导出仅更新状态栏
- [ ] 无扫描结果时空状态
- [ ] compileall 通过

## 12. 后续 Release_023 建议

- **Report Engine Mock** — 基于 ReportDraft 的章节/分页 Mock
- **报告模板注册表** — 多模板 JSON schema
- **真实 ReportDataSource** — 兼容当前 draft JSON schema

## 强调

- **本次只生成 Mock 报告草稿。**
- **不生成真实 PDF / Word / Excel。**
- **不读取真实设备数据。**
- **后续真实报告引擎必须基于 ReportDataSource / ReportDraft 层替换。**
