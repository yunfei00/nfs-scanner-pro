# Device Status Pattern — 设备状态模式

## 设计目标

40px 横条一眼看清四设备 + 扫描上下文五字段。

## 使用场景

Central 顶栏，全页共享。

## 规则

运动/频谱必需绿/蓝才允许开始扫描；相机灰不影响；点击设备名 → 设备页。

## 组件

StatusBar 设备段 + State_Tokens。

## 禁止事项

- 禁止相机红点 error
- 禁止多行设备栏

## 相关

- `../../ui-wireframe/04_Device_Status_Bar.md`
- `../02_Components/StatusBar.md`
