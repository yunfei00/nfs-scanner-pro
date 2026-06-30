"""LUT 色表选择控件 — Release 014。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QWidget

from nfs_scanner_pro.ui import mock_data


class LutSelector(QComboBox):
    value_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("lutSelector")
        for name in ("Turbo", "Jet", "Viridis", "Gray", "Hot"):
            self.addItem(name)
        idx = self.findText(mock_data.ANALYSIS_TASK["lut"])
        if idx >= 0:
            self.setCurrentIndex(idx)
        self.currentTextChanged.connect(self.value_changed.emit)
