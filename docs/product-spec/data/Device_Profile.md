# Device Profile

## 定义

Device Profile 是系统级可复用的设备配置。

它不属于某一个 Project，而是属于软件系统。

## 职责

Device Profile 用于让用户快速复用常用设备设置。

例如：

- 默认运动控制器
- 默认频谱仪
- 默认相机
- 默认探头舵机

## 设备类型

必需设备：

- Motion Controller
- Spectrum Analyzer

可选设备：

- Camera
- Probe Servo

## 规则

- 新建 Project 时可以选择一个 Device Profile。
- Project 保存的是 Device Snapshot，不直接保存 Device Profile。
- 修改 Device Profile 不应自动修改历史 Project。
- Device Profile 可以被多个 Project 使用。

## 典型内容

Motion Profile：

- 控制器类型
- 串口号
- 波特率
- 坐标范围
- 默认速度

Spectrum Profile：

- 设备类型
- 连接方式
- 地址
- 默认频率设置

Camera Profile：

- 相机类型
- 相机编号或地址
- 默认分辨率

Probe Servo Profile：

- Hx 位置
- Hy 位置
- Hx 偏移
- Hy 偏移

## 生命周期

- Created
- Tested
- Default
- Deprecated
