# Release 020 — Scan Result Persistence Mock

## 1. Release 目标

扫描完成后，将 **ScanResultMock** 保存到 `runtime/mock_projects/` 下的 Mock 扫描目录，包含 JSON / CSV 预览 / 摘要。**不保存真实测量数据。**

## 2. 为什么需要扫描结果持久化 Mock

- 验证 ScanTask 在项目文件夹中的落盘结构（ADR / Domain Mapping 预演）。
- 为分析页 / 报告页后续读取扫描结果打样。
- 与 ScanEngineMock 解耦：引擎负责生成结果，Persistence 负责写入。

## 3. 本次实现范围

- `ScanResultPersistenceMock` — save / load_summary / list_scan_tasks
- `scan_result_serializer.py` — JSON / CSV / summary 序列化
- `app_paths.py` — mock_projects / scan 目录路径
- 扫描自然完成时自动 `save_result()`
- 状态栏：`扫描完成，Mock 结果已保存`
- `.gitignore`：`runtime/**/*.json` / `runtime/**/*.csv`

## 4. 本次不做什么

- ❌ 6461 点全量写盘
- ❌ 真实设备数据 / 真实热力图
- ❌ 写入用户真实项目目录 D:/NFS_Projects/...
- ❌ 修改设备 / 分析 / 报告页

## 5. 文件保存路径

```text
runtime/mock_projects/{project_name}/scans/{task_id}/
  scan_result.json
  scan_points_preview.csv
  scan_summary.json
```

## 6. scan_result.json

完整 Mock 元数据：task_id、项目/区域/探头/频率、device_snapshot、result_type=mock。

## 7. scan_points_preview.csv

最多 **200** 行 Mock 预览点：`index,x,y,z,frequency,amplitude,phase,timestamp`。

## 8. scan_summary.json

total_points、saved_preview_points、peak_amplitude、peak_position、mock=true。

## 9. 与 ScanEngineMock 的关系

`finalize_stop()` 自然完成时：

1. 创建 `ScanResultMock`（含 path、device_snapshot）
2. `ScanResultPersistenceMock.save_result(result)`
3. `on_message` 通知保存路径或失败原因

ScanEngine **不依赖** UI 控件。

## 10. 运行方式

```bash
python scripts/run_mock_ui.py
```

扫描页 → 开始扫描 → 等待完成 → 检查 `runtime/mock_projects/.../scans/ST-XXXXXX/`。

## 11. 验收标准

- [ ] 扫描完成生成三文件
- [ ] CSV ≤ 200 数据行
- [ ] 状态栏提示 Mock 结果已保存
- [ ] runtime 不在 Git 中
- [ ] compileall 通过

## 12. 后续 Release_021 建议

- **Analysis Engine Mock** — 读取 scan_summary / preview 生成分析任务
- **扫描结果列表 UI** — 项目内 ScanTask 历史
- **真实 ScanResult 适配器** — 兼容当前 JSON schema

## 强调

- **只保存 Mock 结果。**
- **runtime 不进入 Git。**
- **后续真实扫描结果格式应兼容当前结构。**
