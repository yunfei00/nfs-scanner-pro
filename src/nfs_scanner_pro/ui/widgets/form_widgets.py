"""表单辅助控件。"""

from __future__ import annotations

from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QLineEdit, QVBoxLayout, QWidget


def read_only_row(label: str, value: str, parent: QWidget) -> tuple[QLabel, QLineEdit]:
    lbl = QLabel(label, parent)
    field = QLineEdit(value, parent)
    field.setReadOnly(True)
    return lbl, field


def placeholder_group(title: str, object_name: str, parent: QWidget) -> QGroupBox:
    group = QGroupBox(title, parent)
    group.setObjectName(object_name)
    group.setProperty("accordionHeader", True)
    group.setCheckable(True)
    group.setChecked(False)
    layout = QVBoxLayout(group)
    hint = QLabel("折叠 — 后续 Release 展开", group)
    hint.setProperty("role", "placeholder")
    layout.addWidget(hint)

    def sync_collapsed(checked: bool) -> None:
        hint.setVisible(checked)
        group.setMaximumHeight(16777215 if checked else 44)
        group.updateGeometry()

    group.toggled.connect(sync_collapsed)
    sync_collapsed(False)
    return group


def stat_grid(parent: QWidget, items: list[tuple[str, str]]) -> QWidget:
    from PySide6.QtWidgets import QGridLayout

    wrap = QWidget(parent)
    grid = QGridLayout(wrap)
    grid.setContentsMargins(0, 0, 0, 0)
    grid.setSpacing(6)
    for row, (k, v) in enumerate(items):
        k_lbl = QLabel(k, wrap)
        k_lbl.setProperty("role", "statKey")
        v_lbl = QLabel(v, wrap)
        v_lbl.setProperty("role", "statValue")
        grid.addWidget(k_lbl, row, 0)
        grid.addWidget(v_lbl, row, 1)
    return wrap
