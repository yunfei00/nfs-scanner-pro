"""报告页 — 列表 + PDF 风预览。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.scan_canvas_view import build_report_thumbnail_pixmap


class ReportPage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("reportPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        crumb = QLabel(f"报告 > {mock_data.PROJECT_NAME} > CPU_Area 扫描报告", self)
        crumb.setObjectName("breadcrumbBar")
        crumb.setProperty("role", "pageBreadcrumb")
        root.addWidget(crumb)

        workspace = QHBoxLayout()
        workspace.setSpacing(0)

        self._list = QWidget(self)
        self._list.setObjectName("reportList")
        self._list.setFixedWidth(320)
        ll = QVBoxLayout(self._list)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(0)
        header = QLabel("报告列表", self._list)
        header.setObjectName("reportListHeader")
        header.setProperty("role", "listHeader")
        ll.addWidget(header)

        self._items: list[QFrame] = []
        for i, report in enumerate(mock_data.REPORTS):
            item = QFrame(self._list)
            item.setObjectName(f"reportListItem{report['id']}")
            item.setProperty("role", "reportListItem")
            item.setProperty("active", i == 0)
            il = QVBoxLayout(item)
            il.setContentsMargins(16, 12, 16, 12)
            t = QLabel(report["title"], item)
            t.setProperty("role", "reportTitle")
            m = QLabel(report["meta"], item)
            m.setProperty("role", "reportMeta")
            il.addWidget(t)
            il.addWidget(m)
            ll.addWidget(item)
            self._items.append(item)
        ll.addStretch()
        workspace.addWidget(self._list)

        scroll = QScrollArea(self)
        scroll.setObjectName("reportPreviewScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        preview_host = QWidget()
        preview_host.setObjectName("reportPreviewHost")
        pl = QVBoxLayout(preview_host)
        pl.setContentsMargins(20, 20, 20, 20)

        card = QFrame(preview_host)
        card.setObjectName("reportPreviewCard")
        card.setProperty("role", "pdfCard")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(32, 32, 32, 32)

        report = mock_data.REPORTS[0]
        cl.addWidget(self._pdf_label("CPU_Area 近场扫描报告", "pdfTitle"))
        meta = QGridLayout()
        meta.setHorizontalSpacing(24)
        meta.setVerticalSpacing(8)
        fields = [
            ("报告名称", report["title"]),
            ("项目名称", mock_data.PROJECT_NAME),
            ("区域名称", mock_data.REGION_NAME),
            ("扫描时间", report["scan_time"]),
            ("探头", report["probe"]),
            ("频率", mock_data.FREQUENCY),
        ]
        for i, (k, v) in enumerate(fields):
            kl = QLabel(k)
            kl.setProperty("role", "pdfMetaKey")
            vl = QLabel(v)
            vl.setProperty("role", "pdfMetaValue")
            meta.addWidget(kl, i // 2, (i % 2) * 2)
            meta.addWidget(vl, i // 2, (i % 2) * 2 + 1)
        cl.addLayout(meta)

        thumb = QLabel(card)
        thumb.setObjectName("reportThumb")
        thumb.setPixmap(build_report_thumbnail_pixmap())
        thumb.setScaledContents(True)
        thumb.setFixedHeight(180)
        cl.addWidget(thumb)

        summary = QLabel(
            "结论摘要：CPU 区域在 2.450 GHz 出现局部辐射峰值（-23.45 dBm），"
            "位于 U2·CPU 封装东北侧 12 mm 处。建议进一步 Hy 扫描对比极化分量。"
            "（Mock 占位，不生成真实 PDF）",
            card,
        )
        summary.setWordWrap(True)
        summary.setProperty("role", "pdfSummary")
        cl.addWidget(summary)

        pl.addWidget(card)
        pl.addStretch()
        scroll.setWidget(preview_host)
        workspace.addWidget(scroll, stretch=1)
        root.addLayout(workspace, stretch=1)

    @staticmethod
    def _pdf_label(text: str, role: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setProperty("role", role)
        return lbl
