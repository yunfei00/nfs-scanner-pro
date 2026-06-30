"""项目相关对话框 — 深色 frameless 标题栏 Mock（Release 016）。"""

from __future__ import annotations

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from nfs_scanner_pro import project_mock


class _ProjectDialogTitleBar(QWidget):
    """自定义深色标题栏 — 左侧标题、右侧关闭，支持拖动。"""

    def __init__(self, dialog: QDialog, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("projectDialogTitleBar")
        self.setFixedHeight(40)
        self._dialog = dialog
        self._drag_offset: QPoint | None = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 8, 0)
        layout.setSpacing(8)

        title_label = QLabel(title, self)
        title_label.setObjectName("projectDialogTitleBarLabel")
        layout.addWidget(title_label)
        layout.addStretch(1)

        close_btn = QPushButton("×", self)
        close_btn.setObjectName("projectDialogCloseButton")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(dialog.reject)
        layout.addWidget(close_btn)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self._dialog.frameGeometry().topLeft()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if self._drag_offset is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self._dialog.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._drag_offset = None
        super().mouseReleaseEvent(event)


class _ProjectDialogBase(QDialog):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("projectDialog")
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(480)
        self.setWindowFlags(
            Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint
        )

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_ProjectDialogTitleBar(self, title, self))

        content = QWidget(self)
        content.setObjectName("projectDialogContent")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 20)
        content_layout.setSpacing(16)

        self._body = QWidget(content)
        self._body.setObjectName("projectDialogBody")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(0, 0, 0, 0)
        self._body_layout.setSpacing(12)
        content_layout.addWidget(self._body)

        self._buttons = QDialogButtonBox(content)
        content_layout.addWidget(self._buttons)

        root.addWidget(content)


class NewProjectDialog(_ProjectDialogBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("新建项目", parent)

        form = QFormLayout()
        form.setSpacing(10)
        self._name = QLineEdit("Demo_Project_001", self)
        self._path = QLineEdit("D:/NFS_Projects/Demo_Project_001", self)
        self._pcb = QLineEdit("iPhone16_Mainboard", self)
        self._region = QLineEdit("CPU_Area", self)
        for field in (self._name, self._path, self._pcb, self._region):
            field.setObjectName("projectDialogField")
        form.addRow("项目名称：", self._name)
        form.addRow("项目路径：", self._path)
        form.addRow("PCB 名称：", self._pcb)
        form.addRow("默认区域：", self._region)
        self._body_layout.addLayout(form)

        create_btn = QPushButton("创建", self)
        create_btn.setObjectName("projectDialogPrimaryButton")
        create_btn.setProperty("variant", "primary")
        cancel_btn = QPushButton("取消", self)
        cancel_btn.setObjectName("projectDialogSecondaryButton")
        cancel_btn.setProperty("variant", "secondary")
        self._buttons.addButton(create_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        self._buttons.addButton(cancel_btn, QDialogButtonBox.ButtonRole.RejectRole)
        create_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

    def values(self) -> tuple[str, str, str, str]:
        return (
            self._name.text().strip(),
            self._path.text().strip(),
            self._pcb.text().strip(),
            self._region.text().strip(),
        )


class OpenProjectDialog(_ProjectDialogBase):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("打开项目", parent)
        self._selected_name = ""

        hint = QLabel("选择一个 Mock 项目（不读取真实文件）：", self)
        hint.setObjectName("projectDialogHint")
        self._body_layout.addWidget(hint)

        self._list = QListWidget(self)
        self._list.setObjectName("projectDialogList")
        for item in project_mock.get_recent_projects():
            text = f"{item['name']}\n{item['path']}"
            self._list.addItem(QListWidgetItem(text))
        self._list.setCurrentRow(0)
        self._body_layout.addWidget(self._list)

        open_btn = QPushButton("打开", self)
        open_btn.setObjectName("projectDialogPrimaryButton")
        open_btn.setProperty("variant", "primary")
        cancel_btn = QPushButton("取消", self)
        cancel_btn.setObjectName("projectDialogSecondaryButton")
        cancel_btn.setProperty("variant", "secondary")
        self._buttons.addButton(open_btn, QDialogButtonBox.ButtonRole.AcceptRole)
        self._buttons.addButton(cancel_btn, QDialogButtonBox.ButtonRole.RejectRole)
        open_btn.clicked.connect(self._accept_selection)
        cancel_btn.clicked.connect(self.reject)
        self._list.itemDoubleClicked.connect(lambda _: self._accept_selection())

    def _accept_selection(self) -> None:
        row = self._list.currentRow()
        projects = project_mock.get_recent_projects()
        if 0 <= row < len(projects):
            self._selected_name = projects[row]["name"]
            self.accept()

    def selected_project_name(self) -> str:
        return self._selected_name
