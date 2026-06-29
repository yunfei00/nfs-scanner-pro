"""设备页卡片组件。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
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
        actions: list[tuple[str, str]],
        *,
        badge: str = "已连接",
        extra: QWidget | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName(f"deviceCard{title}")
        self.setProperty("card", True)

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
        header.addWidget(badge_lbl)
        root.addLayout(header)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(6)
        for i, (k, v) in enumerate(rows):
            k_lbl = QLabel(k)
            k_lbl.setProperty("role", "statKey")
            v_lbl = QLabel(v)
            v_lbl.setProperty("role", "statValue")
            grid.addWidget(k_lbl, i, 0)
            grid.addWidget(v_lbl, i, 1)
        root.addLayout(grid)

        if extra is not None:
            root.addWidget(extra)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(8)
        for obj_name, text in actions:
            btn = QPushButton(text)
            btn.setObjectName(obj_name)
            btn.setProperty("variant", "primary" if "测试" in text or "拍照" in text else "action")
            if "校准" in text:
                btn.setProperty("variant", "secondary")
            btn.clicked.connect(lambda _=False, t=text: self.action_clicked.emit(t))
            actions_row.addWidget(btn)
        actions_row.addStretch()
        root.addLayout(actions_row)


class JogPad(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("jogPad")
        grid = QGridLayout(self)
        grid.setSpacing(4)
        labels = [
            ("", None), ("Y+", "jogYPlus"), ("", None),
            ("X-", "jogXMinus"), ("●", "jogCenter"), ("X+", "jogXPlus"),
            ("", None), ("Y-", "jogYMinus"), ("", None),
        ]
        for i, (text, name) in enumerate(labels):
            if not text:
                grid.addWidget(QWidget(), i // 3, i % 3)
                continue
            btn = QPushButton(text)
            if name:
                btn.setObjectName(name)
            btn.setFixedSize(36, 36)
            btn.setProperty("variant", "jog")
            grid.addWidget(btn, i // 3, i % 3)


class ServoSelector(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("servoSelector")
        row = QHBoxLayout(self)
        row.setSpacing(12)
        for name, active in (("Hx", True), ("Hy", False)):
            chip = QLabel(f"{name}\n{'当前' if active else '待命'}")
            chip.setObjectName(f"servoChip{name}")
            chip.setProperty("role", "servoChip")
            chip.setProperty("active", active)
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row.addWidget(chip, stretch=1)
