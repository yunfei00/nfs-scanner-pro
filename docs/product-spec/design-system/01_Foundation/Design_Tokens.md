# Design Tokens — 设计令牌总表

> Release 009.5 · 全产品 Design Token 唯一数值来源

## 1. Token 命名规则

### 1.1 格式

```text
{category}.{group}.{name}[.{variant}]
```

- 全小写，点分分隔
- 类别 `category`：`color` | `typography` | `spacing` | `radius` | `shadow` | `state` | `motion` | `z` | `size` | `opacity`
- 禁止在 Token 名中包含 `#` 或 `px`（值中携带单位）

### 1.2 示例

```text
color.bg.app
color.text.primary
spacing.2
motion.normal
z.tooltip
```

### 1.3 别名（历史兼容）

Release 009 使用的 `--color-primary` 等与点分 Token 一一对应，见各分册及 `06_QSS/token_mapping_qss.md`。

---

## 2. Color Token

```text
color.bg.app              = #07111D
color.bg.panel            = #0B1724
color.bg.canvas           = #050A12
color.bg.toolbar          = #0A1520
color.bg.input            = #0B1724
color.bg.table.stripe     = #0F1A28

color.border.default      = #1E2D3D
color.border.focus        = #0D6EFD
color.border.divider      = #1E2D3D

color.text.primary        = #EAF2FF
color.text.secondary      = #A8B3C2
color.text.disabled       = #6B7280
color.text.inverse        = #FFFFFF

color.brand.primary       = #0D6EFD
color.brand.primary.hover = #0B5ED7
color.brand.primary.press = #0A58CA
color.brand.primary.disabled = #0D6EFD40

color.status.success      = #22C55E
color.status.running      = #3B82F6
color.status.warning      = #FACC15
color.status.error        = #EF4444
color.status.idle         = #6B7280

color.nav.bg              = #0B1724
color.nav.hover           = #1E2D3D80
color.nav.selected        = #0D6EFD26
color.nav.indicator       = #0D6EFD

color.dock.title.bg       = #0B1724
color.table.selected      = #0D6EFD33

color.heatmap.lut         = turbo
opacity.heatmap.overlay   = 0.7
```

---

## 3. Typography Token

```text
typography.family.ui        = "HarmonyOS Sans SC", "Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif
typography.family.mono      = "Consolas", "Cascadia Mono", "Microsoft YaHei UI", monospace

typography.size.menu        = 14px
typography.size.toolbar     = 14px
typography.size.body        = 13px
typography.size.caption     = 12px
typography.size.panel.title = 16px

typography.weight.regular     = 400
typography.weight.medium      = 500
typography.weight.semibold    = 600

typography.lineheight.body    = 20px
typography.lineheight.tight   = 18px
```

---

## 4. Spacing Token

```text
spacing.1  = 4px
spacing.2  = 8px
spacing.3  = 12px
spacing.4  = 16px
spacing.5  = 24px
spacing.6  = 32px

size.window.base.width      = 1920px
size.window.base.height     = 1080px
size.menubar.height         = 32px
size.toolbar.height         = 56px
size.deviceStatus.height    = 40px
size.statusbar.height       = 32px
size.nav.collapsed          = 56px
size.nav.expanded           = 180px
size.nav.item.height        = 48px
size.dock.param.width       = 340px
size.dock.collapsed         = 40px
size.input.height           = 32px
size.button.height          = 36px
size.dock.title.height      = 32px
size.table.row              = 32px
size.canvas.minWidthPercent = 70
```

---

## 5. Radius Token

```text
radius.input    = 4px
radius.button   = 6px
radius.panel    = 8px
radius.dialog   = 8px
radius.tooltip  = 4px
radius.nav.item = 4px
```

---

## 6. Shadow Token

深色主题阴影极轻，避免 Material 大阴影。

```text
shadow.none     = none
shadow.panel    = 0 2px 8px rgba(0, 0, 0, 0.35)
shadow.dock.float = 0 4px 16px rgba(0, 0, 0, 0.45)
shadow.tooltip  = 0 2px 6px rgba(0, 0, 0, 0.5)
shadow.dialog   = 0 8px 24px rgba(0, 0, 0, 0.55)
```

Qt/QSS 无原生 box-shadow 时，浮动 Dock 依赖系统 frame；面板分隔用 `color.border.default` 1px 替代阴影。

---

## 7. State Token

```text
state.device.connected      = color.status.success
state.device.running        = color.status.running
state.device.warning        = color.status.warning
state.device.error          = color.status.error
state.device.disabled       = color.status.idle

state.scan.idle             = idle
state.scan.running          = running
state.scan.paused           = paused
state.scan.completed        = success
state.scan.failed           = error

state.control.default       = default
state.control.hover         = hover
state.control.pressed       = pressed
state.control.focus         = focus
state.control.disabled      = disabled
state.control.checked       = checked
state.control.error         = error
```

---

## 8. Motion Token

```text
motion.instant    = 0ms
motion.fast       = 150ms
motion.normal     = 200ms
motion.slow       = 300ms
motion.easing     = OutCubic
motion.easing.enter = OutCubic
motion.easing.exit  = InCubic
```

---

## 9. Z-Index Token

用于 QGraphicsScene 图层与 Overlay Widget  stacking（非 QSS z-index）。

```text
z.canvas.photo      = 0
z.canvas.heatmap    = 10
z.canvas.grid       = 20
z.canvas.region     = 30
z.canvas.path       = 40
z.canvas.marker     = 50
z.canvas.overlay    = 100
z.dock              = 100
z.breadcrumb        = 110
z.minimap           = 120
z.colorbar          = 130
z.tooltip           = 1000
z.dialog            = 2000
```

---

## 10. Qt / QSS 映射方式

### 10.1 Python 常量（Release 010 推荐）

```text
# tokens.py — 文档化示例，非可执行交付物
TOKENS = {
    "color.bg.app": "#07111D",
    "spacing.2": "8px",
    ...
}
```

### 10.2 QSS 模板替换

```text
QWidget#centralWidget {
    background-color: @color.bg.app@;
}
```

构建时由脚本将 `@color.bg.app@` 替换为 `#07111D`。

### 10.3 动态属性

状态不写入 Token 文件，而用 `state.*` 映射到 QSS 伪状态：

| Token | QSS |
|---|---|
| `state.control.hover` | `:hover` |
| `state.control.disabled` | `:disabled` |
| `state.control.focus` | `:focus` |
| `state.control.error` | `[error="true"]` |

### 10.4 Scene 层

画布颜色通过 `QColor(TOKENS["color.bg.canvas"])` 读取，不用 QSS。

### 10.5 完整映射表

见 [../06_QSS/token_mapping_qss.md](../06_QSS/token_mapping_qss.md)。

---

## 禁止事项

- 禁止在组件文档重复定义与本文冲突的 hex 值。
- 禁止新增 Token 不更新本表与 QSS 映射。
- 禁止 Token 名使用 camelCase 或中文。

## 相关文档

- [Color_Tokens.md](Color_Tokens.md)
- [Typography_Tokens.md](Typography_Tokens.md)
- [Spacing_Tokens.md](Spacing_Tokens.md)
- [Radius_Shadow_Tokens.md](Radius_Shadow_Tokens.md)
- [State_Tokens.md](State_Tokens.md)
