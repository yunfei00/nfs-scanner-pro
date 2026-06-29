# DeviceProfile — 设备配置模板

## 1. 对象定义
系统级可复用设备连接与默认参数模板（ADR-0006）。

## 2. 为什么需要
新建 Project 快速套用实验室标准设备组合。

## 3. 关键字段
profileId, name, motionConfig, spectrumConfig, cameraConfig, servoConfig, isDefault。

## 4. 所属关系
属于 System，**不被 Project 拥有**。

## 5. 与其它对象关系
Project 创建时**引用** → 生成 DeviceSnapshot；修改 Profile 不影响历史 Snapshot。

## 6. 生命周期
Created → Tested → Default → Deprecated。

## 7. 状态
配置有效性（非运行连接态）。

## 8. 文件系统映射
`{appData}/device_profiles/{profileId}.json`

## 9. UI 映射
设置 → 设备 Profile；新建项目 Dialog 选择。

## 10. Qt/PySide6 实现建议
Profile 只读加载；编辑在 Settings 页。

## 11. 禁止事项
禁止 Project 直接持久化 Profile 指针替代 Snapshot。

## 相关
[../../data/Device_Profile.md](../../data/Device_Profile.md)
