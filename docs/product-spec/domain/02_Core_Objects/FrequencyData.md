# FrequencyData — 频谱数据

## 1. 对象定义
某 ScanPoint 或某 Trace 上的 **频域读数**（频谱仪结果）。

## 2. 为什么需要
频谱 Dock、Analysis 频点视图、报告迹线。

## 3. 关键字段
centerFrequency, span, rbw, vbw, traceData[], peakValue, timestamp。

## 4. 所属关系
属于 ScanTask（关联 ScanPoint）。

## 5. 与其它对象关系
Analysis 可选频点；Heatmap 由标量场强派生。

## 6. 生命周期
随 ScanPoint Acquired 写入。

## 7. 状态
raw / validated。

## 8. 文件系统映射
`raw/spectrum/{pointIndex}.json`

## 9. UI 映射
spectrumDock 曲线。

## 10. Qt/PySide6 实现建议
Mock 阶段简化数组；真实 SCPI 异步读。

## 11. 禁止事项
禁止修改已锁定 ScanTask 的 frequency raw。

## 相关
[SpectrumAnalyzer.md](../03_Device_Objects/SpectrumAnalyzer.md)
