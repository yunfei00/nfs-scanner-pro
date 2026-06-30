# Release 021 — Analysis Data Source Mock

## 1. Release 目标

分析页从 **runtime/mock_projects/.../scans/** 读取 Release 020 保存的 Mock 扫描结果，作为分析数据源。不做真实分析算法。

## 2. 为什么分析页需要数据源层

- 分析不应依赖静态 `mock_data.ANALYSIS_TASK`。
- 扫描 → 持久化 → 分析 是核心工作流。
- 后续真实分析算法应替换 `AnalysisDataSource`，而非重写分析页 UI。

## 3. 本次实现范围

- `AnalysisDataSourceMock` — 列出/加载 scan_result.json、scan_summary.json、scan_points_preview.csv
- `AnalysisDatasetMock` — 内存数据集 + cursor_readout
- 分析参数 Dock「数据源」分组：项目、ScanTask 下拉、数据状态、预览点、文件来源
- Breadcrumb / 光标读数 / 状态栏联动
- 无扫描结果时空状态提示

## 4. 本次不做什么

- ❌ 真实热力图 / 频谱分析
- ❌ 读取真实项目目录或设备数据
- ❌ 修改扫描引擎 / 设备页 / 报告页

## 5. AnalysisDataSourceMock 架构

```text
analysis/
  analysis_data_source_mock.py   list/load/build_dataset
  analysis_dataset_mock.py       AnalysisDatasetMock
  analysis_state.py              AnalysisDataState
```

## 6. AnalysisDatasetMock

project / task_id / frequency / preview_points / peak / device_snapshot / source_path

## 7. 与 Scan Result Persistence Mock 的关系

**只读** Release 020 目录：

```text
runtime/mock_projects/{project}/scans/{task_id}/
```

不重复保存、不新建目录。

## 8. 空状态处理

- Dock 提示：「未发现 Mock 扫描结果，请先在扫描页完成一次 Mock 扫描。」
- 画布 overlay：「未加载扫描结果」
- 状态栏：「分析就绪，未发现 Mock 扫描结果」

## 9. 运行方式

```bash
python scripts/run_mock_ui.py
```

1. 扫描页完成一次 Mock 扫描（生成 runtime 文件）
2. 左侧 **分析** → 右侧 Dock 选择 ScanTask

## 10. 验收标准

- [ ] 能识别 runtime 中 ScanTask
- [ ] 加载三文件，CSV ≤ 200 行
- [ ] Breadcrumb 含 ScanTask
- [ ] 无光标/无数据时空状态
- [ ] compileall 通过

## 11. 后续 Release_022 建议

- **Analysis Engine Mock** — 基于 dataset 的统计/滤波 Mock
- **扫描结果列表** — 分析页历史任务管理
- **真实 AnalysisDataSource** — 兼容当前 JSON schema

## 强调

- **只读取 Mock 扫描结果。**
- **不做真实分析 / 热力图。**
- **后续算法必须基于 AnalysisDataSource 层替换。**
