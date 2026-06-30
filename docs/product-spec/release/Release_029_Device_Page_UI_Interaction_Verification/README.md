# Release 029 — Device Page UI Interaction Verification

## 1. Release 目标

补齐 **设备页 UI 层自动验收**：验证 MainWindow 左侧「设备」导航、DevicePage、DeviceManagerMock、右侧「设备配置」Dock、运动平台 Jog、频谱仪测试、相机拍照、舵机 Hx/Hy 切换、设备状态栏、底部状态栏之间的 Mock 联动。

## 2. 为什么需要设备页 UI 自动验收

- Release 012/018 实现了设备 Mock 与 DeviceManagerMock，但未专门验证 **导航 click → 四设备卡片 → Jog/按钮 → 状态栏**。
- 设备页是扫描前置条件，UI 回归应独立于人工点击与真实硬件。

## 3. 覆盖范围

| 检查项 | 内容 |
|---|---|
| compileall | 编译与模块 import |
| mainwindow_boot | offscreen MainWindow、单 Dock |
| device_navigation | 点击「设备」→ 设备配置 Dock、状态栏 |
| device_config_dock | DeviceProfile/连接策略/安全限制/高级 |
| device_manager_mock | connect_all / get_snapshot / is_all_ready |
| device_status_bar | 四设备 chip 简体中文与 connected 状态 |
| motion_card_ui | 运动平台卡片与 Jog 按钮 |
| motion_actions | 回零/停止/刷新/Jog 坐标变化 |
| spectrum_card_ui | 频谱仪卡片字段 |
| spectrum_actions | 测试连接 / Sweep / 读取 Trace |
| camera_card_ui | 相机卡片与预览 Mock |
| camera_actions | 拍照 / 刷新预览 / 打开设置 |
| servo_card_ui | 舵机系统与 Hx/Hy 控件 |
| servo_actions | 切换 / 校准 / 偏移补偿 |
| page_switch_regression | 五页 Dock/工具栏回归 |
| no_real_device_access | 禁止外设字符串 |

## 4. 本次不做什么

- ❌ 不接真实设备 / 不打开串口 / 不扫描 COM 口
- ❌ 不发送 SCPI / 不访问真实相机 / 不控制真实舵机
- ❌ 不实现真实扫描
- ❌ 不改 high_fidelity HTML / 主窗口布局
- ❌ 不把「项目」加入左侧导航

## 5. verify_release_029.py 检查项

见上表；优先通过 **左侧导航按钮 `.click()`** 与各卡片 **objectName 按钮 `.click()`** 触发，辅以 `QApplication.processEvents()`。

## 6. 与 DeviceManagerMock 的关系

- 统一管理 Motion / Spectrum / Camera / Servo 四类 Mock 设备。
- `connect_all()`、`get_device_status()`、`get_snapshot()` 供验收与 UI 同步。

## 7. 与设备状态栏的关系

- `DeviceStatusBar.refresh_from_manager()` 读取 `DeviceManagerMock.get_device_status()`。
- 单行展示四设备 chip 与扫描上下文 meta，不换行、不含「项目」。

## 8. 与 verify_all.py 的集成

`verify_all.py` 串行执行 022~029，029 不递归调用 verify_all。

## 9. 本地运行

```bash
set QT_QPA_PLATFORM=offscreen
python scripts/verify_release_029.py
python scripts/verify_all.py
```

## 10. CI 运行方式

GitHub Actions `NFS Scanner Verification` 工作流执行 `verify_all.py`，自动包含 Release 029。

## 11. 后续 Release 约束

1. 每个 Release 新增 `verify_release_XXX.py` 并注册到 `verify_all.py`。
2. 只有 `verify_all.py` PASS 才 commit / push。
3. UI 交互类 Release 优先 offscreen 按钮触发，避免绕过绑定。
