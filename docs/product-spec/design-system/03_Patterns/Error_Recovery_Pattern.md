# Error Recovery Pattern — 错误恢复模式

## 设计目标

设备断开、扫描失败可理解、可恢复，不丢 PCB 画布上下文。

## 使用场景

频谱断开 mid-scan、运动报警、保存失败。

## 规则

1. statusBar 单行错误摘要 + 设备栏红点
2. 扫描自动 pause，停止按钮仍可达
3. 非阻塞 Toast 可选（V2）；V1 用 statusBar + logDock
4. 相机失败不阻塞扫描（ADR-0003）
5. 项目保存失败 Dialog，不关闭画布

## 组件

StatusBar、Dialog、logDock、Scan_State_Interaction。

## 禁止事项

- 禁止 modal 挡急停
- 禁止 silently fail

## 相关

- `../04_Interaction/Scan_State_Interaction.md`
