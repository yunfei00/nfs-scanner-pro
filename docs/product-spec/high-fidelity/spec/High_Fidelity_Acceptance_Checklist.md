# 高保真验收清单

Release 010 High Fidelity Design Package

## 检查项

| # | 检查项 | 通过标准 | 结果 |
|---|---|---|---|
| 1 | 全部简体中文 | 菜单/工具栏/导航/Dock/状态栏无英文主文案 | ✅ |
| 2 | 无左侧「项目」 | 导航仅扫描/设备/分析/报告 | ✅ |
| 3 | 项目仅在文件菜单 | 工具栏无新建/打开/保存项目 | ✅ |
| 4 | 导航默认图标模式 | 宽 56px | ✅ |
| 5 | 导航 Hover 展开 | 180px，~180ms | ✅ |
| 6 | 设备状态栏单行 | 不换行溢出 | ✅ |
| 7 | PCB 最大视觉区域 | 画布 ≥70% 主内容宽 | ✅ |
| 8 | 右侧参数 Dock | 340px，标题「扫描参数」 | ✅ |
| 9 | 日志/频谱/统计默认隐藏 | 主屏无底部辅助 Dock | ✅ |
| 10 | 热力图整层叠加 | gradient 单层，非逐格 | ✅ |
| 11 | 无真实业务代码 | 无 PySide6/设备/扫描线程 | ✅ |
| 12 | 浏览器可打开 | `prototypes/high_fidelity/index.html` | ✅ |
| 13 | 可作 PySide6 参考 | 与 wireframe + design-system 一致 | ✅ |

## 验证步骤

1. 浏览器打开 `prototypes/high_fidelity/index.html`
2. 打开 `docs/product-spec/high-fidelity/assets/main_window_high_fidelity.svg`
3. 对照 [01_Main_Window_High_Fidelity_Spec.md](../main-window/01_Main_Window_High_Fidelity_Spec.md)
4. 运行 `python scripts/check_spec_registry_paths.py`（Registry 更新后）

## Release 011 门禁

全部 13 项勾选后，可进入 **Release 011 MainWindow Prototype（PySide6）**。
