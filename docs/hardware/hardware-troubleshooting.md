# 硬件故障排查

## 通用

| 问题 | 排查 |
|------|------|
| 真实硬件 disabled | 检查 NFS_ENABLE_REAL_HARDWARE=1 |
| 模式不对 | 检查 NFS_HARDWARE_MODE |
| 配置未生效 | 环境变量优先于 yaml；检查 hardware.local.yaml |
| PyYAML 未安装 | 不影响默认运行；yaml 被跳过 |

## 运动平台

- COM 端口不存在 → 设备管理器确认端口
- pyserial 未安装 → `pip install pyserial`
- GRBL 无响应 → 波特率、USB 线、控制器上电
- 软限位失败 → 调整 NFS_MOTION_*_MIN/MAX

## 频谱仪

- IP 不通 → ping / 防火墙
- 5025 不通 → Test-NetConnection
- pyvisa 未安装 → socket 模式或安装 pyvisa
- Marker 无数据 → 仪表端启用 Marker

## 相机

- 未发现设备 → USB / 驱动
- 被占用 → 关闭其他程序
- cv2 缺失 → `pip install opencv-python`

## 舵机

- 端口错误 → yaml / NFS_SERVO_PORT
- 切换失败 → 先 state 再 switch

## 扫描

- fake-run 失败 → 先 dry-run / 接口审计
- real-run blocked → 检查全部 NFS_ENABLE_REAL_* 开关
- 输出路径不对 → NFS_SCANNER_RUNTIME_DIR / scan.output_dir

## 获取诊断报告

```powershell
python scripts/generate_hardware_bringup_report.py
python scripts/check_hardware_interface_inventory.py
```
