"""应用入口。"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from nfs_scanner_pro.ui.main_window import MainWindow, load_stylesheet


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("NFS Scanner Pro")
    app.setStyle("Fusion")
    load_stylesheet(app)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
