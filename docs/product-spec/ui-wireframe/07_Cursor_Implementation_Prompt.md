# Cursor / AI 编程实现提示词

请按照 docs/product-spec/ui-wireframe 与 docs/product-spec/design-system 中的规范，实现 NFS Scanner Pro 的 PySide6 主窗口框架。

要求：

1. 使用 QMainWindow。
2. 顶部使用 QMenuBar + QToolBar。
3. 左侧导航默认 56px 图标模式，鼠标悬停展开到 180px。
4. 中间使用 QGraphicsView 作为 PCB 主画布。
5. 右侧扫描参数使用 QDockWidget，默认宽度 340px。
6. 日志、频谱、统计使用 QDockWidget，默认隐藏，通过“视图”菜单打开。
7. 项目相关功能只放到“文件”菜单，不放左侧导航。
8. 全部界面文字使用简体中文。
9. 先实现 mock UI，不接真实设备。
10. 所有 objectName 按 docs/product-spec/qt-spec/02_Qt_Object_Names.md 统一命名。
