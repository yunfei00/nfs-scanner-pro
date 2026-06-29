# HxHyCalibration — Hx/Hy 探头校准

## 1. 对象定义
Hx 与 Hy 探头之间的 **位置偏移与切换参数**，供 Hy 扫描前补偿。

## 2. 为什么需要
整区 Hx 完成后切 Hy 需物理 offset（工具菜单「Hx/Hy 校准」）。

## 3. 关键字段
offsetX, offsetY, offsetZ, rotation, calibratedAt, calibratedBy, valid。

## 4. 所属关系
属于 Project 或 System（V1 Project 级）。

## 5. 与其它对象关系
Probe(Hy) 应用 offset；ServoSystem 执行切换。

## 6. 生命周期
Uncalibrated → Calibrated → Stale（硬件变更后）。

## 7. 状态
valid 布尔 + 时间戳。

## 8. 文件系统映射
`{project}/devices/hxhy_calibration.json`

## 9. UI 映射
工具 → Hx/Hy 校准 Dialog。

## 10. Qt/PySide6 实现建议
校准 wizard 写入 JSON；ScanTask 启动 Hy 前校验 valid。

## 11. 禁止事项
禁止无校准提示仍静默 Hy 扫描（可 warning 继续）。

## 相关
[ADR-0004](../../decision/ADR-0004-HxHy_Strategy.md)
