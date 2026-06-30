"""左侧图标导航栏 — 64px 折叠，点击按钮展开至 180px。"""

from __future__ import annotations

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt, Signal, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QButtonGroup,
    QStyle,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

NAV_COLLAPSED = 64
NAV_EXPANDED = 180
NAV_ANIM_MS = 180


class LeftNavigationBar(QWidget):
    """四页导航：扫描 / 设备 / 分析 / 报告。"""

    page_changed = Signal(int)
    expanded_changed = Signal(bool)

    _NAV_ITEMS = (
        ("navScanButton", "扫描", QStyle.StandardPixmap.SP_MediaPlay),
        ("navDeviceButton", "设备", QStyle.StandardPixmap.SP_DriveNetIcon),
        ("navAnalysisButton", "分析", QStyle.StandardPixmap.SP_FileDialogDetailedView),
        ("navReportButton", "报告", QStyle.StandardPixmap.SP_FileIcon),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("leftNavigationBar")
        self._expanded = False
        self._width = float(NAV_COLLAPSED)
        self.setFixedWidth(NAV_COLLAPSED)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(4)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: list[QToolButton] = []

        style = self.style()
        for index, (name, label, sp) in enumerate(self._NAV_ITEMS):
            btn = QToolButton(self)
            btn.setObjectName(name)
            btn.setCheckable(True)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            btn.setIcon(QIcon(style.standardIcon(sp)))
            btn.setIconSize(QSize(24, 24))
            btn.setText(label)
            btn.setToolTip(label)
            btn.setFixedHeight(52)
            self._group.addButton(btn, index)
            layout.addWidget(btn)
            self._buttons.append(btn)

        layout.addStretch()

        self._toggle_btn = QToolButton(self)
        self._toggle_btn.setObjectName("navToggleButton")
        self._toggle_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self._toggle_btn.setText("⟩")
        self._toggle_btn.setToolTip("展开导航")
        self._toggle_btn.setFixedHeight(40)
        self._toggle_btn.clicked.connect(self.toggle_collapsed)
        layout.addWidget(self._toggle_btn)

        self._buttons[0].setChecked(True)
        self._group.idClicked.connect(self.page_changed.emit)

        self._anim = QPropertyAnimation(self, b"navWidth", self)
        self._anim.setDuration(NAV_ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setProperty("expanded", False)

    def get_nav_width(self) -> float:
        return self._width

    def set_nav_width(self, value: float) -> None:
        self._width = value
        w = int(value)
        self.setFixedWidth(w)
        expanded = w > NAV_COLLAPSED + (NAV_EXPANDED - NAV_COLLAPSED) // 2
        style = (
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            if expanded
            else Qt.ToolButtonStyle.ToolButtonIconOnly
        )
        for btn in self._buttons:
            btn.setToolButtonStyle(style)

    navWidth = Property(float, get_nav_width, set_nav_width)

    @property
    def is_expanded(self) -> bool:
        return self._expanded

    def set_expanded(self, expanded: bool, *, animate: bool = True) -> None:
        if expanded == self._expanded and (
            (expanded and self.width() >= NAV_EXPANDED - 2)
            or (not expanded and self.width() <= NAV_COLLAPSED + 2)
        ):
            return
        self._expanded = expanded
        target = NAV_EXPANDED if expanded else NAV_COLLAPSED
        if animate:
            self._animate_to(target, expanded=expanded)
        else:
            self._anim.stop()
            self.set_nav_width(float(target))
            self.setProperty("expanded", expanded)
            self.style().unpolish(self)
            self.style().polish(self)
        self._update_toggle_button()
        self.expanded_changed.emit(self._expanded)

    def toggle_collapsed(self) -> None:
        self.set_expanded(not self._expanded)

    def _update_toggle_button(self) -> None:
        if self._expanded:
            self._toggle_btn.setText("⟨")
            self._toggle_btn.setToolTip("折叠导航")
        else:
            self._toggle_btn.setText("⟩")
            self._toggle_btn.setToolTip("展开导航")

    def _animate_to(self, target: int, *, expanded: bool) -> None:
        self.setProperty("expanded", expanded)
        self.style().unpolish(self)
        self.style().polish(self)
        self._anim.stop()
        self._anim.setStartValue(float(self.width()))
        self._anim.setEndValue(float(target))
        self._anim.start()
