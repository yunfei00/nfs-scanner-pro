# 高保真 Token 快照

> 摘自 [design-system/01_Foundation/Design_Tokens.md](../../design-system/01_Foundation/Design_Tokens.md)  
> 用于 HTML/CSS 高保真与后续 PySide6 QSS 对照

## 1. 色彩 Token

| Token | 值 | CSS 变量 |
|---|---|---|
| color.bg.app | `#07111D` | `--color-bg-app` |
| color.bg.panel | `#0B1724` | `--color-bg-panel` |
| color.bg.canvas | `#050A12` | `--color-bg-canvas` |
| color.bg.toolbar | `#0A1520` | `--color-bg-toolbar` |
| color.border.default | `#1E2D3D` | `--color-border-default` |
| color.text.primary | `#EAF2FF` | `--color-text-primary` |
| color.text.secondary | `#A8B3C2` | `--color-text-secondary` |
| color.brand.primary | `#0D6EFD` | `--color-brand-primary` |
| color.status.success | `#22C55E` | `--color-status-success` |
| color.status.error | `#EF4444` | `--color-status-error` |
| color.nav.indicator | `#0D6EFD` | `--color-nav-indicator` |

## 2. 字体 Token

| Token | 值 | CSS |
|---|---|---|
| typography.family.ui | HarmonyOS Sans SC, Microsoft YaHei UI… | `--font-family-ui` |
| typography.size.menu | 14px | `--font-size-menu` |
| typography.size.toolbar | 14px | `--font-size-toolbar` |
| typography.size.body | 13px | `--font-size-body` |
| typography.size.caption | 12px | `--font-size-caption` |
| typography.size.panel.title | 16px | `--font-size-panel-title` |

## 3. 间距 Token

| Token | 值 | CSS 变量 |
|---|---|---|
| spacing.1 | 4px | `--spacing-1` |
| spacing.2 | 8px | `--spacing-2` |
| spacing.3 | 12px | `--spacing-3` |
| spacing.4 | 16px | `--spacing-4` |
| size.menubar.height | 32px | `--size-menubar` |
| size.toolbar.height | 56px | `--size-toolbar` |
| size.nav.collapsed | 56px | `--size-nav-collapsed` |
| size.nav.expanded | 180px | `--size-nav-expanded` |
| size.dock.param.width | 340px | `--size-dock-width` |

## 4. 圆角 Token

| Token | 值 | CSS 变量 |
|---|---|---|
| radius.input | 4px | `--radius-input` |
| radius.button | 6px | `--radius-button` |
| radius.panel | 8px | `--radius-panel` |

## 5. 阴影 Token

| Token | 值 | CSS 变量 |
|---|---|---|
| shadow.dock.float | `0 4px 16px rgba(0,0,0,0.45)` | `--shadow-float` |

## 6. 状态 Token

| 语义 | 色值 |
|---|---|
| 设备已连接 | `#22C55E` |
| 扫描运行中 | `#3B82F6` |
| 错误 | `#EF4444` |
| 空闲 | `#6B7280` |

## 7. 动效 Token

| Token | 值 | CSS 变量 |
|---|---|---|
| motion.fast | 150ms | `--motion-fast` |
| motion.normal | 180ms | `--motion-normal` |
| motion.ease | cubic-bezier(0.4,0,0.2,1) | `--motion-ease` |

导航 Hover 展开使用 **motion.normal（180ms）**。

## 8. CSS 映射文件

实现见 [prototypes/high_fidelity/styles.css](../../../../prototypes/high_fidelity/styles.css) 顶部 `:root` 块。

PySide6 映射见 `design-system/06_QSS/token_mapping_qss.md`。
