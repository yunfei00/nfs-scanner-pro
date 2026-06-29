# Spectrum State Machine — 频谱子系统状态机

## 1. 状态列表
Disconnected | Connecting | Ready | Measuring | Error

## 2–3. 转换
Ready + scanStart → Measuring → Ready；SCPI 失败 → Error。

## 4–5. 允许/禁止
ScanTask 必需 Ready。禁止 Measuring 时改 centerFreq（锁定）。

## 6. UI
deviceStatusSpectrumIndicator；spectrumDock。

## 7. 日志
SCPI 命令与错误码

## 8. 错误恢复
[Spectrum_Error_Recovery.md](../06_Error_Recovery/Spectrum_Error_Recovery.md)
