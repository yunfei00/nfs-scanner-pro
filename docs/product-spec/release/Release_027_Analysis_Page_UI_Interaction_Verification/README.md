# Release 027 — Analysis Page UI Interaction Verification

## 1. Release 目标

补齐 **分析页 UI 层自动验收**：验证 MainWindow 左侧「分析」导航、AnalysisPage、AnalysisDataSourceMock、右侧「分析参数」Dock、Trace/频率/LUT/透明度控件、光标读数、导出 Mock、状态栏之间的联动。

## 2. 为什么需要分析页 UI 自动验收

- Release 021/024 验证了数据源与全链路，但未专门验证 **导航 click → Dock 切换 → 参数控件 → 状态栏/Breadcrumb**。
- 分析页依赖 Release 020 扫描结果持久化，UI 回归应独立于人工点击。

## 3. 覆盖范围

| 检查项 | 内容 |
|---|---|
| compileall | 编译与模块 import |
| mock_scan_result_ready | ST-VERIFY-027 三文件 fixture |
| mainwindow_boot | offscreen MainWindow、单 Dock |
| analysis_navigation | 点击「分析」→ 分析参数 Dock、Breadcrumb、状态栏 |
| analysis_dock_content | 数据源/显示/光标/导出分组与控件 |
| analysis_data_source | AnalysisDataSourceMock + ScanTask 联动 |
| trace_frequency_lut_controls | Trace/频率/模式/LUT/透明度切换 |
| cursor_readout | X/Y/Z/频率/幅度/相位、锁定/复制 |
| export_mock_actions | 三项导出仅更新状态栏 |
| analysis_canvas_state | PCB + 热力图 Mock、色带、空状态 |
| page_switch_regression | 四页 Dock 标题回归 |
| no_real_device_access | 禁止外设字符串 |

## 4. 本次不做什么

- ❌ 不接真实设备 / 串口 / SCPI / 频谱仪
- ❌ 不实现真实热力图 / 频谱分析算法
- ❌ 不生成 PDF / Word / Excel / 真实图片
- ❌ 不改 high_fidelity HTML / 主窗口布局
- ❌ 不把「项目」加入左侧导航

## 5. verify_release_027.py 检查项

见上表；优先通过 **左侧导航按钮 `.click()`** 触发切页，辅以 `QApplication.processEvents()` 驱动控件变更与导出 Mock 定时器。

## 6. 与 AnalysisDataSourceMock 的关系

- 从 `runtime/mock_projects/` 读取 Release 020 扫描结果三文件。
- `build_dataset()` / `cursor_readout()` 提供 Mock 读数；验收不访问真实算法。

## 7. 与 Release 020 扫描结果持久化的关系

- 若无 ST-VERIFY-027，脚本自动创建 Mock 三文件于 `runtime/mock_projects/iPhone16_Mainboard/scans/ST-VERIFY-027/`。
- runtime 不进入 Git。

## 8. 与 verify_all.py 的集成

`verify_all.py` 串行执行 022~027，027 不递归调用 verify_all。

## 9. 本地运行

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_027.py
python scripts/verify_all.py
```

## 10. CI 运行方式

GitHub Actions `NFS Scanner Verification` 工作流执行 `verify_all.py`，自动包含 Release 027。

## 11. 后续 Release 约束

1. 每个 Release 新增 `verify_release_XXX.py` 并注册到 `verify_all.py`。
2. 只有 `verify_all.py` PASS 才 commit / push。
3. UI 交互类 Release 优先 offscreen 按钮触发，避免绕过绑定。
