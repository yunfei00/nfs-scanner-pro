# MotionSystem — 运动平台

## 1. 对象定义
运行期 **运动控制器**抽象（GRBL 等），非持久化根实体。

## 2. 为什么需要
ScanTask 路径执行、起点/终点记录、回零。

## 3. 关键字段
connectionState, port, baud, position{x,y,z}, isHomed, limits, feedRate。

## 4. 所属关系
配置来自 DeviceProfile；快照写入 DeviceSnapshot。

## 5. 与其它对象关系
ScanPoint 坐标来源；Motion 未就绪则 ScanTask 不可 Running。

## 6–7. 生命周期/状态
[Motion_State_Machine.md](../04_State_Machines/Motion_State_Machine.md)

## 8. 文件系统映射
仅 DeviceSnapshot JSON，无独立目录。

## 9. UI 映射
deviceStatusMotionIndicator；设备页。

## 10. Qt/PySide6 实现建议
`MotionDriver` 接口；异步 moveTo。

## 11. 禁止事项
禁止 Motion 断开仍 Running ScanTask 无 pause。

## 相关
[Motion_Error_Recovery.md](../06_Error_Recovery/Motion_Error_Recovery.md)
