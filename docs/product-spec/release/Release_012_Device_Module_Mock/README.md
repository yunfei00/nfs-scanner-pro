# Release 012 — Device Module Mock

## 1. Release 目标

在 **Release 011 主窗口壳层** 基础上，将设备页升级为完整的 **Device Center Mock**，包含四设备卡片、Jog/HxHy 控件、相机预览占位与右侧设备配置 Dock。**不接真实硬件**。

## 2. 本次实现范围

- 运动平台卡片：坐标、行程、速度、回零/停止/刷新、XY/Z Jog
- 频谱仪卡片：型号/地址/Trace/频率、测试连接/Sweep/读 Trace
- 相机卡片：预览 Mock、拍照/刷新/设置
- 舵机卡片：Hx/Hy 切换、校准、偏移补偿
- 右侧「设备配置」Dock：DeviceProfile、连接策略、安全限制、高级折叠
- Mock 数据：`MOTION_STATE`、`SPECTRUM_STATE`、`CAMERA_STATE`、`SERVO_STATE`、`DEVICE_PROFILE`
- 按钮点击更新底部状态栏 `Mock：…` 文案

## 3. 本次不做什么

- ❌ 串口 / COM 扫描 / TCP/VISA / 相机 SDK / 舵机驱动
- ❌ 真实扫描线程与热力图算法
- ❌ 修改扫描页 PCB 画布、frameless 标题栏、左侧导航结构
- ❌ 修改 `prototypes/high_fidelity/` HTML

## 4. 输入规范

- Release 011 主窗口：[Release_011_MainWindow_PySide6_Prototype/README.md](../Release_011_MainWindow_PySide6_Prototype/README.md)
- 设备页高保真：[high-fidelity/pages/device/Device_Page_High_Fidelity.md](../../high-fidelity/pages/device/Device_Page_High_Fidelity.md)
- 领域对象：[domain/03_Device_Objects/](../../domain/03_Device_Objects/)
- 设备状态机：[domain/04_State_Machines/Device_State_Machine.md](../../domain/04_State_Machines/Device_State_Machine.md)

## 5. 输出文件

```text
src/nfs_scanner_pro/ui/pages/device_page.py
src/nfs_scanner_pro/ui/mock_data.py
src/nfs_scanner_pro/ui/device_config_dock.py
src/nfs_scanner_pro/ui/widgets/device_card.py
src/nfs_scanner_pro/ui/widgets/jog_control.py
src/nfs_scanner_pro/ui/widgets/camera_preview_mock.py
src/nfs_scanner_pro/ui/widgets/hxhy_control.py
src/nfs_scanner_pro/ui/widgets/device_profile_panel.py
src/nfs_scanner_pro/resources/styles/dark_theme.qss
docs/product-spec/release/Release_012_Device_Module_Mock/README.md
```

## 6. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

启动后点击左侧 **设备** 进入 Device Center。

## 7. 验收标准

| # | 项 |
|---|---|
| 1 | `python scripts/run_mock_ui.py` 可启动 |
| 2 | 设备页四张卡片完整 |
| 3 | 运动平台含 Jog / 回零 / 坐标 |
| 4 | 频谱仪含测试连接 / Sweep / Trace |
| 5 | 相机含预览 Mock / 拍照 |
| 6 | 舵机含 Hx/Hy 切换 / 校准 |
| 7 | 右侧 Dock「设备配置」含 DeviceProfile |
| 8 | 按钮仅更新 Mock 状态栏 |
| 9 | 不接真实设备 |
| 10 | 简体中文 UI |

## 8. 后续 Release_013 建议

- 设备连接状态机驱动卡片徽标（connected / disconnected / fault）
- 设备页与顶部设备状态栏联动刷新
- 设备 Mock 日志面板（视图菜单控制）
- ScanTask 与设备就绪状态联动（仍 Mock）

---

**依赖**：Release 011  
**任务入口**：`spec/AI_INDEX.md` → Device / UI Context
