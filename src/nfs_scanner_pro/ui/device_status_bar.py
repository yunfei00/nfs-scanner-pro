"""设备状态栏 — 单行展示四设备与扫描上下文。"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from nfs_scanner_pro.devices import get_device_manager
from nfs_scanner_pro.ui import mock_data


class DeviceStatusBar(QWidget):
    _FONT_MAX_PX = 13
    _FONT_MIN_PX = 10
    _SPACING_MAX = 6
    _SPACING_MIN = 2
    _MARGIN_MAX = 10
    _MARGIN_MIN = 2
    _DEVICE_PAD = 12
    _META_PAD = 8
    _SEP_PAD = 6

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("deviceStatusBar")
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(self._MARGIN_MAX, 0, self._MARGIN_MAX, 0)
        self._layout.setSpacing(self._SPACING_MAX)

        self._entries: list[dict] = []
        self._meta_entries: list[dict] = []
        self._device_labels: list[QLabel] = []
        indicator_names = [
            "deviceStatusMotionIndicator",
            "deviceStatusSpectrumIndicator",
            "deviceStatusCameraIndicator",
            "deviceStatusServoIndicator",
        ]

        for obj_name in indicator_names:
            label = QLabel("", self)
            label.setObjectName(obj_name)
            label.setProperty("role", "deviceChip")
            label.setWordWrap(False)
            self._layout.addWidget(label)
            self._device_labels.append(label)

        self._layout.addStretch(1)

        meta_parts = [
            f"探头：{mock_data.PROBE_NAME}",
            f"高度：{mock_data.POSITION['z']:.3f} mm",
            f"区域：{mock_data.REGION_NAME}",
            f"频率：{mock_data.FREQUENCY}",
            f"点数：{mock_data.POINTS}",
        ]
        for i, text in enumerate(meta_parts):
            if i > 0:
                sep = QLabel("|", self)
                sep.setObjectName("deviceStatusSeparator")
                sep.setProperty("role", "metaSep")
                sep.setWordWrap(False)
                self._layout.addWidget(sep)
                self._meta_entries.append(
                    {
                        "label": sep,
                        "full": "|",
                        "short": "|",
                        "allow_short": False,
                        "pad": self._SEP_PAD,
                    }
                )

            meta = QLabel(text, self)
            meta.setObjectName(
                "deviceStatusPointsLabel" if text.startswith("点数") else f"deviceStatusMeta{i}"
            )
            meta.setProperty("role", "deviceMeta")
            meta.setWordWrap(False)
            meta.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            self._layout.addWidget(meta)
            self._meta_entries.append(
                {
                    "label": meta,
                    "full": text,
                    "short": text,
                    "allow_short": False,
                    "pad": self._META_PAD,
                }
            )

        self.refresh_from_manager()

    def refresh_from_manager(self) -> None:
        manager = get_device_manager()
        manager.sync_mock_data()
        device_entries: list[dict] = []
        for label, device in zip(self._device_labels, manager.get_device_status()):
            detail = f"({device['detail']})" if device["detail"] else ""
            full = f"● {device['name']}{detail}"
            short = "● 舵机" if device["name"] == "舵机系统" else full
            label.setProperty("status", device["status"])
            label.setToolTip(
                manager.device_tooltips().get(device["name"], device["name"])
            )
            label.style().unpolish(label)
            label.style().polish(label)
            device_entries.append(
                {
                    "label": label,
                    "full": full,
                    "short": short,
                    "allow_short": device["name"] == "舵机系统",
                    "pad": self._DEVICE_PAD,
                }
            )
        self._entries = device_entries + self._meta_entries
        self._reflow()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._reflow()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._reflow()

    def _display_text(self, entry: dict, *, short_servo: bool) -> str:
        if short_servo and entry["allow_short"]:
            return entry["short"]
        return entry["full"]

    def _measure_total(
        self, metrics: QFontMetrics, spacing: int, *, short_servo: bool
    ) -> int:
        texts = [self._display_text(e, short_servo=short_servo) for e in self._entries]
        total = sum(
            metrics.horizontalAdvance(t) + entry["pad"]
            for t, entry in zip(texts, self._entries)
        )
        if len(texts) > 1:
            total += spacing * (len(texts) - 1)
        return total

    def _reflow(self) -> None:
        if self.width() <= 0:
            return

        for short_servo in (False, True):
            for margin in range(self._MARGIN_MAX, self._MARGIN_MIN - 1, -2):
                self._layout.setContentsMargins(margin, 0, margin, 0)
                available = self.width() - margin * 2
                for px in range(self._FONT_MAX_PX, self._FONT_MIN_PX - 1, -1):
                    for spacing in range(self._SPACING_MAX, self._SPACING_MIN - 1, -1):
                        font = QFont(self.font())
                        font.setPixelSize(px)
                        metrics = QFontMetrics(font)
                        if self._measure_total(metrics, spacing, short_servo=short_servo) <= available:
                            self._apply_layout(font, spacing, short_servo=short_servo)
                            return

        font = QFont(self.font())
        font.setPixelSize(self._FONT_MIN_PX)
        self._layout.setContentsMargins(self._MARGIN_MIN, 0, self._MARGIN_MIN, 0)
        self._layout.setSpacing(self._SPACING_MIN)
        self._apply_layout(font, self._SPACING_MIN, short_servo=True)

    def _apply_layout(self, font: QFont, spacing: int, *, short_servo: bool) -> None:
        self.setFont(font)
        self._layout.setSpacing(spacing)
        metrics = QFontMetrics(font)
        for entry in self._entries:
            label = entry["label"]
            text = self._display_text(entry, short_servo=short_servo)
            label.setFont(font)
            label.setText(text)
            width = metrics.horizontalAdvance(text) + entry["pad"]
            label.setFixedWidth(width)
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
