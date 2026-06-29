"""中央 PCB 扫描画布 — QGraphicsView + 整图热力图占位。"""

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
)
from PySide6.QtWidgets import (
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

PCB_WIDTH = 820.0
PCB_HEIGHT = 520.0
REGION_X = 120.0
REGION_Y = 80.0
REGION_W = 560.0
REGION_H = 360.0


def _build_heatmap_pixmap(width: int, height: int) -> QPixmap:
    """整张 QImage 渐变模拟热力图，禁止逐格绘制。"""
    image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    gradient = QLinearGradient(0, 0, float(width), float(height))
    gradient.setColorAt(0.0, QColor(59, 130, 246, 90))
    gradient.setColorAt(0.45, QColor(234, 179, 8, 140))
    gradient.setColorAt(1.0, QColor(239, 68, 68, 170))
    painter.fillRect(image.rect(), gradient)
    painter.end()
    return QPixmap.fromImage(image)


class ScanCanvasView(QGraphicsView):
    mouse_scene_moved = Signal(float, float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("scanCanvasView")
        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QColor("#0A1520"))

        self._scene = QGraphicsScene(self)
        self._scene.setObjectName("scanScene")
        self.setScene(self._scene)
        self._build_scene()

    def _build_scene(self) -> None:
        # PCB 主区域
        pcb = QGraphicsRectItem(0, 0, PCB_WIDTH, PCB_HEIGHT)
        pcb.setBrush(QBrush(QColor("#132337")))
        pcb.setPen(QPen(QColor("#1E2D3D"), 2))
        pcb.setZValue(0)
        self._scene.addItem(pcb)

        # 扫描区域
        region = QGraphicsRectItem(REGION_X, REGION_Y, REGION_W, REGION_H)
        region.setBrush(QBrush(Qt.GlobalColor.transparent))
        region.setPen(QPen(QColor("#3B82F6"), 2, Qt.PenStyle.DashLine))
        region.setZValue(2)
        self._scene.addItem(region)

        # 热力图 — 单张 QPixmapItem
        hm_w, hm_h = int(REGION_W), int(REGION_H)
        heat_pix = _build_heatmap_pixmap(hm_w, hm_h)
        heat_item = QGraphicsPixmapItem(heat_pix)
        heat_item.setPos(REGION_X, REGION_Y)
        heat_item.setOpacity(0.72)
        heat_item.setZValue(1)
        self._scene.addItem(heat_item)

        # 网格点（装饰，非热力图数据格）
        step = 40
        dot_pen = QPen(QColor("#2A3F55"))
        for gx in range(int(REGION_X), int(REGION_X + REGION_W), step):
            for gy in range(int(REGION_Y), int(REGION_Y + REGION_H), step):
                dot = self._scene.addEllipse(gx - 1, gy - 1, 2, 2, dot_pen, QBrush(QColor("#2A3F55")))
                dot.setZValue(3)

        # 坐标轴标签
        for label, x, y in (
            ("X", REGION_X, PCB_HEIGHT + 12),
            ("Y", -28, REGION_Y + REGION_H / 2),
            ("Z", PCB_WIDTH + 8, 16),
        ):
            text = QGraphicsTextItem(label)
            text.setDefaultTextColor(QColor("#A8B3C2"))
            text.setPos(x, y)
            text.setZValue(4)
            self._scene.addItem(text)

        self._scene.setSceneRect(-40, -10, PCB_WIDTH + 60, PCB_HEIGHT + 40)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        scene_pos: QPointF = self.mapToScene(event.position().toPoint())
        self.mouse_scene_moved.emit(scene_pos.x(), scene_pos.y())
        super().mouseMoveEvent(event)


class ScanCanvasWidget(QWidget):
    """面包屑 + 画布 + 鼠标位置浮窗。"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("scanPage")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(4)

        self._breadcrumb = QLabel(mock_data.BREADCRUMB, self)
        self._breadcrumb.setObjectName("breadcrumbBar")
        layout.addWidget(self._breadcrumb)

        canvas_container = QWidget(self)
        canvas_container.setObjectName("scanCanvasContainer")
        self._canvas_container = canvas_container
        container_layout = QVBoxLayout(canvas_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        self._view = ScanCanvasView(canvas_container)
        container_layout.addWidget(self._view)

        self._position_overlay = QLabel(canvas_container)
        self._position_overlay.setObjectName("canvasPositionOverlay")
        self._position_overlay.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._update_position_overlay(mock_data.POSITION["x"], mock_data.POSITION["y"])
        self._position_overlay.adjustSize()
        self._view.mouse_scene_moved.connect(self._on_mouse_moved)

        layout.addWidget(canvas_container, stretch=1)

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        margin = 12
        cw = self._canvas_container.width()
        ch = self._canvas_container.height()
        self._position_overlay.move(
            cw - self._position_overlay.width() - margin,
            ch - self._position_overlay.height() - margin,
        )

    def _on_mouse_moved(self, sx: float, sy: float) -> None:
        # 将场景坐标映射为 mock mm 读数
        x = mock_data.POSITION["x"] + (sx - REGION_X) * 0.05
        y = mock_data.POSITION["y"] + (sy - REGION_Y) * 0.05
        self._update_position_overlay(x, y)

    def _update_position_overlay(self, x: float, y: float) -> None:
        pos = mock_data.POSITION
        self._position_overlay.setText(
            f"X: {x:.2f} mm\n"
            f"Y: {y:.2f} mm\n"
            f"Z: {pos['z']:.2f} mm\n"
            f"频率: {mock_data.FREQUENCY}\n"
            f"幅度: {pos['amp']:.2f} dBm"
        )
        self._position_overlay.adjustSize()
