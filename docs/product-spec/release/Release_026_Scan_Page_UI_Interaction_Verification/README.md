# Release 026 — Scan Page UI Interaction Verification

## 1. Release 目标

补齐 **扫描页 UI 层自动验收**：验证 MainWindow 工具栏、ScanPage、ScanEngineMock、扫描参数 Dock、状态栏、画布当前点之间的 Mock 联动。

## 2. 为什么需要扫描页 UI 自动验收

- Release 019/024 验证了引擎与全链路，但未专门验证 **按钮 click → UI 绑定 → 参数锁定**。
- 扫描页是核心工作流入口，UI 回归应独立于人工点击。

## 3. 覆盖范围

| 检查项 | 内容 |
|---|---|
| mainwindow_boot | offscreen MainWindow、单 Dock、扫描参数标题 |
| scan_toolbar_buttons | 六项简体中文工具栏按钮 |
| start_scan_ui_binding | 开始扫描 → SCANNING、状态栏、按钮禁用、参数锁定 |
| scan_progress_updates | tick 后 index / 进度 / 状态更新 |
| scan_canvas_current_point | set_current_scan_point + 画布 marker |
| stop_scan_ui_binding | 停止扫描 → 非 SCANNING、恢复编辑 |
| scan_completion_persistence | 6461 点完成 + runtime 三文件 |
| scan_parameter_locking | Dock 控件 lock/unlock |
| page_switch_regression | 四页 Dock 标题回归 |
| no_real_device_access | 禁止外设字符串 |

## 4. 本次不做什么

- ❌ 不接真实设备 / 串口 / SCPI / 相机
- ❌ 不实现真实扫描 / 热力图算法
- ❌ 不生成 PDF / Word / Excel
- ❌ 不改 high_fidelity HTML / 主窗口布局

## 5. verify_release_026.py 检查项

见上表；优先通过 **工具栏按钮 `.click()`** 触发，辅以 `QApplication.processEvents()` 与 `_on_timer_tick()` 驱动。

## 6. 与 ScanEngineMock 的关系

- UI QTimer 调用 `ScanEngineMock.tick()`；验收脚本可手动 tick 加速。
- 完成时 `finalize_stop()` 触发 `ScanResultPersistenceMock.save_result()`。

## 7. 与 ScanResultPersistenceMock 的关系

- 扫描完成后验证 `runtime/mock_projects/.../scans/{task_id}/` 三文件。
- runtime 不进入 Git。

## 8. 与 verify_all.py 的集成

`verify_all.py` 串行执行 022~026，026 不递归调用 verify_all。

## 9. 本地运行

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_026.py
python scripts/verify_all.py
```

## 10. CI 运行方式

GitHub Actions `NFS Scanner Verification` 工作流执行 `verify_all.py`，自动包含 Release 026。

## 11. 后续 Release 约束

1. 每个 Release 新增 `verify_release_XXX.py` 并注册到 `verify_all.py`。
2. 只有 `verify_all.py` PASS 才 commit / push。
3. UI 交互类 Release 优先 offscreen 按钮触发，避免绕过绑定。
