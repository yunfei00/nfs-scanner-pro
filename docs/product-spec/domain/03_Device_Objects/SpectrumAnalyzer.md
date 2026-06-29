# SpectrumAnalyzer — 频谱仪

## 1. 对象定义
运行期频谱仪抽象（SCPI），采集 FrequencyData。

## 2. 为什么需要
ScanTask 每点场强读数；**扫描必需设备**。

## 3. 关键字段
connectionState, address, centerFreq, span, rbw, activeTrace。

## 4–5. 关系
DeviceProfile/Snapshot；ScanTask 依赖就绪。

## 6–7. 状态
[Spectrum_State_Machine.md](../04_State_Machines/Spectrum_State_Machine.md)

## 8. 映射
Snapshot 内 spectrum 段。

## 9. UI
deviceStatusSpectrumIndicator；instrumentSettingsGroup。

## 10. Qt
`SpectrumDriver` SCPI 会话。

## 11. 禁止
禁止 Spectrum 离线开始 ScanTask。

## 相关
[Spectrum_Error_Recovery.md](../06_Error_Recovery/Spectrum_Error_Recovery.md)
