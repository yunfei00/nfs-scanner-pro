# Device Error Recovery

## 场景
任一必需设备断开 mid-session。

## 动作
1. ScanTask → Paused（若 Running）
2. statusBar 摘要 + device 指示点变红（Motion/Spectrum）
3. logDock 写 DEVICE_LOST 事件
4. 工具菜单「设备管理」引导重连
5. 重连成功 → 用户选择 Resume 或 Cancel ScanTask

## 禁止
Modal 挡停止按钮。
