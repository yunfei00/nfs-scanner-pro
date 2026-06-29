# Dark Theme Tokens（QSS 令牌文档）

> **历史兼容**：已迁移到 `01_Foundation/Design_Tokens.md` 与 `06_QSS/token_mapping_qss.md`，保留用于历史兼容。

> 本文档定义深色主题令牌。Release 010 实现时将令牌展开为实际 QSS 属性值。  
> QSS 不支持原生 CSS 变量，以下为**命名约定**。

## 使用方式

Release 010 可选方案：

1. Python 字典 `TOKENS = {"color-primary": "#0D6EFD", ...}` 格式化 QSS 模板
2. 构建脚本将 `@color-primary@` 替换为 hex
3. 注释块人工对照维护

---

## 颜色令牌

```css
/* === Background === */
--color-bg-deep:          #07111D;   /* 菜单栏、表头 */
--color-bg-panel:         #0B1724;   /* 面板、Dock 内容 */
--color-canvas-bg:        #050A12;   /* 画布背景 */
--color-toolbar-bg:       #0A1520;   /* 工具栏 */
--color-nav-bg:           #0B1724;   /* 左侧导航 */
--color-dock-title-bg:    #0B1724;   /* Dock 标题栏 */
--color-input-bg:         #0B1724;   /* 输入框 */

/* === Border & Divider === */
--color-border:           #1E2D3D;
--color-divider:          #1E2D3D;

/* === Text === */
--color-text-primary:     #EAF2FF;
--color-text-secondary:   #A8B3C2;

/* === Brand & Primary === */
--color-primary:          #0D6EFD;
--color-primary-hover:    #0B5ED7;
--color-primary-pressed:  #0A58CA;
--color-primary-disabled: #0D6EFD40;

/* === Status === */
--color-status-ok:        #22C55E;
--color-status-running:   #3B82F6;
--color-status-warning:   #FACC15;
--color-status-error:     #EF4444;
--color-status-idle:      #6B7280;

/* === Interactive === */
--color-nav-hover:        #1E2D3D80;
--color-nav-selected:     #0D6EFD26;
--color-input-focus:      #0D6EFD;
--color-table-stripe:     #0F1A28;
--color-table-selected:   #0D6EFD33;
```

## 尺寸令牌

```css
/* === Layout heights === */
--height-menubar:         32px;
--height-toolbar:         56px;
--height-device-status:   40px;
--height-statusbar:       32px;
--height-nav-item:        48px;
--height-input:           32px;
--height-button:          36px;
--height-dock-title:      32px;
--height-table-row:       32px;

/* === Layout widths === */
--width-nav-collapsed:    56px;
--width-nav-expanded:     180px;
--width-dock-param:       340px;
--width-dock-collapsed:   40px;

/* === Radius === */
--radius-input:           4px;
--radius-button:          6px;
--radius-dialog:          8px;

/* === Spacing === */
--space-1:                4px;
--space-2:                8px;
--space-3:                12px;
--space-4:                16px;
--space-5:                24px;
--space-6:                32px;
```

## 字体令牌

```css
--font-family-ui:         "HarmonyOS Sans SC", "Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
--font-family-mono:       "Consolas", "Cascadia Mono", "Microsoft YaHei UI", monospace;
--font-size-menu:         14px;
--font-size-toolbar:      14px;
--font-size-body:         13px;
--font-size-caption:      12px;
--font-size-panel-title:  16px;
```

## 热力图

```css
--heatmap-overlay-opacity: 0.7;
--heatmap-lut-default:     turbo;
```

## 全局 QWidget 示例片段（展开后）

```css
QWidget {
    background-color: #07111D;
    color: #EAF2FF;
    font-family: "HarmonyOS Sans SC", "Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
    font-size: 13px;
}
```

## 禁止事项

- 禁止令牌表外新增颜色不经 `01_Color_System.md` 评审。
- 禁止浅色令牌与深色混用为默认。
- 禁止在令牌文件写 PySide6 加载代码（本文档仅规范）。

## 相关文档

- `01_Color_System.md`
- `15_QSS_Guide.md`
