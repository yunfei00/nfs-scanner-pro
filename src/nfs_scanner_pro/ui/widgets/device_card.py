"""设备页卡片组件。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DeviceCard(QWidget):
    action_clicked = Signal(str)

    def __init__(
        self,
        title: str,
        rows: list[tuple[str, str]],
        actions: list[tuple[str, str, str]],
        *,
        badge: str = "已连接",
        extra: QWidget | None = None,
        object_name: str | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName(object_name or f"deviceCard{title}")
        self.setProperty("card", True)
        self.setProperty("deviceCard", True)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setObjectName("deviceCardTitle")
        title_lbl.setProperty("role", "cardTitle")
        header.addWidget(title_lbl)
        header.addStretch()
        badge_lbl = QLabel(badge)
        badge_lbl.setObjectName("deviceCardBadge")
        badge_lbl.setProperty("role", "badge")
        badge_lbl.setProperty("connected", True)
        header.addWidget(badge_lbl)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        for i, (key, val) in enumerate(rows):
            key_lbl = QLabel(key)
            key_lbl.setProperty("role", "statKey")
            val_lbl = QLabel(val)
            val_lbl.setProperty("role", "statValue")
            val_lbl.setObjectName(f"deviceCardValue{i}")
            grid.addWidget(key_lbl, i, 0)
            grid.addWidget(val_lbl, i, 1)
        root.addLayout(grid)

        if extra is not None:
            root.addWidget(extra)

        if actions:
            actions_row = QHBoxLayout()
            actions_row.setSpacing(8)
            for obj_name, text, variant in actions:
                btn = QPushButton(text)
                btn.setObjectName(obj_name)
                btn.setProperty("variant", variant)
                btn.clicked.connect(lambda _=False, t=text: self.action_clicked.emit(t))
                actions_row.addWidget(btn)
            actions_row.addStretch()
            root.addLayout(actions_row)
