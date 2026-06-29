# Device State Machine — 设备总状态机

> 聚合 Motion、Spectrum、Camera、Servo 四子系统。ScanTask 能否进入「准备就绪」由本机判定。

## 1. 状态列表

| 内部 ID | 中文名 | 说明 |
|---|---|---|
| `Unconfigured` | 未配置 | 无 DeviceProfile 或未填连接参数 |
| `Disconnected` | 未连接 | 已配置但未建立连接 |
| `Connecting` | 连接中 | 正在握手/打开串口/SCPI |
| `Connected` | 已连接 | 空闲可接受命令 |
| `Busy` | 忙碌 | 扫描/移动/切换/拍照中 |
| `Error` | 错误 | 连接或命令失败，需恢复 |
| `Disabled` | 禁用 | 用户或系统关闭该设备（如相机可选关闭） |

---

## 2. 状态说明

### 未配置
无端口/IP/Profile。设备页表单可编辑。ScanTask **未就绪**（必需设备）。

### 未连接
配置有效但未 connect。允许「连接设备」。Spectrum/Motion 未连接 → ScanTask 未就绪。

### 连接中
禁止重复连接。statusBar「正在连接…」。超时 → 错误。

### 已连接
指示点**绿色**（Camera 可选为灰/绿）。ScanTask 必需设备满足时可贡献「准备就绪」。

### 忙碌
ScanTask Scanning 期间 Motion/Spectrum 为 Busy。禁止 disconnect、改波特率。

### 错误
指示点**红色**（Camera 可选设备仍用**灰/黄**，非红，ADR-0003）。log ERROR。ScanTask → 暂停或错误。

### 禁用
Camera/Servo 可 Disabled。不参与 ScanTask 前置校验（Camera）；Servo 禁用时 Hx/Hy 切换需人工确认。

---

## 3. 状态转换表

| 从 | 事件 | 到 |
|---|---|---|
| 未配置 | 保存配置 | 未连接 |
| 未连接 | connect | 连接中 |
| 连接中 | success | 已连接 |
| 连接中 | fail | 错误 |
| 已连接 | scanStart | 忙碌 |
| 忙碌 | scanEnd | 已连接 |
| 已连接 | disconnect | 未连接 |
| 已连接 | fault | 错误 |
| 错误 | retry | 连接中 |
| 错误 | disable | 禁用 |
| 禁用 | enable | 未连接 |

**ScanTask 门控**：Motion=已连接∧Spectrum=已连接 → 必需设备 OK；Camera/Servo 任意。

---

## 4. 允许动作

| 状态 | 允许 |
|---|---|
| 未配置 | 编辑 Profile、选端口 |
| 未连接 | connect、改配置 |
| 已连接 | 回零、拍照、开始扫描（若 Region OK） |
| 忙碌 | 暂停/停止扫描 |
| 错误 | 重连、查 log、导出诊断 |
| 禁用 | 启用设备 |

---

## 5. 禁止动作

- 忙碌时 disconnect
- 扫描中修改 Motion 串口参数
- Camera 错误阻止 ScanTask（仅警告）
- 未连接态开始扫描

---

## 6. UI 表现

| 状态 | deviceStatus 圆点 | 设备页 |
|---|---|---|
| 未配置 | 灰 | 表单空 |
| 未连接 | 灰 | 「连接」可用 |
| 连接中 | 蓝闪 | 进度 |
| 已连接 | 绿 | 状态正常 |
| 忙碌 | 蓝 | 命令锁定 |
| 错误 | 红（Camera 除外） | 重试按钮 |
| 禁用 | 灰 | 开关 off |

---

## 7. 日志记录

`{Project}/logs/device.log` — `DeviceConnected` / `DeviceDisconnected` / `DeviceError`

---

## 8. 错误恢复

见 [Device_Error_Recovery.md](../06_Error_Recovery/Device_Error_Recovery.md) 及各子设备 Recovery 文档。

## 子状态机

- [Motion_State_Machine.md](Motion_State_Machine.md)
- [Spectrum_State_Machine.md](Spectrum_State_Machine.md)
- [Camera_State_Machine.md](Camera_State_Machine.md)
- [Servo_State_Machine.md](Servo_State_Machine.md)
