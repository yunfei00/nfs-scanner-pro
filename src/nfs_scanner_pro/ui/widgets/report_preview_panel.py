"""报告 PDF 风预览面板 — Release 015/022。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from nfs_scanner_pro.report.report_preview_model import ReportPreviewModel
from nfs_scanner_pro.ui.scan_canvas_view import build_report_thumbnail_pixmap


class ReportPreviewPanel(QScrollArea):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("reportPreviewScroll")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)

        host = QWidget()
        host.setObjectName("reportPreviewHost")
        pl = QVBoxLayout(host)
        pl.setContentsMargins(20, 20, 20, 20)

        self._card = QFrame(host)
        self._card.setObjectName("reportPreviewCard")
        self._card.setProperty("role", "pdfCard")
        cl = QVBoxLayout(self._card)
        cl.setContentsMargins(32, 32, 32, 32)

        self._title_lbl = QLabel("CPU_Area 近场扫描报告", self._card)
        self._title_lbl.setProperty("role", "pdfTitle")
        cl.addWidget(self._title_lbl)

        self._meta_host = QWidget(self._card)
        self._meta = QGridLayout(self._meta_host)
        self._meta.setHorizontalSpacing(24)
        self._meta.setVerticalSpacing(8)
        self._meta.setContentsMargins(0, 0, 0, 0)
        cl.addWidget(self._meta_host)

        self._thumb = QLabel(self._card)
        self._thumb.setObjectName("reportThumb")
        self._thumb.setPixmap(build_report_thumbnail_pixmap())
        self._thumb.setScaledContents(True)
        self._thumb.setFixedHeight(180)
        cl.addWidget(self._thumb)

        self._summary = QLabel(self._card)
        self._summary.setWordWrap(True)
        self._summary.setProperty("role", "pdfSummary")
        cl.addWidget(self._summary)

        self._footer = QLabel(self._card)
        self._footer.setWordWrap(True)
        self._footer.setProperty("role", "pdfFooter")
        cl.addWidget(self._footer)

        self._empty_overlay = QLabel(self._card)
        self._empty_overlay.setObjectName("reportPreviewEmpty")
        self._empty_overlay.setProperty("role", "emptyOverlay")
        self._empty_overlay.setWordWrap(True)
        self._empty_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_overlay.hide()
        cl.addWidget(self._empty_overlay)

        pl.addWidget(self._card)
        pl.addStretch()
        self.setWidget(host)

    def show_report(self, report: dict) -> None:
        model = ReportPreviewModel.from_list_item(report)
        self.show_model(model)

    def show_model(self, model: ReportPreviewModel) -> None:
        self._clear_meta()
        self._empty_overlay.hide()
        self._meta_host.show()
        self._thumb.show()
        self._summary.show()
        self._footer.show()

        if model.empty:
            self._title_lbl.setText(model.title or "报告预览")
            self._meta_host.hide()
            self._thumb.hide()
            self._summary.hide()
            self._footer.hide()
            self._empty_overlay.setText(model.empty_message)
            self._empty_overlay.show()
            return

        for i, (key, value) in enumerate(model.basic_info.items()):
            kl = QLabel(key, self._meta_host)
            kl.setProperty("role", "pdfMetaKey")
            vl = QLabel(value, self._meta_host)
            vl.setProperty("role", "pdfMetaValue")
            vl.setWordWrap(True)
            self._meta.addWidget(kl, i // 2, (i % 2) * 2)
            self._meta.addWidget(vl, i // 2, (i % 2) * 2 + 1)

        self._title_lbl.setText(model.title)
        if model.heatmap_preview:
            self._thumb.setPixmap(build_report_thumbnail_pixmap())
            self._thumb.show()
        else:
            self._thumb.hide()
        self._summary.setText(f"结论摘要：{model.summary}")
        self._footer.setText(model.footer)

    def _clear_meta(self) -> None:
        while self._meta.count():
            item = self._meta.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
