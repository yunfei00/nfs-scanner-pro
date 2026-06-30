# Release 017 — Workspace Persistence Mock

## 1. Release 目标

在 **Release 016 项目 Mock** 与四页主窗口基础上，实现**工作区状态 Mock 持久化**：启动时自动恢复上次页面、导航折叠、Dock 显示、窗口尺寸与当前项目；关闭时写入本地 JSON。

## 2. 为什么需要 Workspace Persistence

- Mock UI 需要验证「关闭再打开」的连续体验，而非每次回到默认扫描页。
- 项目、页面、布局属于**工作区上下文**，与 Project 文件夹域模型分离。
- 持久化仅保存 Mock 元数据，为后续真实工作区恢复打样。

## 3. 本次实现范围

- `app_paths.py`：`runtime/` 目录与 JSON 路径
- `workspace_state_mock.py`：加载 / 保存 / 重置 / 增量更新 API
- 启动恢复：项目、Breadcrumb、最近项目菜单、页面、导航、Dock、窗口
- 关闭保存：完整 snapshot 写入 `runtime/workspace_state_mock.json`
- 文件菜单项目操作后同步保存 workspace
- 设置菜单：**重置工作区状态**
- `.gitignore`：`runtime/*.json` 不提交 Git

## 4. 本次不做什么

- ❌ 不存真实设备 / 扫描 / 报告数据
- ❌ 不读取真实项目文件夹内容
- ❌ 不把「项目」加入左侧导航
- ❌ 不修改四页结构与扫描画布
- ❌ 不接真实硬件

## 5. 状态文件位置

```text
runtime/workspace_state_mock.json
```

目录不存在时自动创建。JSON 损坏或读取失败时回退 `DEFAULT_WORKSPACE_STATE`，状态栏提示恢复失败。

## 6. 输入规范

- Release 016：[Release_016_Project_File_System_Mock/README.md](../Release_016_Project_File_System_Mock/README.md)
- ADR-0018：[decision/ADR-0018-Project-As-Folder-Domain.md](../../decision/ADR-0018-Project-As-Folder-Domain.md)
- Project 对象：[domain/02_Core_Objects/Project.md](../../domain/02_Core_Objects/Project.md)

## 7. 输出文件

```text
src/nfs_scanner_pro/app_paths.py
src/nfs_scanner_pro/workspace_state_mock.py
src/nfs_scanner_pro/project_mock.py
src/nfs_scanner_pro/ui/main_window.py
src/nfs_scanner_pro/ui/navigation_bar.py
.gitignore
docs/product-spec/release/Release_017_Workspace_Persistence_Mock/README.md
```

## 8. 运行方式

```bash
pip install PySide6
python scripts/run_mock_ui.py
```

1. 切换到分析页 / 展开左侧导航 / 隐藏右侧 Dock  
2. 关闭应用  
3. 再次启动 — 应恢复上述状态  
4. 检查 `runtime/workspace_state_mock.json` 已生成  

## 9. 验收标准

- [ ] 启动读取 workspace state
- [ ] 页面 / 导航 / Dock / 窗口状态可恢复
- [ ] 项目 Mock 与最近项目菜单同步保存
- [ ] JSON 损坏不崩溃
- [ ] `runtime/*.json` 不在 Git 中
- [ ] 左侧导航仍无「项目」
- [ ] `python -m compileall src` 通过

## 10. 后续 Release_018 建议

- **日志 / 频谱 / 统计 Dock Mock**
- **扫描→分析→报告联动**（扫描完成 Mock 报告草稿）
- **工作区状态版本号**与迁移（schema v2）

## 强调

- 这是 **Mock 持久化**，只写 workspace 元数据。
- **Project 仍然不是左侧导航一级页面**。
- 复制项目文件夹仍是备份主路径；Import/Export Project 不是主路径。
