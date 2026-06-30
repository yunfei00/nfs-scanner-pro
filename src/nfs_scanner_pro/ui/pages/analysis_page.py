"""分析页 — PCB + 热力图 + 光标 Mock（Release 014）。"""

from __future__ import annotations

from PySide6.QtCore import Signal

from nfs_scanner_pro.ui import mock_data
from nfs_scanner_pro.ui.analysis_mock import AnalysisMock
from nfs_scanner_pro.ui.scan_canvas_view import PcbCanvasWidget, REGION_H, REGION_W, REGION_X, REGION_Y


class AnalysisPage(PcbCanvasWidget):
    analysis_status_updated = Signal(str, str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(
            object_name="analysisPage",
            breadcrumb=mock_data.BREADCRUMB_ANALYSIS,
            show_minimap=True,
            show_handles=False,
            overlay_mode="cursor",
            show_crosshair=True,
            parent=parent,
        )
        self._mock = AnalysisMock(self)
        self._control_panel = None
        self._grid_visible = True

        self._mock.display_changed.connect(self._apply_display)
        self._mock.cursor_changed.connect(self._on_cursor_changed)
        self._mock.status_message.connect(self.analysis_status_updated.emit)
        self._apply_display(self._mock.params)
        c = self._mock.cursor
        self._on_cursor_changed(c)

    def bind_control_panel(self, panel) -> None:
        self._control_panel = panel
        panel.params_changed.connect(self._on_panel_params)
        panel.export_requested.connect(self._mock.start_export)
        panel.cursor_lock_changed.connect(self._on_cursor_lock)
        panel.cursor_copy_requested.connect(self._on_copy_cursor)

    def toggle_grid(self) -> bool:
        self._grid_visible = not self._grid_visible
        self._view.set_grid_visible(self._grid_visible)
        return self._grid_visible

    def _on_panel_params(self, params: dict) -> None:
        self._mock.apply_params(**params)

    def _apply_display(self, params) -> None:
        self._view.set_heatmap_opacity(self._mock.heatmap_opacity())
        self._color_scale.set_title(self._mock.color_scale_title())

    def _on_cursor_changed(self, data: dict) -> None:
        self.update_cursor_readout(
            data["x"],
            data["y"],
            data["z"],
            data["frequency"],
            data["amp"],
            data["phase"],
        )
        if self._control_panel is not None:
            self._control_panel.update_cursor_panel(data)
        sx = REGION_X + (data["x"] - 10.0) / 180.0 * REGION_W
        sy = REGION_Y + (data["y"] + 150.0) / 140.0 * REGION_H
        self._view.set_crosshair_position(sx, sy)

    def _on_cursor_lock(self, locked: bool) -> None:
        self._mock.set_cursor_locked(locked)
        if self._control_panel is not None:
            self._control_panel.set_cursor_locked(locked)
        msg = "Mock：光标已锁定" if locked else "Mock：光标已解锁"
        self.analysis_status_updated.emit(
            msg,
            self._mock._status_extra1(),
            self._mock._status_extra2(),
        )

    def _on_copy_cursor(self) -> None:
        text = self._mock.copy_cursor_readout()
        print(f"[Mock UI] 复制读数：{text}", flush=True)
        self.analysis_status_updated.emit(
            "Mock：读数已复制",
            self._mock._status_extra1(),
            self._mock._status_extra2(),
        )

    def _on_mouse_moved(self, sx: float, sy: float) -> None:
        rel_x = (sx - REGION_X) / REGION_W if REGION_W else 0
        rel_y = (sy - REGION_Y) / REGION_H if REGION_H else 0
        x = 10.0 + rel_x * 180.0
        y = -150.0 + rel_y * 140.0
        self._mock.update_cursor_position(x, y)
        self._view.set_crosshair_position(sx, sy)
