# Release 019 — Scan Engine Abstraction Mock

## 1. Release 目标

将 Release 013 中 UI 内部的扫描 Mock 逻辑抽象为独立 **ScanEngineMock** 层，UI 仅保留 QTimer 驱动 `tick()`。**不接真实设备。**

## 2. 为什么需要 Scan Engine 抽象层

- UI 不应直接拥有扫描状态机与路径生成逻辑。
- 后续真实扫描只需替换 `ScanEngine`，无需重写扫描页。
- 扫描结果需关联 **DeviceSnapshot**（来自 DeviceManagerMock）。

## 3. 本次实现范围

- `scan/` 包：状态、配置、路径、进度、结果、引擎
- `ScanEngineMock.tick()` — 无 PySide6 依赖
- UI QTimer 100 ms 调用 `tick()`
- 扫描页 / 画布 / 参数 Dock 集成
- 停止 / 完成 / 进度 / 坐标 / 画布当前点

## 4. 本次不做什么

- ❌ 真实运动 / SCPI / 相机 / 舵机
- ❌ 真实扫描线程 / 热力图算法 / 写盘
- ❌ 修改设备页 / 分析页 / 报告页 / 导航

## 5. ScanEngineMock 架构

```text
scan/
  scan_state.py         ScanState 枚举
  scan_task_config.py   ScanTaskConfig
  scan_point.py         ScanPointMock
  scan_path_mock.py     蛇形路径 generate_path / get_point
  scan_progress.py      ScanProgressMock
  scan_result_mock.py   ScanResultMock + device_snapshot
  scan_engine_mock.py   ScanEngineMock.prepare/start/stop/tick
```

## 6. ScanTaskConfig

项目 / 区域 / 探头 / 频率 / 起止坐标 / 步进 / total_points=6461 等 Mock 默认值。

## 7. ScanPathMock

按 config 生成蛇形网格索引，按需计算 ScanPointMock，不预存 6461 点。

## 8. ScanProgressMock

current_index / percent / remaining_time / current_point / as_status_text()

## 9. DeviceSnapshot 关系

`start()` 时调用 `device_manager.get_snapshot()`，写入 `ScanResultMock.device_snapshot`。

## 10. UI 集成方式

- `scan_page.py`：`get_scan_engine()` + QTimer → `engine.tick()`
- `scan_canvas_view.py`：`set_current_scan_point()` 高亮当前点
- `scan_parameter_dock.py`：扫描中锁定字段（沿用 Release 013）

## 11. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

扫描页 → 开始扫描 → 观察进度 / 坐标 / 画布点移动 → 停止或等待完成。

## 12. 验收标准

- [ ] ScanEngineMock 状态 SCANNING / COMPLETED
- [ ] 进度与扫描点增长
- [ ] 画布当前点移动
- [ ] stop / complete 行为正确
- [ ] get_snapshot() 在结果中
- [ ] ScanEngine 不依赖 QTimer
- [ ] compileall 通过

## 13. 后续 Release_020 建议

- **Analysis Engine Mock** — 扫描结果 → 分析任务
- **ScanEngine 真实适配器** — 替换 Mock，接口不变
- **ScanResult 持久化** — 写入项目文件夹 Mock JSON

## 强调

- **本次不接真实设备，只做 Mock。**
- **UI 不应直接拥有扫描逻辑。**
- **后续真实扫描必须替换 ScanEngine，而不是重写 UI。**
