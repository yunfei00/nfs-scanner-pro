# Parameter Dock Pattern — 参数 Dock 模式

## 设计目标

右侧 340px Accordion 承载全部扫描/区域/仪表参数。

## 使用场景

scanParamDock 默认 visible；auto-hide 可选。

## 规则

五组 Accordion；扫描中锁定区域范围与步进；视图菜单可隐藏面板。

## 组件

DockPanel + PropertyPanel + Input/ComboBox。

## 禁止事项

- 禁止参数散落到多个永久 Dock

## 相关

- `../02_Components/PropertyPanel.md`
