# Release 040 — Real Spectrum Single Point Amplitude Read

## 1. Release 目标

在 Release_039 安全连接与基础 SCPI 查询基础上，增加**真实频谱仪 Marker 单点幅度读取**，返回 amplitude / frequency / trace / unit，不修改仪表配置、不启动 sweep、不读取完整 Trace 数组。

## 2. 为什么先做单点幅度读取

扫描链路最终需要幅度数据，但一次性读取完整 Trace 数据量大且风险高。先读取仪表已有 Marker 的单点幅度，可验证 SCPI 读通路与数据解析，而不触发 sweep 或配置变更。

## 3. NFS_ENABLE_REAL_HARDWARE

统一安全开关。未设置时不连接 socket/VISA、不读取幅度。

## 4. NFS_SPECTRUM_BACKEND / HOST / PORT / VISA_ADDRESS

与 Release_039 相同：

| 变量 | 默认 |
|------|------|
| `NFS_SPECTRUM_BACKEND` | `socket` |
| `NFS_SPECTRUM_HOST` | `192.168.1.100` |
| `NFS_SPECTRUM_PORT` | `5025` |
| `NFS_SPECTRUM_VISA_ADDRESS` | `TCPIP0::192.168.1.100::inst0::INSTR` |

## 5. SpectrumScpiAdapter 单点读取接口

| 方法 | 说明 |
|------|------|
| `read_marker_amplitude()` | 查询已有 Marker 幅度（及可选频率） |
| `read_single_point_amplitude()` | 连接 → IDN → 频率 → Marker → 断开 |
| `parse_amplitude_response(raw)` | 解析 `-23.45` 等幅度字符串 |
| `parse_marker_response(raw)` | 解析 Marker 复合响应 |
| `safe_single_point_snapshot()` | 安全单点快照入口 |

## 6. 允许的 Marker 查询命令

- `CALC:MARK1:Y?` / `CALC:MARK:Y?` / `CALC:MARKER1:Y?` / `CALC:MARKER:Y?`
- `CALC:MARK1:X?` / `CALC:MARK:X?` / `CALC:MARKER1:X?` / `CALC:MARKER:X?`

**不发送** `CALC:MARK:STAT ON` 等 Marker 启用命令。

## 7. 禁止的 SCPI 命令

- `INIT` / `SING` / sweep / 校准
- `CALC:DATA?` / `TRAC:DATA?` / 完整 Trace 读取
- 频率/带宽/功率设置写命令

## 8. check_spectrum_single_point_safe.py 用法

**默认（不连接）：**
```bash
python scripts/check_spectrum_single_point_safe.py
```

**手动探测（PowerShell）：**
```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_SPECTRUM_BACKEND="socket"
$env:NFS_SPECTRUM_HOST="192.168.1.100"
$env:NFS_SPECTRUM_PORT="5025"
python scripts/check_spectrum_single_point_safe.py
```

## 9. check_real_devices_safe.py

启用后除 Release_039 项外，还输出：

- Spectrum single point amplitude: PASS / FAIL
- amplitude_dbm
- marker raw

## 10. 本地验收

```bash
python scripts/verify_release_040.py
python scripts/verify_all.py --only 040
python scripts/verify_all.py --from 039
```

## 11. 后续 Release_041 建议

**运动平台当前位置 + 频谱仪单点幅度联合采样** — 在用户显式开启双重硬件开关后，同步读取 motion 位置与 spectrum 单点幅度，仍不启动真实扫描路径。
