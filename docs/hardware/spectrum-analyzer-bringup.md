# 频谱仪联调清单

## 接口说明

`SpectrumScpiAdapter`：query / write / query_idn / read_marker_amplitude / read_trace_* / configure / sweep（默认关闭）。

## Socket 模式

```powershell
$env:NFS_HARDWARE_MODE="real"
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_SPECTRUM_BACKEND="socket"
$env:NFS_SPECTRUM_HOST="192.168.1.100"
$env:NFS_SPECTRUM_PORT="5025"
python scripts/debug_real_spectrum.py --idn
```

## VISA 模式

设置 `NFS_SPECTRUM_BACKEND=visa` 与 `NFS_SPECTRUM_VISA_ADDRESS`。需安装 pyvisa。

## 安全查询

首次仅：`*IDN?`、`FREQ:CENT?`、Marker 幅度（不 sweep）。

## 写命令 / Sweep / Trace

| 开关 | 风险 |
|------|------|
| `NFS_ENABLE_REAL_SPECTRUM_WRITE=1` | 修改仪表配置 |
| `NFS_ENABLE_REAL_SPECTRUM_SWEEP=1` | 启动 sweep |
| `NFS_ENABLE_REAL_SPECTRUM_TRACE_READ=1` | 读取大量 trace 数据 |

默认全部关闭。

## 常见问题

| 现象 | 处理 |
|------|------|
| IP 不通 | ping 主机、检查网线 |
| 5025 端口不通 | telnet / Test-NetConnection |
| pyvisa 未安装 | `pip install pyvisa` |
| SCPI 不兼容 | 对照仪表手册调整命令 |
| Marker 不存在 | 先在仪表上启用 Marker 1 |
