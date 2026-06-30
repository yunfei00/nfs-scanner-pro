# Release 036 — Real Device Adapter Inventory And Bridge

## 1. 为什么现在停止纯 Mock 验证，转真实设备接入

- Release 022~035 已完成 Mock UI、工作区、ScanTask、分析页数据源联动验收。
- 继续写纯 UI verify 脚本无法推进真实扫描闭环。
- 当前仓库 **无历史真实设备 Python 代码**，仅有 Mock 层与产品规格文档中的 GRBL/SCPI 描述。

## 2. 当前 Mock 架构

| 组件 | 路径 |
|---|---|
| 设备管理器 | `devices/device_manager_mock.py` |
| 运动平台 Mock | `devices/motion_mock.py` |
| 频谱仪 Mock | `devices/spectrum_mock.py` |
| 相机 Mock | `devices/camera_mock.py` |
| 舵机 Mock | `devices/servo_mock.py` |
| UI 入口 | `get_device_manager()` |

## 3. 真实设备接入目标

建立 `devices/real/` Adapter 层，与 Mock 接口对齐，通过安全开关控制，第一阶段只做 **连接 / 查询 / 断开**。

## 4. 安全开关 NFS_ENABLE_REAL_HARDWARE

```bash
# 默认：Mock UI，不连接真实设备
# 启用真实设备安全探测：
set NFS_ENABLE_REAL_HARDWARE=1        # Windows cmd
$env:NFS_ENABLE_REAL_HARDWARE="1"     # PowerShell
export NFS_ENABLE_REAL_HARDWARE=1     # Linux/macOS
```

仅当值为 `1` 时，`RealDeviceManager` 才允许执行安全连接与查询。

## 5. RealDeviceManager 架构

```
RealDeviceManager
├── motion: MotionGrblAdapter
├── spectrum: SpectrumScpiAdapter
├── camera: CameraAdapter
└── servo: ServoAdapter
```

方法：`connect_all_safe()` / `disconnect_all()` / `test_all_safe()` / `get_device_status()` / `get_snapshot()`

## 6. MotionGrblAdapter

- 配置：`COM6` / `115200` / `timeout=2`（可通过环境变量覆盖）
- 允许：`connect()` / `disconnect()` / `query_status()` / `refresh_position()`
- 阻断：`jog()` / `move_to()` / `home()` / `stop()`

## 7. SpectrumScpiAdapter

- 支持 `pyvisa` 或 `socket` TCP/IP fallback
- 允许：`*IDN?` / `FREQ:CENT?` / `CALC:PAR:CAT?`
- 阻断：Sweep / 频率配置变更

## 8. CameraAdapter

- 可选 `opencv-python` 枚举相机
- 不启动实时预览 / 不拍照（默认）

## 9. ServoAdapter

- 仅读取配置
- 阻断 Hx/Hy 切换与校准动作

## 10. check_real_devices_safe.py 用法

```bash
# 默认（不连接）
python scripts/check_real_devices_safe.py

# 启用后安全探测
$env:NFS_ENABLE_REAL_HARDWARE="1"
python scripts/check_real_devices_safe.py
```

## 11. 本次不做什么

- ❌ 不执行 G0/G1 运动 / 不回零
- ❌ 不执行真实扫描路径
- ❌ 不改主窗口 UI 布局
- ❌ 不将 UI 默认切到 RealDeviceManager
- ❌ 不生成真实 PDF / Word / Excel

## 12. 后续 Release_037 建议

**真实运动平台安全连接与位置读取** — 在 `NFS_ENABLE_REAL_HARDWARE=1` 下验证 GRBL 串口连接、M114 位置读取、状态查询稳定性；仍不启用 jog/move/home。

## 13. 代码盘点结果（2026-06）

| 类别 | 结论 |
|---|---|
| 历史真实设备 Python 代码 | **未找到**（仅文档与 Mock） |
| 可复用 | Mock 接口、`DeviceState`、`device_types` |
| 不可直接复用 | 无 GRBL/VISA 历史实现 |
| UI 当前使用 | `DeviceManagerMock` via `get_device_manager()` |
| 真实设备接入点 | `devices/real/` + `check_real_devices_safe.py` |
