"""Hx / Hy 探头切换 Mock 控件。"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class HxHyControl(QWidget):
    action_clicked = Signal(str)
    probe_changed = Signal(str)

    def __init__(self, *, current: str = "Hx", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("hxHyControl")
        self._current = current

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(8)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(12)
        self._chips: dict[str, QLabel] = {}
        for name in ("Hx", "Hy"):
            chip = QLabel("", self)
            chip.setObjectName(f"servoChip{name}")
            chip.setProperty("role", "servoChip")
            chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
            chip.setMinimumWidth(72)
            chip.setMinimumHeight(48)
            chip_row.addWidget(chip, stretch=1)
            self._chips[name] = chip
        root.addLayout(chip_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for obj_name, text in (
            ("servoSwitchHxButton", "切换到 Hx"),
            ("servoSwitchHyButton", "切换到 Hy"),
        ):
            btn = QPushButton(text)
            btn.setObjectName(obj_name)
            btn.setProperty("variant", "action")
            btn.clicked.connect(lambda _=False, t=text: self.action_clicked.emit(t))
            btn_row.addWidget(btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        cal_row = QHBoxLayout()
        cal_row.setSpacing(8)
        for obj_name, text, variant in (
            ("servoCalibrateButton", "Hx/Hy 校准", "secondary"),
            ("servoApplyOffsetButton", "应用偏移补偿", "action"),
        ):
            btn = QPushButton(text)
            btn.setObjectName(obj_name)
            btn.setProperty("variant", variant)
            btn.clicked.connect(lambda _=False, t=text: self.action_clicked.emit(t))
            cal_row.addWidget(btn)
        cal_row.addStretch()
        root.addLayout(cal_row)

        self.set_probe(current)

    def set_probe(self, probe: str) -> None:
        self._current = probe
        for name, chip in self._chips.items():
            active = name == probe
            chip.setProperty("active", active)
            state = "当前" if active else "待命"
            chip.setText(f"{name}\n{state}")
            chip.style().unpolish(chip)
            chip.style().polish(chip)
        self.probe_changed.emit(probe)

    @property
    def current_probe(self) -> str:
        return self._current
