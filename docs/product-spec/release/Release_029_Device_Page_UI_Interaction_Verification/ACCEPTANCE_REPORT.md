# Release_029 验收报告

## 执行时间

2026-07-01 23:49:05 UTC

## 执行命令

```bash
python scripts/verify_release_029.py
python scripts/verify_all.py
```

## 检查项

- [PASS] `compileall`
- [PASS] `mainwindow_boot` — docks=1
- [PASS] `device_navigation` — dock='设备配置' status='状态：设备就绪'
- [PASS] `device_config_dock` — groups=['DeviceProfile', '连接策略', '安全限制', '高级']
- [PASS] `device_manager_mock` — ready=True keys=['timestamp', 'motion', 'spectrum', 'camera', 'servo']
- [PASS] `device_status_bar` — ● 运动平台(COM6) ● 频谱仪(ZNA67) ● 相机(USB3.0) ● 舵机系统
- [PASS] `motion_card_ui` — card=deviceCardMotion
- [PASS] `motion_actions` — pos=(45.20,-28.30,5.00) jogs=[True, True, True, True, True, True]
- [PASS] `spectrum_card_ui` — deviceCardSpectrum
- [PASS] `spectrum_actions` — 状态：Mock：频谱仪连接测试成功; 状态：Mock：单次 Sweep 完成; 状态：Mock：Trace 1 @ 2.450 GHz（1 MHz — 67 GHz）
- [PASS] `camera_card_ui` — deviceCardCamera
- [PASS] `camera_actions` — 状态：Mock：相机拍照完成; 状态：Mock：相机预览已刷新; 状态：Mock：打开相机设置
- [PASS] `servo_card_ui` — deviceCardServo
- [PASS] `servo_actions` — probe=Hy status='状态：Mock：偏移补偿已应用'
- [PASS] `page_switch_regression` — 0:'扫描参数', 1:'设备配置', 2:'分析参数', 3:'报告设置', 1:'设备配置'
- [PASS] `no_real_device_access`

## 结果

PASS

## 是否接真实设备

否

## 是否打开串口

否

## 是否发送 SCPI

否

## 是否访问真实相机

否

## 是否控制真实舵机

否

## 是否修改 high_fidelity HTML

否

## 是否可以提交

是
