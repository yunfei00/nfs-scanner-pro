# Probe — 探头通道

## 1. 对象定义
表示 **Hx 或 Hy** 探头采样方向，非物理探头 SN 独立对象（V1）。

## 2. 为什么需要
ADR-0004 整区 Hx 后整区 Hy；Breadcrumb、ScanTask 通道标识。

## 3. 关键字段
channel: Hx | Hy；offsetX, offsetY, offsetZ（Hy 相对 Hx 补偿）。

## 4. 所属关系
每条 ScanTask 绑定一个 Probe 实例。

## 5. 与其它对象关系
关联 HxHyCalibration；ServoSystem 切换硬件位置。

## 6. 生命周期
随 ScanTask 创建而确定，不单独归档。

## 7. 状态
当前通道为 UI 会话 + ScanTask 持久字段。

## 8. 文件系统映射
记录在 scan.json `probeChannel`；校准在 `{project}/devices/hxhy_calibration.json`。

## 9. UI 映射
`fieldProbeChannel`、Breadcrumb `Hx Probe`。

## 10. Qt/PySide6 实现建议
enum ProbeChannel；切换发 domain event probeChannelChanged。

## 11. 禁止事项
禁止 V1 每 ScanPoint 切换通道。

## 相关
[HxHyCalibration.md](HxHyCalibration.md)
