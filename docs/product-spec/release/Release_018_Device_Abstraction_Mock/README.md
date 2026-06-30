# Release 018 — Device Abstraction Mock

## 1. Release 目标

在 **Release 012 设备页 UI** 基础上，建立 **设备抽象层 Mock**（`src/nfs_scanner_pro/devices/`），为后续接入真实硬件提供统一接口。**本次不接真实设备。**

## 2. 为什么需要设备抽象层

- UI 不应直接调用串口、SCPI、相机 SDK、舵机驱动。
- 扫描 / 分析 / 报告模块将来通过 **DeviceManager** 获取设备状态与快照。
- Mock 层先验证接口与状态机，再替换为真实驱动。

## 3. 本次实现范围

- `DeviceState` 枚举（未配置 / 未连接 / 连接中 / 已连接 / 忙碌 / 错误 / 禁用）
- `DeviceType`（motion / spectrum / camera / servo）
- `BaseDeviceMock` 基类（connect / disconnect / snapshot / 回调）
- 四类设备 Mock：Motion / Spectrum / Camera / Servo
- `DeviceManagerMock`：connect_all / get_snapshot / get_device_status
- `DeviceSnapshot`：timestamp + 四设备 snapshot
- 设备页按钮调用 Mock 层；设备状态栏从 Manager 读取

## 4. 本次不做什么

- ❌ 串口 / COM 扫描 / SCPI / 相机 SDK / 舵机控制
- ❌ 真实设备线程 / 真实扫描
- ❌ 修改扫描画布 / frameless / 左侧导航 / high_fidelity HTML

## 5. 设备抽象层结构

```text
devices/
  base.py              BaseDeviceMock
  device_state.py      DeviceState
  device_types.py      DeviceType
  device_snapshot.py   build_device_snapshot()
  device_manager_mock.py  DeviceManagerMock
  motion_mock.py       MotionControllerMock
  spectrum_mock.py     SpectrumAnalyzerMock
  camera_mock.py       CameraSystemMock
  servo_mock.py        ServoSystemMock
```

## 6. DeviceManager Mock

- 持有四类设备实例
- `connect_all()` → 全部 connected
- `get_device_status()` → 设备状态栏结构
- `get_snapshot()` → 供后续 ScanTask 保存设备状态
- `get_device_manager()` 单例供 UI 使用

## 7. DeviceSnapshot Mock

```python
{
  "timestamp": "2026-...",
  "motion": {...},
  "spectrum": {...},
  "camera": {...},
  "servo": {...}
}
```

## 8. UI 集成方式

- `device_page.py`：按钮 → `DeviceManagerMock` 对应方法 → 状态栏 Mock 文案
- `device_status_bar.py`：`refresh_from_manager()` 读取 chip 状态（绿/灰/红）
- `mock_data.py`：由 `sync_mock_data()` 同步常量（兼容旧引用）

## 9. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

左侧 **设备** → 测试回零 / Jog / 频谱测试 / 拍照 / 切换 Hy。

## 10. 验收标准

- [ ] 设备页按钮调用 Mock 层，状态栏显示 Mock 结果
- [ ] Jog 更新坐标 Mock 数值
- [ ] 设备状态栏来自 DeviceManagerMock
- [ ] `get_snapshot()` 返回四类快照
- [ ] 无串口 / SCPI / 相机 / 舵机真实访问
- [ ] compileall 通过

## 11. 后续 Release_019 建议

- **MotionController 真实串口适配器**（实现同一 BaseDevice 接口）
- **Spectrum VISA/SCPI 适配器**（可选 Mock 切换）
- **ScanTask 启动前 `is_all_ready()` 检查**

## 强调

- **本次不接真实设备，只做 Mock。**
- **后续真实设备必须走 `devices/` 抽象层。**
- **UI 禁止直接调用硬件 API。**
