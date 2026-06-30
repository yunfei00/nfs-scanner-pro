"""运动平台 Jog 控制 Mock。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class JogControl(QWidget):
    jog_clicked = Signal(str)

    _PAD = (
        ("", None),
        ("Y+", "jogYPlus"),
        ("", None),
        ("X-", "jogXMinus"),
        ("●", "jogCenter"),
        ("X+", "jogXPlus"),
        ("", None),
        ("Y-", "jogYMinus"),
        ("", None),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("jogPad")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        grid = QGridLayout()
        grid.setSpacing(4)
        for i, (text, name) in enumerate(self._PAD):
            if not text:
                grid.addWidget(QWidget(), i // 3, i % 3)
                continue
            btn = QPushButton(text)
            if name:
                btn.setObjectName(name)
            btn.setFixedSize(36, 36)
            btn.setProperty("variant", "jog")
            btn.clicked.connect(lambda _=False, t=text: self.jog_clicked.emit(t))
            grid.addWidget(btn, i // 3, i % 3)
        root.addLayout(grid)

        z_row = QHBoxLayout()
        z_row.setSpacing(4)
        for text, name in (("Z+", "jogZPlus"), ("Z-", "jogZMinus")):
            btn = QPushButton(text)
            btn.setObjectName(name)
            btn.setFixedSize(48, 32)
            btn.setProperty("variant", "jog")
            btn.clicked.connect(lambda _=False, t=text: self.jog_clicked.emit(t))
            z_row.addWidget(btn)
        z_row.addStretch()
        root.addLayout(z_row)
