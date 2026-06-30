"""光标读数面板 — Release 014。"""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QPushButton, QVBoxLayout, QWidget


class CursorReadoutPanel(QGroupBox):
    lock_toggled = Signal(bool)
    copy_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("光标", parent)
        self.setObjectName("analysisCursorGroup")

        root = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(6)

        self._labels: dict[str, QLabel] = {}
        for key, title in (
            ("x", "X"),
            ("y", "Y"),
            ("z", "Z"),
            ("frequency", "频率"),
            ("amp", "幅度"),
            ("phase", "相位"),
        ):
            lbl = QLabel("—", self)
            lbl.setObjectName("cursorReadoutValue")
            lbl.setProperty("role", "statValue")
            self._labels[key] = lbl
            form.addRow(f"{title}：", lbl)

        root.addLayout(form)

        btn_row = QVBoxLayout()
        self._lock_btn = QPushButton("锁定光标", self)
        self._lock_btn.setObjectName("cursorLockButton")
        self._lock_btn.setProperty("variant", "secondary")
        self._lock_btn.clicked.connect(self._on_lock)
        copy_btn = QPushButton("复制读数", self)
        copy_btn.setObjectName("cursorCopyButton")
        copy_btn.setProperty("variant", "secondary")
        copy_btn.clicked.connect(self.copy_requested.emit)
        btn_row.addWidget(self._lock_btn)
        btn_row.addWidget(copy_btn)
        root.addLayout(btn_row)

        self._locked = False

    def update_readout(self, data: dict) -> None:
        self._labels["x"].setText(f"{data['x']:.2f} mm")
        self._labels["y"].setText(f"{data['y']:.2f} mm")
        self._labels["z"].setText(f"{data['z']:.2f} mm")
        self._labels["frequency"].setText(str(data["frequency"]))
        self._labels["amp"].setText(f"{data['amp']:.2f} dBm")
        self._labels["phase"].setText(f"{data['phase']:.1f}°")

    def set_locked(self, locked: bool) -> None:
        self._locked = locked
        self._lock_btn.setText("解锁光标" if locked else "锁定光标")

    def _on_lock(self) -> None:
        self._locked = not self._locked
        self.set_locked(self._locked)
        self.lock_toggled.emit(self._locked)
