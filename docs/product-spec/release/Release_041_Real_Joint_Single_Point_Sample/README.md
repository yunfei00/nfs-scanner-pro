# Release 041 — Real Joint Single Point Sample

## 1. Release 目标

将**运动平台当前位置读取**与**频谱仪 Marker 单点幅度读取**合并为一次真实联合采样，生成 JSON / CSV 单点样本，不运动、不 sweep、不改仪表配置。

## 2. 为什么要先做联合单点采样

扫描链路需要“位置 + 幅度”成对数据。先在不动平台、不扫频的前提下验证联合读取与样本落盘，可降低误触发风险。

## 3. NFS_ENABLE_REAL_HARDWARE

统一安全开关。未设置时不连接串口/socket/VISA，不生成真实采样记录。

## 4. 运动平台当前位置读取

通过 `MotionGrblAdapter.refresh_position()` 读取 MPos/WPos，**不发送 jog / move / home**。

## 5. 频谱仪单点幅度读取

通过 `SpectrumScpiAdapter.read_marker_amplitude()` 读取已有 Marker 幅度，**不启动 sweep、不读完整 Trace**。

## 6. JointSampleAdapter 接口

| 方法 | 说明 |
|------|------|
| `sample_once_safe(save=False)` | 联合采样主入口 |
| `build_sample_record()` | 构造样本记录 |
| `save_sample_json()` / `save_sample_csv()` | 持久化 |
| `snapshot()` | 最近样本状态 |

## 7. check_joint_single_point_sample_safe.py 用法

**默认（不连接）：**
```bash
python scripts/check_joint_single_point_sample_safe.py
```

**手动联合采样（PowerShell）：**
```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_MOTION_PORT="COM6"
$env:NFS_SPECTRUM_BACKEND="socket"
$env:NFS_SPECTRUM_HOST="192.168.1.100"
$env:NFS_SPECTRUM_PORT="5025"
python scripts/check_joint_single_point_sample_safe.py --save
```

## 8. --save / --no-save

- 默认不保存（`--save` 未指定）
- `--save` 写入 JSON / CSV
- `--no-save` 只读取打印

## 9. JSON 输出格式

`runtime/verification/R041/joint_samples/{sample_id}/single_point_sample.json`

含 `sample_id`、`position`、`spectrum`、`motion_command_executed: false`、`sweep_started: false`。

## 10. CSV 输出格式

同目录 `single_point_sample.csv`，表头 + 一行数据。

## 11. 本次禁止行为

- 自动扫描 / 路径运动 / jog / home
- sweep / 改频率带宽功率
- 完整 Trace 数组读取

## 12. 本地验收

```bash
python scripts/verify_release_041.py
python scripts/verify_all.py --only 041
```

## 13. 后续 Release_042 建议

**真实小区域 3×3 手动扫描预演** — 用户显式确认后逐点移动并采样，仍不自动连续运动。
