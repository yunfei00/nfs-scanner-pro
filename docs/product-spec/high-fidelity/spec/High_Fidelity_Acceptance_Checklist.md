# 高保真验收清单 — Release 010 候选定稿

Release 010 High Fidelity Design Package · **候选定稿版（v2.1 Final Candidate）**

> 交互原型：[prototypes/high_fidelity/index.html](../../../../prototypes/high_fidelity/index.html)

## 检查项

| # | 检查项 | 通过标准 | 结果 |
|---|---|---|---|
| 1 | 全部简体中文 | 菜单/工具栏/导航/Dock/状态栏无英文主文案 | ✅ |
| 2 | 无左侧「项目」 | 导航仅扫描/设备/分析/报告 | ✅ |
| 3 | 项目仅在文件菜单 | 工具栏无新建/打开/保存/项目管理器 | ✅ |
| 4 | 导航默认图标模式 | 宽 **64px** | ✅ |
| 5 | 导航 Hover 展开 | **180px**，~180ms | ✅ |
| 6 | 设备状态栏单行 | 不换行 | ✅ |
| 7 | **PCB 占据视觉中心** | 深绿 PCB 占主区域 ≥75%；尺寸未缩小 | ✅ |
| 8 | 热力图专业清晰 | 中心红→外圈蓝绿 **radial** 整层 | ✅ |
| 9 | 右侧参数 Dock | **360px**，表单/统计卡片 | ✅ |
| 10 | Dock 底部可访问 | 内容不被状态栏遮挡；Dock **内部独立滚动** | ✅ |
| 11 | 色带可见 | 幅度(dBm) -10…-90 | ✅ |
| 12 | **无浏览器滚动条** | `body`/`html` `overflow: hidden`；仅整体 scale | ✅ |
| 13 | **字体可读性** | 菜单 16px；Dock 标签 **+1px**（14~16px） | ✅ |
| 14 | 无页面内异常 X 元素 | 无顶部中央灰色 X（浏览器预览浮层除外） | ✅ |
| 15 | 日志/频谱/统计隐藏 | 主屏无辅助 Dock | ✅ |
| 16 | 无外部依赖 | 无 CDN/外链图 | ✅ |
| 17 | 工具栏与状态栏 | 主/危险按钮清晰；进度条 10px | ✅ |
| 18 | 可作 PySide6 参考 | 与 wireframe + design-system 一致 | ✅ |

## 验证步骤

1. 全屏打开 `prototypes/high_fidelity/index.html`
2. 确认 **无浏览器纵向/横向滚动条**
3. 确认右侧 Dock 折叠区可滚动到底，不被底部状态栏遮挡
4. 确认 PCB、热力图、色带、工具栏结构未变

## Release 010 候选定稿结论

**18/18 通过** — 本清单版本标记为 **Release 010 候选定稿**，可提交 Release 010。

## Release 011 门禁

候选定稿 Accepted 后，可进入 **Release 011 MainWindow Prototype（PySide6）**。
