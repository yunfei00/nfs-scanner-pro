# 06 Dock 系统规范

## Dock 类型

| Dock | 默认状态 | 位置 |
|---|---|---|
| 扫描参数 | 显示 | 右侧 |
| 日志信息 | 隐藏 | 底部 |
| 频谱仪 | 隐藏 | 底部 |
| 扫描统计 | 隐藏 | 底部 |
| 数据表格 | 隐藏 | 底部 |
| 色带 | 可选 | 画布右侧 |
| 小地图 | 显示 | 画布右下 |

## 行为

支持固定、自动隐藏、关闭、拖动停靠、恢复默认布局。

## Qt 实现

使用 QMainWindow + QDockWidget + QGraphicsView + QToolBar + QStatusBar + QMenuBar。
