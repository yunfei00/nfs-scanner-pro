# Release 045 — Real Fake Mock Hardware Mode Switch And Debug Guide

## 1. Release 目标

在 Release_044 真实硬件功能层离线实现基础上，增加 **Mock / Fake / Real** 三种硬件模式切换、设备页 UI、安全探测与调试文档/脚本。本 Release **重点不是接设备成功**，而是让模式边界清晰、默认安全。

## 2. 三种硬件模式

| 模式 | 实现 | 连接真实设备 |
|------|------|--------------|
| Mock | `MockDeviceManager` | 否（默认） |
| Fake Hardware | `FakeTransport` + `RealDeviceManager` | 否 |
| Real Hardware | `RealDeviceManager` | 仅 `NFS_ENABLE_REAL_HARDWARE=1` + 安全探测 |

## 3. Mock 模式说明

- 默认模式
- 设备页四卡片行为与 Release_029 一致
- 用于 UI 回归与无设备演示

## 4. Fake Hardware 模式说明

- 切换后不连接真实设备
- 状态栏提示「已切换到 Fake Hardware 模式」
- 可用于 `hardware_debug_wizard.py --fake-check` 与 `run_real_scan_offline.py --fake-run`

## 5. Real Hardware 模式说明

- 切换后**不自动连接**
- 显示风险提示：需 `NFS_ENABLE_REAL_HARDWARE=1` 并点击 **安全探测**
- 安全探测仅调用 `test_all_safe()`：status/position、IDN/frequency/marker、enumerate、get_state

## 6. 为什么 Real 模式不自动连接

防止启动或切换模式时误开串口、socket、相机或舵机。真实连接必须用户显式开启总开关并点击安全探测。

## 7. Device Page 模式切换

设备页 breadcrumb 下方增加：

- 硬件模式下拉框：Mock / Fake / Real
- Real 模式下显示 **安全探测** 按钮
- 模式提示标签 `hardwareModeHint`

## 8. 安全探测按钮

- 未设置 `NFS_ENABLE_REAL_HARDWARE=1` → 返回 disabled，不打开任何设备
- 已设置 → `RealDeviceManager.test_all_safe()`，禁止 jog/move/home/sweep/capture/servo switch

## 9. hardware_debug_wizard.py 用法

```bash
python scripts/hardware_debug_wizard.py
python scripts/hardware_debug_wizard.py --show-env
python scripts/hardware_debug_wizard.py --fake-check
python scripts/hardware_debug_wizard.py --real-check
```

## 10. docs/hardware-debug-guide.md 说明

完整分步调试顺序、安全开关表、故障排查与 PowerShell 示例见 `docs/hardware-debug-guide.md`。

## 11. 本次不做什么

- ❌ 不默认连接真实设备
- ❌ 不自动运动 / sweep / 拍照 / 切舵机
- ❌ 不提供 real-run 扫描 UI 入口（留给 Release_046）
- ❌ 不改 high_fidelity HTML / 主窗口布局 / 左侧导航

## 12. 下一步 Release_046 建议

**真实扫描 UI 控制台**：接入 dry-run / fake-run / real-run 三种执行入口，与当前硬件模式及安全开关联动。

## 验收

```bash
python scripts/verify_release_045.py
python scripts/verify_all.py --only 045
```
