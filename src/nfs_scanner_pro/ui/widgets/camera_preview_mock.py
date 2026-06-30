"""相机预览 Mock 区域。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class CameraPreviewMock(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("cameraPreviewMock")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._label = QLabel("相机预览区域（Mock）", self)
        self._label.setObjectName("cameraPreview")
        self._label.setProperty("role", "cameraPreview")
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setMinimumHeight(120)
        layout.addWidget(self._label)

    def set_status_text(self, text: str) -> None:
        self._label.setText(text)
