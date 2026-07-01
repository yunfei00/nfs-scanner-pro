# Release 039 — Real Spectrum Analyzer Safe Connect And Read

## 1. Release 目标

在真实设备 Adapter 桥接（Release_036）与运动平台安全能力（Release_037/038）基础上，接入**真实频谱仪/矢网/频谱分析仪的安全只读查询**：连接、`*IDN?`、系统错误、中心频率、Trace 列表，不修改仪表配置。

## 2. 为什么先做频谱仪安全查询

扫描链路依赖频谱数据，但直接读写 SCPI 配置或启动 sweep 风险高。本阶段先验证 TCP/VISA 连通性与只读查询，确保默认不连接、不写配置、不 sweep。

## 3. NFS_ENABLE_REAL_HARDWARE

统一安全开关。未设置时：

- 不连接 socket / VISA
- 返回 disabled 状态

本 Release **不新增**独立写配置开关（本阶段仅查询）。

## 4. NFS_SPECTRUM_BACKEND

- `socket`（默认）— 使用 `host:port` TCP
- `visa` — 使用 pyvisa 打开 `NFS_SPECTRUM_VISA_ADDRESS`

## 5. NFS_SPECTRUM_HOST / PORT

| 变量 | 默认 |
|------|------|
| `NFS_SPECTRUM_HOST` | `192.168.1.100` |
| `NFS_SPECTRUM_PORT` | `5025` |
| `NFS_SPECTRUM_TIMEOUT` | `3.0` |

## 6. NFS_SPECTRUM_VISA_ADDRESS

默认：`TCPIP0::192.168.1.100::inst0::INSTR`

## 7. SpectrumScpiAdapter 接口

| 方法 | 说明 |
|------|------|
| `connect()` / `disconnect()` | 安全连接/断开 |
| `query(command)` | 白名单 SCPI 查询 |
| `query_idn()` | `*IDN?` |
| `query_system_error()` | `SYST:ERR?` |
| `get_current_frequency()` | `FREQ:CENT?` / `SENS:FREQ:CENT?` |
| `read_trace_info()` | `CALC:PAR:CAT?`（轻量） |
| `test_connection()` | 安全探测序列 |
| `snapshot()` | 结构化状态 |

## 8. 允许的 SCPI 查询命令

- `*IDN?`
- `SYST:ERR?`
- `FREQ:CENT?` / `SENS:FREQ:CENT?`
- `CALC:PAR:CAT?` / `CALC:PAR:SEL?`
- `INST:SEL?` / `CONF?`

## 9. 禁止的 SCPI 命令

- 任何写命令（不带 `?`）
- `INIT` / `SING` / `CAL` / sweep 相关
- `CALC:DATA?` / `TRAC:DATA?` / 大批量 Trace 读取
- 频率/带宽/功率设置

## 10. check_real_devices_safe.py 用法

**默认（不连接）：**

```bash
python scripts/check_real_devices_safe.py
```

**启用后（PowerShell）：**

```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_SPECTRUM_BACKEND="socket"
$env:NFS_SPECTRUM_HOST="192.168.1.100"
$env:NFS_SPECTRUM_PORT="5025"
python scripts/check_real_devices_safe.py
```

## 11. socket 模式示例

```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_SPECTRUM_BACKEND="socket"
$env:NFS_SPECTRUM_HOST="192.168.1.100"
$env:NFS_SPECTRUM_PORT="5025"
python scripts/check_real_devices_safe.py
```

## 12. VISA 模式示例

```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_SPECTRUM_BACKEND="visa"
$env:NFS_SPECTRUM_VISA_ADDRESS="TCPIP0::192.168.1.100::inst0::INSTR"
python scripts/check_real_devices_safe.py
```

## 13. 本地验收

```bash
python scripts/verify_release_039.py
python scripts/verify_all.py --only 039
python scripts/verify_all.py --from 038
```

## 14. 后续 Release_040 建议

**真实频谱仪单点幅度读取** — 在保持只读/安全策略下，读取当前 Trace 上单个频率点的幅度，仍不启动 sweep、不修改仪表配置。
