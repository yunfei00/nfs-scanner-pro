# Qt ObjectName Rules — objectName 命名规则

## 设计目标

全局唯一、稳定、可 QSS 锚定，Release 010 禁止随意改名。

## 命名规则

1. **camelCase**，不以数字开头
2. 与 `02_Components` 文档一致
3. 每窗口唯一；Dock/Page 级前缀
4. 动态列表项：`fieldStepX`，不用随机 UUID

## 完整清单

```text
mainWindow
menuBar
mainToolBar
statusBar
centralWidget
leftNavigationBar
navScanButton
navDeviceButton
navAnalysisButton
navReportButton
pageStack
scanPage
devicePage
analysisPage
reportPage
deviceStatusBar
deviceStatusMotionIndicator
deviceStatusSpectrumIndicator
deviceStatusCameraIndicator
deviceStatusServoIndicator
breadcrumbBar
scanCanvasView
scanScene
scanParamDock
scanSettingsGroup
regionSettingsGroup
displaySettingsGroup
instrumentSettingsGroup
advancedSettingsGroup
logDock
spectrumDock
statisticsDock
dataTableDock
dataTableView
toolbarStartScanButton
toolbarStopScanButton
toolbarCaptureButton
toolbarAlignButton
toolbarGridButton
toolbarMeasureButton
statusBarMessageLabel
statusBarProgressBar
statusBarDateTimeLabel
dialogNewProject
dialogButtonOk
dialogButtonCancel
```

## Qt API

`widget.setObjectName("scanCanvasView")` 在 `__init__` 完成，早于 `setStyleSheet`。

## 禁止事项

- 禁止空 objectName 依赖 class 选择器 alone
- 禁止运行时改 objectName

## 相关

- `../../qt-spec/02_Qt_Object_Names.md`
