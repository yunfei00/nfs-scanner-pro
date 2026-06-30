"""报告 PDF 风预览面板 — Release 015。"""

from __future__ import annotations

from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from nfs_scanner_pro.ui import mock_data
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

        self._meta = QGridLayout()
        self._meta.setHorizontalSpacing(24)
        self._meta.setVerticalSpacing(8)
        cl.addLayout(self._meta)
        self._meta_labels: list[tuple[QLabel, QLabel]] = []

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

        pl.addWidget(self._card)
        pl.addStretch()
        self.setWidget(host)

        self.show_report(mock_data.REPORTS[0])

    def show_report(self, report: dict) -> None:
        while self._meta.count():
            item = self._meta.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._meta_labels.clear()

        region = report.get("region", mock_data.REGION_NAME)
        probe_label = report["probe"]
        if probe_label in ("Hx", "Hy"):
            probe_label = f"{probe_label}(100 μm)" if probe_label == "Hx" else "Hy(100 μm)"

        fields = [
            ("报告名称", report["name"]),
            ("项目名称", report.get("project", mock_data.PROJECT_NAME)),
            ("区域名称", region),
            ("探头", probe_label),
            ("扫描时间", report.get("scan_time", f"{report['time']}:00")),
            ("频率", report.get("frequency", mock_data.FREQUENCY)),
        ]
        for i, (k, v) in enumerate(fields):
            kl = QLabel(k)
            kl.setProperty("role", "pdfMetaKey")
            vl = QLabel(v)
            vl.setProperty("role", "pdfMetaValue")
            self._meta.addWidget(kl, i // 2, (i % 2) * 2)
            self._meta.addWidget(vl, i // 2, (i % 2) * 2 + 1)
            self._meta_labels.append((kl, vl))

        self._title_lbl.setText(f"{region} 近场扫描报告")
        self._summary.setText(f"结论摘要：{report.get('summary', '')}")
