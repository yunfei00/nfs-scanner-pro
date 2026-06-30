"""打开最近项目子菜单 — Release 016。"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

from nfs_scanner_pro import project_mock


def populate_recent_project_menu(
    menu: QMenu,
    on_open: Callable[[str], None],
) -> None:
    """填充「打开最近项目」子菜单。"""
    menu.clear()
    for item in project_mock.get_recent_projects():
        act = QAction(item["name"], menu)
        act.triggered.connect(lambda _checked=False, name=item["name"]: on_open(name))
        menu.addAction(act)
