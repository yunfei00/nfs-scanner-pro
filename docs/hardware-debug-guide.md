# 真实硬件调试指南（Release 045）

本文档说明 nfs-scanner-pro 的三种硬件模式、安全开关与分步调试顺序。**当前文档用于调试准备，不代表真实设备已经联调成功。**

## 1. 三种硬件模式

| 模式 | 说明 | 默认 |
|------|------|------|
| **Mock** | 使用 `MockDeviceManager`，UI 原型与离线演示，不连接真实设备 | ✅ 是 |
| **Fake Hardware** | 使用 `FakeTransport` 模拟真实命令链路，可离线验证流程与数据格式 | 否 |
| **Real Hardware** | 使用 `RealDeviceManager`，仅表示意图；**必须**额外开启安全开关才能连接 | 否 |

在设备页可切换：**Mock 模式 / Fake 模式 / Real 模式**。  
也可通过环境变量覆盖（优先级高于持久化文件）：

```powershell
$env:NFS_HARDWARE_MODE="mock"   # 或 fake / real
```

## 2. 为什么默认是 Mock

- 保证 UI 与验收脚本在无设备环境下可重复运行
- 避免误连串口、频谱仪 socket、相机或舵机
- 真实硬件能力分层发布，Mock 层保持稳定回归基线

## 3. Fake Hardware 用途

在没有物理设备时：

- 测试真实流程（连接 → 查询 → 断开）
- 验证 SCPI / GRBL 命令构造
- 验证 joint sample、扫描计划、结果保存格式
- 运行 `run_real_scan_offline.py --fake-run`

Fake 模式**不会**打开真实串口或网络连接。

## 4. Real Hardware 调试顺序

### 第一步：运动平台状态

```powershell
$env:NFS_HARDWARE_MODE="real"
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_MOTION_PORT="COM6"
python scripts/debug_real_motion.py --status
```

### 第二步：频谱仪 IDN

```powershell
$env:NFS_SPECTRUM_BACKEND="socket"
$env:NFS_SPECTRUM_HOST="192.168.1.100"
$env:NFS_SPECTRUM_PORT="5025"
python scripts/debug_real_spectrum.py --idn
```

### 第三步：频谱仪 Marker 幅度

```powershell
python scripts/debug_real_spectrum.py --marker
```

### 第四步：相机枚举

```powershell
$env:NFS_ENABLE_REAL_CAMERA="1"
python scripts/debug_real_camera.py --list
```

### 第五步：舵机状态

```powershell
$env:NFS_ENABLE_REAL_SERVO="1"
python scripts/debug_real_servo.py --state
```

### 第六步：fake-run 扫描

```powershell
python scripts/run_real_scan_offline.py --fake-run
```

### 第七步：真实扫描前检查

完整 **real-run** 扫描需后续 Release（建议 Release_046）提供 UI 控制台与 dry-run / fake-run / real-run 入口。  
当前 Release 仅支持 **安全探测**（`test_all_safe`）：不运动、不 sweep、不拍照、不切舵机。

## 5. 安全开关说明

| 环境变量 | 作用 |
|----------|------|
| `NFS_HARDWARE_MODE` | `mock` / `fake` / `real`，选择硬件模式意图 |
| `NFS_ENABLE_REAL_HARDWARE=1` | **总开关**：允许 Real 层连接真实设备 |
| `NFS_ENABLE_REAL_MOTION_JOG=1` | 允许点动（本 Release 安全探测不包含） |
| `NFS_ENABLE_REAL_MOTION_MOVE=1` | 允许绝对移动 |
| `NFS_ENABLE_REAL_MOTION_HOME=1` | 允许回零 |
| `NFS_ENABLE_REAL_SPECTRUM_WRITE=1` | 允许 SCPI 写命令 |
| `NFS_ENABLE_REAL_SPECTRUM_SWEEP=1` | 允许 sweep |
| `NFS_ENABLE_REAL_SPECTRUM_TRACE_READ=1` | 允许读取完整 trace |
| `NFS_ENABLE_REAL_CAMERA=1` | 允许打开相机 |
| `NFS_ENABLE_REAL_SERVO=1` | 允许舵机控制 |
| `NFS_ENABLE_REAL_SCAN_EXECUTION=1` | 允许真实扫描执行 |

**Real 模式 ≠ 已启用真实硬件。** 未设置 `NFS_ENABLE_REAL_HARDWARE=1` 时，安全探测返回 disabled，不会打开任何设备。

## 6. 统一调试入口

```powershell
python scripts/hardware_debug_wizard.py
python scripts/hardware_debug_wizard.py --show-env
python scripts/hardware_debug_wizard.py --fake-check
python scripts/hardware_debug_wizard.py --real-check   # 需 NFS_ENABLE_REAL_HARDWARE=1
```

## 7. 设备页操作

1. 打开 **设备** 页
2. 在 **硬件模式** 下拉框选择 Mock / Fake / Real
3. Real 模式下点击 **安全探测**（需 `NFS_ENABLE_REAL_HARDWARE=1`）
4. 切换模式不会自动连接真实设备

## 8. 出错排查

| 现象 | 可能原因 |
|------|----------|
| COM 端口错误 | 端口号不对、设备未上电、被其他程序占用 |
| pyserial 未安装 | `pip install pyserial` |
| 频谱仪 IP 不通 | 网络、防火墙、IP/端口配置错误 |
| pyvisa 未安装 | `pip install pyvisa`（若使用 VISA 后端） |
| 相机被占用 | 关闭其他采集软件；检查 `NFS_ENABLE_REAL_CAMERA=1` |
| 舵机端口错误 | 检查 `NFS_SERVO_PORT` 与 `NFS_ENABLE_REAL_SERVO=1` |

## 9. 重要声明

- 验收与 CI **默认不**设置 `NFS_ENABLE_REAL_HARDWARE=1`
- 本文档描述调试准备流程，**不保证**现场设备已联调成功
- 危险动作（运动、sweep、拍照、舵机切换）需对应子开关，且不在 Release_045 安全探测范围内
