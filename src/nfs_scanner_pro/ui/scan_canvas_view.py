"""中央 PCB 扫描画布 — QGraphicsView + 整图热力图 Mock。"""

from __future__ import annotations

from PySide6.QtCore import QPointF, Qt, Signal
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

# 场景坐标 — 对齐高保真 PCB 比例
PCB_X = 0.0
PCB_Y = 0.0
PCB_WIDTH = 1320.0
PCB_HEIGHT = 828.0
REGION_X = 192.0
REGION_Y = 88.0
REGION_W = 880.0
REGION_H = 560.0
HANDLE_SIZE = 14.0


def _build_radial_heatmap_pixmap(width: int, height: int) -> QPixmap:
    """整张 QImage 径向渐变模拟热力图，禁止逐格绘制。"""
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


class ColorScaleWidget(QWidget):
    """色带 Mock — 幅度(dBm) -10 … -90。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("colorScaleWidget")
        self.setFixedSize(52, 220)

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(4, 24, -20, -4)
        grad = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        grad.setColorAt(0.0, QColor("#EF4444"))
        grad.setColorAt(0.25, QColor("#EAB308"))
        grad.setColorAt(0.5, QColor("#22C55E"))
        grad.setColorAt(0.75, QColor("#06B6D4"))
        grad.setColorAt(1.0, QColor("#3B82F6"))
        painter.fillRect(rect, grad)
        painter.setPen(QPen(QColor("#1E2D3D")))
        painter.drawRect(rect)
        painter.setPen(QColor("#A8B3C2"))
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        painter.drawText(0, 16, "幅度(dBm)")
        labels = ["-10", "-20", "-30", "-40", "-50", "-60", "-70", "-80", "-90"]
        for i, label in enumerate(labels):
            y = rect.top() + (rect.height() * i) / (len(labels) - 1)
            painter.drawText(rect.right() + 4, int(y + 4), label)
        painter.end()


class ScanCanvasView(QGraphicsView):
    mouse_scene_moved = Signal(float, float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("scanCanvasView")
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QColor("#0A1018"))

        self._scene = QGraphicsScene(self)
        self._scene.setObjectName("scanScene")
        self.setScene(self._scene)
        self._build_scene()

    def _build_scene(self) -> None:
        # 深绿 PCB 基板
        pcb = QGraphicsRectItem(PCB_X, PCB_Y, PCB_WIDTH, PCB_HEIGHT)
        pcb.setBrush(QBrush(QColor("#185a3e")))
        pcb.setPen(QPen(QColor("#2d8a62"), 2))
        pcb.setZValue(0)
        self._scene.addItem(pcb)

        # 内层铜区
        inner = QGraphicsRectItem(PCB_X + 24, PCB_Y + 20, PCB_WIDTH - 48, PCB_HEIGHT - 40)
        inner.setBrush(QBrush(QColor("#134832")))
        inner.setPen(QPen(QColor("#1f6b4a"), 1))
        inner.setZValue(1)
        self._scene.addItem(inner)

        # 芯片矩形
        chips = [
            (80, 60, 180, 120, "#1a3d2e"),
            (320, 80, 140, 100, "#1e4534"),
            (520, 50, 200, 150, "#163828"),
            (780, 90, 160, 110, "#1a4030"),
            (980, 70, 220, 130, "#184032"),
            (200, 420, 260, 180, "#1c4436"),
            (560, 380, 300, 200, "#184030"),
            (920, 400, 240, 160, "#1a3a2c"),
        ]
        for x, y, w, h, color in chips:
            chip = QGraphicsRectItem(PCB_X + x, PCB_Y + y, w, h)
            chip.setBrush(QBrush(QColor(color)))
            chip.setPen(QPen(QColor("#2d5a48"), 1))
            chip.setZValue(2)
            self._scene.addItem(chip)

        # 走线
        trace_pen = QPen(QColor("#c9a227"), 1.2)
        trace_pen.setCosmetic(True)
        traces = [
            (120, 200, 400, 180),
            (400, 180, 520, 140),
            (700, 160, 980, 130),
            (300, 420, 560, 400),
            (860, 400, 1100, 380),
            (150, 300, 150, 420),
        ]
        for x1, y1, x2, y2 in traces:
            line = QGraphicsLineItem(PCB_X + x1, PCB_Y + y1, PCB_X + x2, PCB_Y + y2)
            line.setPen(trace_pen)
            line.setZValue(3)
            self._scene.addItem(line)

        # 金色焊盘 / 过孔
        pad_brush = QBrush(QColor("#c9a227"))
        via_pen = QPen(QColor("#c9a227"), 0.8)
        for gx in range(100, int(PCB_WIDTH - 40), 16):
            for gy in range(60, int(PCB_HEIGHT - 40), 16):
                h = (gx * 7 + gy * 13) % 97
                if h > 58:
                    continue
                r = 3.5 if h % 7 == 0 else (2.8 if h % 4 == 0 else 2.0)
                pad = QGraphicsEllipseItem(
                    PCB_X + gx - r, PCB_Y + gy - r, r * 2, r * 2
                )
                pad.setBrush(pad_brush)
                pad.setPen(QPen(QColor("#a88420"), 0.5))
                pad.setOpacity(0.85)
                pad.setZValue(4)
                self._scene.addItem(pad)
                if h % 11 == 0:
                    via = QGraphicsEllipseItem(
                        PCB_X + gx - r - 2, PCB_Y + gy - r - 2, (r + 2) * 2, (r + 2) * 2
                    )
                    via.setBrush(Qt.BrushStyle.NoBrush)
                    via.setPen(via_pen)
                    via.setOpacity(0.45)
                    via.setZValue(4)
                    self._scene.addItem(via)

        # 扫描区域白框
        region = QGraphicsRectItem(REGION_X, REGION_Y, REGION_W, REGION_H)
        region.setBrush(QBrush(QColor(255, 255, 255, 10)))
        region.setPen(QPen(QColor("#FFFFFF"), 2.5))
        region.setZValue(6)
        self._scene.addItem(region)

        # 热力图 — 单张 QPixmapItem
        hm_w, hm_h = int(REGION_W), int(REGION_H)
        heat_pix = _build_radial_heatmap_pixmap(hm_w, hm_h)
        heat_item = QGraphicsPixmapItem(heat_pix)
        heat_item.setPos(REGION_X, REGION_Y)
        heat_item.setOpacity(0.68)
        heat_item.setZValue(5)
        self._scene.addItem(heat_item)

        # 扫描点网格（装饰线，非热力图数据格）
        grid_pen = QPen(QColor(255, 255, 255, 40))
        grid_pen.setStyle(Qt.PenStyle.DotLine)
        step = 40
        for gx in range(int(REGION_X), int(REGION_X + REGION_W) + 1, step):
            line = QGraphicsLineItem(gx, REGION_Y, gx, REGION_Y + REGION_H)
            line.setPen(grid_pen)
            line.setZValue(7)
            self._scene.addItem(line)
        for gy in range(int(REGION_Y), int(REGION_Y + REGION_H) + 1, step):
            line = QGraphicsLineItem(REGION_X, gy, REGION_X + REGION_W, gy)
            line.setPen(grid_pen)
            line.setZValue(7)
            self._scene.addItem(line)

        # 拖拽手柄
        handle_pen = QPen(QColor("#1a8cff"), 2)
        handle_brush = QBrush(QColor("#FFFFFF"))
        handle_positions = [
            (REGION_X - HANDLE_SIZE / 2, REGION_Y - HANDLE_SIZE / 2),
            (REGION_X + REGION_W / 2 - HANDLE_SIZE / 2, REGION_Y - HANDLE_SIZE / 2),
            (REGION_X + REGION_W - HANDLE_SIZE / 2, REGION_Y - HANDLE_SIZE / 2),
            (REGION_X - HANDLE_SIZE / 2, REGION_Y + REGION_H / 2 - HANDLE_SIZE / 2),
            (REGION_X + REGION_W - HANDLE_SIZE / 2, REGION_Y + REGION_H / 2 - HANDLE_SIZE / 2),
            (REGION_X - HANDLE_SIZE / 2, REGION_Y + REGION_H - HANDLE_SIZE / 2),
            (REGION_X + REGION_W / 2 - HANDLE_SIZE / 2, REGION_Y + REGION_H - HANDLE_SIZE / 2),
            (REGION_X + REGION_W - HANDLE_SIZE / 2, REGION_Y + REGION_H - HANDLE_SIZE / 2),
        ]
        for hx, hy in handle_positions:
            handle = QGraphicsRectItem(hx, hy, HANDLE_SIZE, HANDLE_SIZE)
            handle.setBrush(handle_brush)
            handle.setPen(handle_pen)
            handle.setZValue(8)
            self._scene.addItem(handle)

        # 坐标轴
        axis_color = QColor("#9EB0C4")
        for label, x, y in (
            ("X →", REGION_X + 8, REGION_Y + REGION_H + 28),
            ("Y →", PCB_X - 36, REGION_Y + REGION_H / 2),
            ("Z", PCB_X + PCB_WIDTH + 12, PCB_Y + 24),
        ):
            text = QGraphicsTextItem(label)
            text.setDefaultTextColor(axis_color)
            text.setPos(x, y)
            text.setZValue(9)
            self._scene.addItem(text)

        self._scene.setSceneRect(-50, -20, PCB_WIDTH + 80, PCB_HEIGHT + 60)
        self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if self._scene.items():
            self.fitInView(self._scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        scene_pos: QPointF = self.mapToScene(event.position().toPoint())
        self.mouse_scene_moved.emit(scene_pos.x(), scene_pos.y())
        super().mouseMoveEvent(event)


class ScanCanvasWidget(QWidget):
    """面包屑 + 画布 + 色带/小地图/坐标浮窗。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("scanPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        self._breadcrumb = QLabel(mock_data.BREADCRUMB, self)
        self._breadcrumb.setObjectName("breadcrumbBar")
        layout.addWidget(self._breadcrumb)

        self._canvas_container = QWidget(self)
        self._canvas_container.setObjectName("scanCanvasContainer")
        container_layout = QVBoxLayout(self._canvas_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self._view = ScanCanvasView(self._canvas_container)
        container_layout.addWidget(self._view)

        self._color_scale = ColorScaleWidget(self._canvas_container)
        self._color_scale.setObjectName("colorScaleOverlay")

        self._minimap = QLabel(self._canvas_container)
        self._minimap.setObjectName("minimapOverlay")
        self._minimap.setPixmap(_build_minimap_pixmap())
        self._minimap.setFixedSize(148, 100)
        self._minimap.setScaledContents(True)

        minimap_title = QLabel("小地图", self._canvas_container)
        minimap_title.setObjectName("minimapTitleLabel")
        minimap_title.setStyleSheet("color: #6B8299; font-size: 11px;")
        self._minimap_title = minimap_title

        self._position_overlay = QLabel(self._canvas_container)
        self._position_overlay.setObjectName("canvasPositionOverlay")
        self._position_overlay.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self._update_position_overlay(mock_data.POSITION["x"], mock_data.POSITION["y"])
        self._view.mouse_scene_moved.connect(self._on_mouse_moved)

        layout.addWidget(self._canvas_container, stretch=1)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        margin = 12
        cw = self._canvas_container.width()
        ch = self._canvas_container.height()

        self._color_scale.move(margin, ch - self._color_scale.height() - margin)

        mm_x = cw - self._minimap.width() - margin
        mm_y = ch - self._minimap.height() - margin - 16
        self._minimap_title.move(mm_x + 6, mm_y - 14)
        self._minimap.move(mm_x, mm_y)

        self._position_overlay.move(
            cw - self._position_overlay.width() - margin,
            margin,
        )

    def _on_mouse_moved(self, sx: float, sy: float) -> None:
        rel_x = (sx - REGION_X) / REGION_W if REGION_W else 0
        rel_y = (sy - REGION_Y) / REGION_H if REGION_H else 0
        x = mock_data.POSITION["x"] + rel_x * 20.0
        y = mock_data.POSITION["y"] + rel_y * 20.0
        self._update_position_overlay(x, y)

    def _update_position_overlay(self, x: float, y: float) -> None:
        pos = mock_data.POSITION
        self._position_overlay.setText(
            "当前坐标\n"
            f"X：{x:.2f} mm\n"
            f"Y：{y:.2f} mm\n"
            f"Z：{pos['z']:.2f} mm\n"
            f"频率：{mock_data.FREQUENCY}\n"
            f"幅度：{pos['amp']:.2f} dBm"
        )
        self._position_overlay.adjustSize()
