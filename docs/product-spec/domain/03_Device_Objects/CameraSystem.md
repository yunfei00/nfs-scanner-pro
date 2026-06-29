# CameraSystem — 相机

## 1. 对象定义
可选 USB 相机，用于 PCB 拍照（ADR-0003）。

## 2. 为什么需要
PCB.imagedAt；Alignment 图像源。

## 3. 关键字段
connectionState, deviceId, resolution, lastCapturePath。

## 4–5. 关系
可选；失败不阻止 ScanTask。

## 6–7. 状态
[Camera_State_Machine.md](../04_State_Machines/Camera_State_Machine.md)

## 8–9. 映射/UI
sample/images/；deviceStatusCameraIndicator（灰=idle 非 error）。

## 10. Qt
`CameraDriver` 抓拍至临时文件再 commit PCB。

## 11. 禁止
禁止相机离线示 error 红；禁止阻止扫描。

## 相关
[Camera_Error_Recovery.md](../06_Error_Recovery/Camera_Error_Recovery.md)
