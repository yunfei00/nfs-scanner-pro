# Scan State Machine — 扫描任务状态机

> ScanTask 运行期主状态机。UI 须与 [Scan_State_Interaction](../../design-system/04_Interaction/Scan_State_Interaction.md) 及工具栏启用态严格一致。

## 1. 状态列表

| 内部 ID | 中文名 | 说明 |
|---|---|---|
| `NotReady` | 未就绪 | 前置条件未满足，不可开始 |
| `Ready` | 准备就绪 | 校验通过，可开始扫描 |
| `Scanning` | 扫描中 | 正在逐点采集 |
| `Paused` | 暂停 | 用户或系统暂停，保留进度 |
| `Stopping` | 停止中 | 收到停止指令，收尾当前点/写盘 |
| `Completed` | 已完成 | 正常结束，raw 已保存 |
| `Error` | 错误 | 不可继续，需人工处理或重置 |

> 历史文档中的 Pending/Queued/Failed/Cancelled 映射：`NotReady`≈Pending；`Ready`≈Queued；`Error`≈Failed；用户取消可在 `Stopping` 后标记 `Cancelled` 子状态写入 scan.json，UI 仍归入「已完成/错误」展示。

---

## 2. 状态说明（含 UI / 日志 / 设备）

### 未就绪（NotReady）

| 项 | 规则 |
|---|---|
| 进入条件 | 无 Project / 无 Region / 无起终点 / Motion 或 Spectrum 未就绪 |
| 开始扫描 | **禁用** |
| 停止扫描 | **禁用** |
| 参数编辑 | 可编辑（除扫描中锁定项） |
| 设备断开 | 允许（本就未扫） |
| 保存数据 | 允许保存 Project/Region 配置 |
| 状态栏 | 灰色文案「未就绪：{原因}」 |
| 日志级别 | INFO |
| 日志示例 | `ScanTask:NotReady reason=SpectrumDisconnected` |

### 准备就绪（Ready）

| 项 | 规则 |
|---|---|
| 进入条件 | 设备就绪 + Region 有效 + 参数校验通过 |
| 开始扫描 | **启用**（主蓝） |
| 停止扫描 | **禁用** |
| 参数编辑 | **可编辑** |
| 设备断开 | **不建议**；若断开则退回未就绪 |
| 保存数据 | 允许 |
| 状态栏 | 绿色/白字「就绪」 |
| 日志级别 | INFO |
| 日志示例 | `ScanTask:Ready regionId=… pointCount=6461` |

### 扫描中（Scanning）

| 项 | 规则 |
|---|---|
| 进入条件 | 用户开始或暂停恢复 |
| 开始扫描 | **禁用** |
| 停止扫描 | **启用**（危险色） |
| 参数编辑 | **锁定**步进、起终点、Region 范围；频率类可锁定 |
| 设备断开 | **禁止**主动断开；意外断开 → 暂停或错误 |
| 保存数据 | 允许保存 Project；**禁止**修改当前 ScanTask 路径参数 |
| 状态栏 | **蓝色**进度、点数、ETA |
| 日志级别 | INFO + 每 N 点 DEBUG |
| 日志示例 | `ScanTask:Scanning point=120/6461` |

### 暂停（Paused）

| 项 | 规则 |
|---|---|
| 进入条件 | 用户暂停 / 设备短暂异常自动暂停 |
| 开始扫描 | **启用**（文案「继续」） |
| 停止扫描 | **启用** |
| 参数编辑 | 部分锁定（同扫描中） |
| 设备断开 | 允许诊断性操作，恢复前须重连 |
| 保存数据 | 允许；已采 raw **保留** |
| 状态栏 | 黄色「已暂停」 |
| 日志级别 | WARN |
| 日志示例 | `ScanTask:Paused reason=UserPause` |

### 停止中（Stopping）

| 项 | 规则 |
|---|---|
| 进入条件 | 用户点停止 / 正常扫完最后一点 |
| 开始扫描 | **禁用** |
| 停止扫描 | **禁用**（防重复） |
| 参数编辑 | **禁用** |
| 设备断开 | **不允许**新断开请求 |
| 保存数据 | 内部 flush raw，UI 禁止关 Project |
| 状态栏 | 灰色「正在停止…」 |
| 日志级别 | INFO |
| 日志示例 | `ScanTask:Stopping flushRaw=true` |

### 已完成（Completed）

| 项 | 规则 |
|---|---|
| 进入条件 | Stopping 成功收尾 |
| 开始扫描 | **启用**（新 ScanTask 或重扫） |
| 停止扫描 | **禁用** |
| 参数编辑 | **可编辑** |
| 设备断开 | 允许 |
| 保存数据 | 允许；Snapshot **锁定** |
| 状态栏 | 绿色「扫描完成」 |
| 日志级别 | INFO |
| 日志示例 | `ScanTask:Completed scanTaskId=… duration=…` |

### 错误（Error）

| 项 | 规则 |
|---|---|
| 进入条件 | 致命设备错误 / 磁盘失败 / 不可恢复 SCPI |
| 开始扫描 | **禁用**（须先重置到准备就绪） |
| 停止扫描 | **禁用**（已停） |
| 参数编辑 | 只读查看或有限编辑 |
| 设备断开 | 允许（便于检修） |
| 保存数据 | 已写 raw **保留**；允许导出日志 |
| 状态栏 | **红色**错误摘要 |
| 日志级别 | ERROR |
| 日志示例 | `ScanTask:Error code=MOTION_TIMEOUT` |

---

## 3. 状态转换表

| 从 | 事件 | 到 | 备注 |
|---|---|---|---|
| 未就绪 | 前置条件满足 | 准备就绪 | validateAll |
| 准备就绪 | 前置失效 | 未就绪 | 设备掉线等 |
| 准备就绪 | 用户开始 | 扫描中 | 冻结 DeviceSnapshot |
| 扫描中 | 用户暂停 | 暂停 | |
| 暂停 | 用户继续 | 扫描中 | |
| 扫描中 | 用户停止 | 停止中 | |
| 暂停 | 用户停止 | 停止中 | |
| 停止中 | 收尾成功 | 已完成 | |
| 扫描中 | 致命错误 | 错误 | 见 Error Recovery |
| 错误 | 用户重置且条件满足 | 准备就绪 | 不删 raw |
| 扫描中 | 最后一点完成 | 停止中 | 自动 |

---

## 4. 允许动作

| 状态 | 允许 |
|---|---|
| 未就绪 | 编辑 Region、连接设备、打开项目 |
| 准备就绪 | 开始扫描、改参数、拍照 |
| 扫描中 | 暂停、停止、看进度/频谱 |
| 暂停 | 继续、停止、查 log |
| 停止中 | 等待（可显示取消强制，V2） |
| 已完成 | 生成热力图、分析、新 ScanTask |
| 错误 | 查 log、导出诊断、重置状态 |

---

## 5. 禁止动作

- 扫描中修改 Region 起终点或步进
- 停止中关闭 Project 无确认
- 错误态静默覆盖 raw 目录
- 未就绪态开始扫描（按钮须 disabled）
- 扫描中把 Camera 离线当 Error 阻断（相机可选，ADR-0003）

---

## 6. UI 表现（汇总）

| 状态 | toolbarStart | toolbarStop | scanParamDock | statusBar 色 |
|---|---|---|---|---|
| 未就绪 | 灰 | 灰 | 可编辑 | 灰 |
| 准备就绪 | 蓝 | 灰 | 可编辑 | 白/绿 |
| 扫描中 | 灰 | 红 | 部分锁 | 蓝 |
| 暂停 | 蓝「继续」 | 红 | 部分锁 | 黄 |
| 停止中 | 灰 | 灰 | 锁 | 灰 |
| 已完成 | 蓝 | 灰 | 可编辑 | 绿 |
| 错误 | 灰 | 灰 | 受限 | 红 |

Breadcrumb 在 Scanning 显示当前点/通道/频率。

---

## 7. 日志记录

- 路径：`{Project}/logs/scan_{scanTaskId}.log`
- 每次转换：`timestamp | level | from → to | event | payload`
- 与 [Domain_Event_Model](../07_Implementation_Guide/Domain_Event_Model.md) 中 `ScanStarted` / `ScanCompleted` 等对齐

---

## 8. 错误恢复

| 场景 | 目标状态 | 文档 |
|---|---|---|
| 运动超时 | 暂停 或 错误 | [Motion_Error_Recovery.md](../06_Error_Recovery/Motion_Error_Recovery.md) |
| 频谱 SCPI 失败 | 暂停 | [Spectrum_Error_Recovery.md](../06_Error_Recovery/Spectrum_Error_Recovery.md) |
| 中途停止 | 停止中→已完成 | [Scan_Error_Recovery.md](../06_Error_Recovery/Scan_Error_Recovery.md) |
| 设备断开 | 暂停 | [Device_Error_Recovery.md](../06_Error_Recovery/Device_Error_Recovery.md) |
| 热力图失败 | 保持已完成 | raw 不删，Analysis 重试 |

---

## 相关 ADR

- [ADR-0017](../../decision/ADR-0017-Scan-State-Machine.md)
- [ADR-0020](../../decision/ADR-0020-DeviceSnapshot-For-ScanTask.md)

## 相关对象

- [ScanTask.md](../02_Core_Objects/ScanTask.md)
- [ScanTask_Lifecycle.md](../05_Lifecycle/ScanTask_Lifecycle.md)
