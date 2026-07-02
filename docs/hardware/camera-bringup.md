# 相机联调清单

## 接口说明

`CameraAdapter`：enumerate_devices / connect / capture_image / snapshot。

## 后端

- **fake**：FakeTransport，不打开真实相机
- **opencv (cv2)**：需 `NFS_ENABLE_REAL_CAMERA=1`

## 枚举设备

```powershell
$env:NFS_ENABLE_REAL_HARDWARE="1"
$env:NFS_ENABLE_REAL_CAMERA="1"
python scripts/debug_real_camera.py --list
```

Fake 模式：

```powershell
python scripts/debug_real_camera.py --list --fake
```

## 拍照保存

需 `NFS_ENABLE_REAL_CAMERA=1`，输出目录 `NFS_CAMERA_OUTPUT_DIR` 或 yaml `camera.output_dir`。

## 常见问题

| 现象 | 处理 |
|------|------|
| 未发现设备 | 检查 USB、驱动 |
| 相机被占用 | 关闭其他采集软件 |
| cv2 未安装 | `pip install opencv-python` |
