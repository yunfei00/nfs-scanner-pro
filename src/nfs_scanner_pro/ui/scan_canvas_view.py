"""中央 PCB 扫描画布 — QGraphicsView + 整图热力图 Mock。"""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal, QRectF
from PySide6.QtGui import (
    QBrush,
    QColor,
    QImage,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
    QRadialGradient,
)
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsPixmapItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsTextItem,
    QGraphicsView,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data

PCB_X = 0.0
PCB_Y = 0.0
PCB_WIDTH = 1320.0
PCB_HEIGHT = 828.0
REGION_X = 192.0
REGION_Y = 88.0
REGION_W = 880.0
REGION_H = 560.0
HANDLE_SIZE = 14.0
PCB_VIEW_RECT = (PCB_X - 20, PCB_Y - 10, PCB_WIDTH + 40, PCB_HEIGHT + 50)
PCB_ZOOM_FACTOR = 1.05


def _build_radial_heatmap_pixmap(width: int, height: int) -> QPixmap:
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    cx, cy = width / 2.0, height / 2.0
    radius = max(width, height) * 0.55
    gradient = QRadialGradient(cx, cy, radius)
    gradient.setColorAt(0.0, QColor(239, 68, 68, 175))
    gradient.setColorAt(0.35, QColor(234, 179, 8, 140))
    gradient.setColorAt(0.65, QColor(34, 197, 94, 100))
    gradient.setColorAt(1.0, QColor(59, 130, 246, 70))
    painter.fillRect(image.rect(), gradient)
    painter.end()
    return QPixmap.fromImage(image)


def _build_minimap_pixmap() -> QPixmap:
    pix = QPixmap(148, 100)
    pix.fill(QColor("#134832"))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#185a3e"))
    painter.setPen(QPen(QColor("#2d8a62"), 1))
    painter.drawRoundedRect(20, 12, 108, 76, 2, 2)
    painter.setPen(QPen(QColor("#1a8cff"), 1))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(38, 24, 52, 36)
    grad = QRadialGradient(64, 42, 30)
    grad.setColorAt(0.0, QColor(239, 68, 68, 150))
    grad.setColorAt(1.0, QColor(59, 130, 246, 60))
    painter.fillRect(38, 24, 52, 36, grad)
    painter.end()
    return pix


def build_report_thumbnail_pixmap(width: int = 640, height: int = 180) -> QPixmap:
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(QColor("#0a1018"))
    painter = QPainter(image)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor("#185a3e"))
    painter.setPen(QPen(QColor("#2d8a62"), 1.5))
    painter.drawRoundedRect(40, 20, width - 80, height - 40, 8, 8)
    painter.setBrush(QColor("#0d1520"))
    painter.drawRect(120, 50, 80, 55)
    painter.drawRect(280, 70, 110, 70)
    pad_brush = QBrush(QColor("#c9a227"))
    for cx, cy in ((100, 40), (350, 55), (480, 80), (400, 120)):
        painter.setBrush(pad_brush)
        painter.drawEllipse(cx, cy, 4, 4)
    grad = QRadialGradient(320, 90, 80)
    grad.setColorAt(0.0, QColor(239, 68, 68, 200))
    grad.setColorAt(0.35, QColor(234, 179, 8, 150))
    grad.setColorAt(0.65, QColor(34, 197, 94, 100))
    grad.setColorAt(1.0, QColor(59, 130, 246, 60))
    painter.fillRect(160, 45, 320, 90, grad)
    painter.setPen(QPen(QColor(255, 255, 255, 120)))
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRect(160, 45, 320, 90)
    painter.end()
    return QPixmap.fromImage(image)


class ColorScaleWidget(QWidget):
    """色带浮层 — 对齐高保真右侧垂直居中布局。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("colorScaleWidget")
        self.setFixedSize(80, 286)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(8, 16, 26, 230))

        title_rect = self.rect().adjusted(4, 6, -4, -8)
        painter.setPen(QColor("#EAF2FF"))
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(
            title_rect,
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
            "幅度(dBm)",
        )

        bar = self.rect().adjusted(12, 28, -38, -10)
        grad = QLinearGradient(bar.topLeft(), bar.bottomLeft())
        grad.setColorAt(0.0, QColor("#EF4444"))
        grad.setColorAt(0.25, QColor("#EAB308"))
        grad.setColorAt(0.5, QColor("#22C55E"))
        grad.setColorAt(0.75, QColor("#06B6D4"))
        grad.setColorAt(1.0, QColor("#3B82F6"))
        painter.fillRect(bar, grad)
        painter.setPen(QPen(QColor("#243647")))
        painter.drawRect(bar)

        painter.setPen(QColor("#9EB0C4"))
        font.setPointSize(8)
        font.setBold(False)
        painter.setFont(font)
        labels = ["-10", "-20", "-30", "-40", "-50", "-60", "-70", "-80", "-90"]
        for i, label in enumerate(labels):
            y = bar.top() + (bar.height() * i) / (len(labels) - 1)
            painter.drawText(bar.right() + 6, int(y + 4), label)
        painter.end()


class ScanCanvasView(QGraphicsView):
    mouse_scene_moved = Signal(float, float)

    def __init__(self, parent: QWidget | None = None, *, show_handles: bool = True) -> None:
        super().__init__(parent)
        self.setObjectName("scanCanvasView")
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setBackgroundBrush(QColor("#0A1018"))
        self._show_handles = show_handles

        self._scene = QGraphicsScene(self)
        self._scene.setObjectName("scanScene")
        self.setScene(self._scene)
        self._build_scene()

    def _build_scene(self) -> None:
        pcb = QGraphicsRectItem(PCB_X, PCB_Y, PCB_WIDTH, PCB_HEIGHT)
        pcb.setBrush(QBrush(QColor("#185a3e")))
        pcb.setPen(QPen(QColor("#2d8a62"), 2))
        self._scene.addItem(pcb)

        inner = QGraphicsRectItem(PCB_X + 24, PCB_Y + 20, PCB_WIDTH - 48, PCB_HEIGHT - 40)
        inner.setBrush(QBrush(QColor("#134832")))
        inner.setPen(QPen(QColor("#1f6b4a"), 1))
        self._scene.addItem(inner)

        chips = [
            (80, 60, 180, 120, "#1a3d2e"),
            (320, 80, 140, 100, "#1e4534"),
            (520, 50, 200, 150, "#163828"),
            (620, 320, 200, 130, "#0a1220"),
            (980, 480, 100, 70, "#0d1520"),
        ]
        for x, y, w, h, color in chips:
            chip = QGraphicsRectItem(PCB_X + x, PCB_Y + y, w, h)
            chip.setBrush(QBrush(QColor(color)))
            chip.setPen(QPen(QColor("#2d5a48"), 1))
            self._scene.addItem(chip)

        trace_pen = QPen(QColor("#c9a227"), 1.2)
        trace_pen.setCosmetic(True)
        for x1, y1, x2, y2 in (
            (120, 200, 400, 180), (400, 180, 520, 140), (700, 160, 980, 130),
            (300, 420, 560, 400), (150, 300, 150, 420),
        ):
            line = QGraphicsLineItem(PCB_X + x1, PCB_Y + y1, PCB_X + x2, PCB_Y + y2)
            line.setPen(trace_pen)
            self._scene.addItem(line)

        pad_brush = QBrush(QColor("#c9a227"))
        via_pen = QPen(QColor("#c9a227"), 0.8)
        for gx in range(100, int(PCB_WIDTH - 40), 16):
            for gy in range(60, int(PCB_HEIGHT - 40), 16):
                h = (gx * 7 + gy * 13) % 97
                if h > 58:
                    continue
                r = 3.5 if h % 7 == 0 else (2.8 if h % 4 == 0 else 2.0)
                pad = QGraphicsEllipseItem(PCB_X + gx - r, PCB_Y + gy - r, r * 2, r * 2)
                pad.setBrush(pad_brush)
                pad.setPen(QPen(QColor("#a88420"), 0.5))
                pad.setOpacity(0.85)
                self._scene.addItem(pad)
                if h % 11 == 0:
                    via = QGraphicsEllipseItem(
                        PCB_X + gx - r - 2, PCB_Y + gy - r - 2, (r + 2) * 2, (r + 2) * 2
                    )
                    via.setBrush(Qt.BrushStyle.NoBrush)
                    via.setPen(via_pen)
                    via.setOpacity(0.45)
                    self._scene.addItem(via)

        region = QGraphicsRectItem(REGION_X, REGION_Y, REGION_W, REGION_H)
        region.setBrush(QBrush(QColor(255, 255, 255, 10)))
        region.setPen(QPen(QColor("#FFFFFF"), 2.5))
        self._scene.addItem(region)

        heat_item = QGraphicsPixmapItem(_build_radial_heatmap_pixmap(int(REGION_W), int(REGION_H)))
        heat_item.setPos(REGION_X, REGION_Y)
        heat_item.setOpacity(0.68)
        self._scene.addItem(heat_item)

        grid_pen = QPen(QColor(255, 255, 255, 40))
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        for gx in range(int(REGION_X), int(REGION_X + REGION_W) + 1, 40):
            line = QGraphicsLineItem(gx, REGION_Y, gx, REGION_Y + REGION_H)
            line.setPen(grid_pen)
            self._scene.addItem(line)
        for gy in range(int(REGION_Y), int(REGION_Y + REGION_H) + 1, 40):
            line = QGraphicsLineItem(REGION_X, gy, REGION_X + REGION_W, gy)
            line.setPen(grid_pen)
            self._scene.addItem(line)

        if self._show_handles:
            handle_pen = QPen(QColor("#1a8cff"), 2)
            handle_brush = QBrush(QColor("#FFFFFF"))
            for hx, hy in (
                (REGION_X - HANDLE_SIZE / 2, REGION_Y - HANDLE_SIZE / 2),
                (REGION_X + REGION_W / 2 - HANDLE_SIZE / 2, REGION_Y - HANDLE_SIZE / 2),
                (REGION_X + REGION_W - HANDLE_SIZE / 2, REGION_Y - HANDLE_SIZE / 2),
                (REGION_X - HANDLE_SIZE / 2, REGION_Y + REGION_H - HANDLE_SIZE / 2),
                (REGION_X + REGION_W - HANDLE_SIZE / 2, REGION_Y + REGION_H - HANDLE_SIZE / 2),
            ):
                handle = QGraphicsRectItem(hx, hy, HANDLE_SIZE, HANDLE_SIZE)
                handle.setBrush(handle_brush)
                handle.setPen(handle_pen)
                self._scene.addItem(handle)

        axis_color = QColor("#9EB0C4")
        for label, x, y in (
            ("X →", REGION_X + 8, REGION_Y + REGION_H + 28),
            ("Y →", PCB_X - 36, REGION_Y + REGION_H / 2),
            ("Z", PCB_X + PCB_WIDTH + 12, PCB_Y + 24),
        ):
            text = QGraphicsTextItem(label)
            text.setDefaultTextColor(axis_color)
            text.setPos(x, y)
            self._scene.addItem(text)

        self._scene.setSceneRect(-30, -10, PCB_WIDTH + 60, PCB_HEIGHT + 50)
        self._fit_pcb()

    def _fit_pcb(self) -> None:
        x, y, w, h = PCB_VIEW_RECT
        target = QRectF(x, y, w, h)
        self.resetTransform()
        self.fitInView(target, Qt.AspectRatioMode.KeepAspectRatio)
        if PCB_ZOOM_FACTOR != 1.0:
            self.scale(PCB_ZOOM_FACTOR, PCB_ZOOM_FACTOR)
        self.centerOn(PCB_X + PCB_WIDTH / 2, PCB_Y + PCB_HEIGHT / 2)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._scene.items():
            self._fit_pcb()

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        scene_pos: QPointF = self.mapToScene(event.position().toPoint())
        self.mouse_scene_moved.emit(scene_pos.x(), scene_pos.y())
        super().mouseMoveEvent(event)


class PcbCanvasWidget(QWidget):
    def __init__(
        self,
        *,
        object_name: str,
        breadcrumb: str,
        show_minimap: bool = True,
        show_handles: bool = True,
        overlay_mode: str = "coord",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName(object_name)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        breadcrumb_lbl = QLabel(breadcrumb, self)
        breadcrumb_lbl.setObjectName("breadcrumbBar")
        layout.addWidget(breadcrumb_lbl)

        self._canvas_container = QWidget(self)
        self._canvas_container.setObjectName("scanCanvasContainer")
        cl = QVBoxLayout(self._canvas_container)
        cl.setContentsMargins(0, 0, 0, 0)

        self._view = ScanCanvasView(self._canvas_container, show_handles=show_handles)
        cl.addWidget(self._view)

        self._color_scale = ColorScaleWidget(self._canvas_container)
        self._color_scale.setObjectName("colorScaleOverlay")

        self._minimap = QLabel(self._canvas_container)
        self._minimap.setObjectName("minimapOverlay")
        self._minimap.setPixmap(_build_minimap_pixmap())
        self._minimap.setFixedSize(132, 88)
        self._minimap.setVisible(show_minimap)

        self._minimap_title = QLabel("小地图", self._canvas_container)
        self._minimap_title.setObjectName("minimapTitleLabel")
        self._minimap_title.setProperty("role", "minimapTitle")
        self._minimap_title.setVisible(show_minimap)

        self._position_overlay = QLabel(self._canvas_container)
        self._position_overlay.setObjectName("canvasPositionOverlay")
        self._overlay_mode = overlay_mode
        self._update_position_overlay(mock_data.POSITION["x"], mock_data.POSITION["y"])
        self._view.mouse_scene_moved.connect(self._on_mouse_moved)

        layout.addWidget(self._canvas_container, stretch=1)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        margin = 14
        cw, ch = self._canvas_container.width(), self._canvas_container.height()
        cs_w = self._color_scale.width()
        cs_h = self._color_scale.height()
        self._color_scale.move(cw - cs_w - margin, max(margin, (ch - cs_h) // 2))

        if self._minimap.isVisible():
            mm_y = ch - self._minimap.height() - margin
            self._minimap_title.move(margin + 4, mm_y - 14)
            self._minimap.move(margin, mm_y)

        overlay_x = cw - self._position_overlay.width() - margin
        overlay_y = ch - self._position_overlay.height() - margin
        self._position_overlay.move(max(margin, overlay_x), max(margin, overlay_y))

    def _on_mouse_moved(self, sx: float, sy: float) -> None:
        rel_x = (sx - REGION_X) / REGION_W if REGION_W else 0
        rel_y = (sy - REGION_Y) / REGION_H if REGION_H else 0
        x = mock_data.POSITION["x"] + rel_x * 20.0
        y = mock_data.POSITION["y"] + rel_y * 20.0
        self._update_position_overlay(x, y)

    def _update_position_overlay(self, x: float, y: float) -> None:
        pos = mock_data.POSITION
        if self._overlay_mode == "cursor":
            text = (
                "光标读数\n"
                f"X：{x:.2f} mm · Y：{y:.2f} mm\n"
                f"幅度：{pos['amp']:.2f} dBm · 相位：112.3°"
            )
        else:
            text = (
                "当前坐标\n"
                f"X：{x:.2f} mm\nY：{y:.2f} mm\nZ：{pos['z']:.2f} mm\n"
                f"频率：{mock_data.FREQUENCY}\n幅度：{pos['amp']:.2f} dBm"
            )
        self._position_overlay.setText(text)
        self._position_overlay.adjustSize()


class ScanCanvasWidget(PcbCanvasWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            object_name="scanPage",
            breadcrumb=mock_data.BREADCRUMB_SCAN,
            show_minimap=True,
            show_handles=True,
            overlay_mode="coord",
            parent=parent,
        )
