#!/usr/bin/env python3
"""Release_029 自动验收 — Device Page UI Interaction Verification。"""

from __future__ import annotations

import compileall
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from verification_utils import (  # noqa: E402
    DOCK_TITLES,
    FORBIDDEN_PATTERNS,
    MOCK_DEVICE_DIRS,
    REPORT_TOOLBAR,
    ROOT,
    SCAN_TOOLBAR,
    CheckResult,
    setup_offscreen,
    setup_path,
    toolbar_texts,
)

DEVICE_IMPORTS = (
    "nfs_scanner_pro.ui.main_window",
    "nfs_scanner_pro.ui.pages.device_page",
    "nfs_scanner_pro.ui.device_status_bar",
    "nfs_scanner_pro.ui.device_config_dock",
    "nfs_scanner_pro.devices.device_manager_mock",
    "nfs_scanner_pro.devices.motion_mock",
    "nfs_scanner_pro.devices.spectrum_mock",
    "nfs_scanner_pro.devices.camera_mock",
    "nfs_scanner_pro.devices.servo_mock",
)

WORKFLOW_PAGES = (0, 1, 2, 3, 1)


def _status_text(win) -> str:
    return win._status._message.text()


def _collect_text(widget) -> str:
    from PySide6.QtWidgets import QCheckBox, QLabel, QLineEdit, QPushButton

    parts: list[str] = []
    for cls in (QLabel, QLineEdit, QCheckBox, QPushButton):
        for child in widget.findChildren(cls):
            text = child.text()
            if text:
                parts.append(text)
    return " ".join(parts)


def _click_button(parent, *, object_name: str | None = None, text: str | None = None):
    from PySide6.QtWidgets import QPushButton

    if object_name:
        btn = parent.findChild(QPushButton, object_name)
    elif text:
        btn = next(
            (b for b in parent.findChildren(QPushButton) if b.text() == text),
            None,
        )
    else:
        btn = None
    if btn is None:
        raise RuntimeError(f"button not found: {object_name or text!r}")
    btn.click()


def check_compileall_and_imports(check: CheckResult) -> None:
    ok = bool(compileall.compile_dir(str(ROOT / "src" / "nfs_scanner_pro"), quiet=1))
    failed: list[str] = []
    if ok:
        for mod in DEVICE_IMPORTS:
            try:
                __import__(mod)
            except Exception as exc:  # noqa: BLE001
                failed.append(f"{mod}: {exc}")
                ok = False
    check.add("compileall", ok, "; ".join(failed) if failed else "")


class DeviceUiContext:
    def __init__(self) -> None:
        self.app = None
        self.win = None


def boot_mainwindow(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QApplication, QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        ctx.app = QApplication.instance() or QApplication([])
        ctx.win = MainWindow()
        ctx.win.show()
        ctx.app.processEvents()

        docks = ctx.win.findChildren(QDockWidget)
        nav_texts = [btn.text() for btn in ctx.win._nav.findChildren(QToolButton) if btn.text()]
        ok = (
            ctx.win is not None
            and len(docks) == 1
            and ctx.win._right_dock is not None
            and not ctx.win._right_dock.isFloating()
            and "项目" not in nav_texts
        )
        check.add("mainwindow_boot", ok, f"docks={len(docks)}")
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("mainwindow_boot", False, str(exc))
        return False


def navigate_to_device(ctx: DeviceUiContext) -> None:
    from nfs_scanner_pro.ui.main_window import MainWindow

    ctx.win._nav._buttons[MainWindow.PAGE_DEVICE].click()
    ctx.app.processEvents()


def check_device_navigation(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QDockWidget

        from nfs_scanner_pro.ui.main_window import MainWindow

        navigate_to_device(ctx)
        win = ctx.win
        nav_btn = win._nav._buttons[MainWindow.PAGE_DEVICE]
        status = _status_text(win)
        dock_title = win._right_dock.windowTitle() if win._right_dock else ""

        ok = (
            win._current_page == MainWindow.PAGE_DEVICE
            and win._page_stack.currentIndex() == MainWindow.PAGE_DEVICE
            and nav_btn.isChecked()
            and dock_title == "设备配置"
            and len(win.findChildren(QDockWidget)) == 1
            and ("设备就绪" in status or "设备" in status)
        )
        check.add(
            "device_navigation",
            ok,
            f"dock={dock_title!r} status={status!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("device_navigation", False, str(exc))
        return False


def check_device_config_dock(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QGroupBox

        navigate_to_device(ctx)
        panel = ctx.win._device_panel
        groups = {g.title(): g for g in panel.findChildren(QGroupBox)}
        text = _collect_text(panel)
        required_groups = ("DeviceProfile", "连接策略", "安全限制", "高级")
        required_text = (
            "Lab_Default_v1",
            "COM6 · 115200",
            "ZNA67 · TCP/IP",
            "USB3.0 Camera",
            "HxHy_Default",
            "启动时自动连接",
            "相机可选",
            "设备异常时阻止扫描",
            "X 范围",
            "Y 范围",
            "Z 范围",
            "默认速度",
        )
        ok = all(name in groups for name in required_groups) and all(
            token in text for token in required_text
        )
        check.add(
            "device_config_dock",
            ok,
            f"groups={list(groups.keys())}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("device_config_dock", False, str(exc))
        return False


def check_device_manager_mock(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        from nfs_scanner_pro.devices.device_manager_mock import DeviceManagerMock

        manager = DeviceManagerMock()
        connect_msg = manager.connect_all()
        status_rows = manager.get_device_status()
        snapshot = manager.get_snapshot()
        names = {row["name"] for row in status_rows}

        ok = (
            "Mock" in connect_msg
            and {"motion", "spectrum", "camera", "servo"} <= set(snapshot.keys())
            and "运动平台" in names
            and "频谱仪" in names
            and "相机" in names
            and "舵机系统" in names
            and manager.is_all_ready()
        )
        check.add(
            "device_manager_mock",
            ok,
            f"ready={manager.is_all_ready()} keys={list(snapshot.keys())}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("device_manager_mock", False, str(exc))
        return False


def check_device_status_bar(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        bar = ctx.win._device_bar
        bar.refresh_from_manager()
        ctx.app.processEvents()

        labels = bar._device_labels
        texts = [label.text() for label in labels]
        combined = " ".join(texts)
        required = (
            "运动平台",
            "COM6",
            "频谱仪",
            "ZNA67",
            "相机",
            "USB3.0",
            "舵机",
        )
        status_ok = all(label.property("status") == "connected" for label in labels)
        text_ok = all(token in combined for token in required)
        layout_ok = all(not label.wordWrap() for label in labels) and "项目" not in combined

        ok = text_ok and status_ok and layout_ok
        check.add(
            "device_status_bar",
            ok,
            combined,
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("device_status_bar", False, str(exc))
        return False


def check_motion_card_ui(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        card = ctx.win._device_page._motion_card
        text = _collect_text(card)
        required = (
            "运动平台",
            "COM6",
            "115200",
            "当前坐标",
            "回零",
            "停止",
            "刷新位置",
            "X+",
            "X-",
            "Y+",
            "Y-",
            "Z+",
            "Z-",
        )
        ok = all(token in text for token in required) and "X" in text and "Y" in text and "Z" in text
        check.add("motion_card_ui", ok, f"card={card.objectName()}")
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("motion_card_ui", False, str(exc))
        return False


def check_motion_actions(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        win = ctx.win
        page = win._device_page
        motion = page._manager.motion
        card = page._motion_card

        x0, y0, z0 = motion.x, motion.y, motion.z
        statuses: list[str] = []
        jog_checks: list[bool] = []

        for obj_name in ("motionHomeButton", "motionStopButton", "motionRefreshButton"):
            _click_button(card, object_name=obj_name)
            ctx.app.processEvents()
            statuses.append(_status_text(win))

        _click_button(card, object_name="jogXPlus")
        ctx.app.processEvents()
        jog_checks.append(abs(motion.x - (x0 + 1.0)) < 0.01)
        statuses.append(_status_text(win))

        _click_button(card, object_name="jogXMinus")
        ctx.app.processEvents()
        jog_checks.append(abs(motion.x - x0) < 0.01)
        statuses.append(_status_text(win))

        _click_button(card, object_name="jogYPlus")
        ctx.app.processEvents()
        jog_checks.append(abs(motion.y - (y0 + 1.0)) < 0.01)
        statuses.append(_status_text(win))

        _click_button(card, object_name="jogYMinus")
        ctx.app.processEvents()
        jog_checks.append(abs(motion.y - y0) < 0.01)
        statuses.append(_status_text(win))

        _click_button(card, object_name="jogZPlus")
        ctx.app.processEvents()
        jog_checks.append(abs(motion.z - (z0 + 0.1)) < 0.01)
        statuses.append(_status_text(win))

        _click_button(card, object_name="jogZMinus")
        ctx.app.processEvents()
        jog_checks.append(abs(motion.z - z0) < 0.01)
        statuses.append(_status_text(win))

        mock_ok = all("Mock" in s for s in statuses)
        ok = mock_ok and all(jog_checks)
        check.add(
            "motion_actions",
            ok,
            f"pos=({motion.x:.2f},{motion.y:.2f},{motion.z:.2f}) jogs={jog_checks}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("motion_actions", False, str(exc))
        return False


def check_spectrum_card_ui(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        card = ctx.win.findChild(type(ctx.win._device_page._motion_card), "deviceCardSpectrum")
        text = _collect_text(card)
        required = (
            "频谱仪",
            "ZNA67",
            "TCP/IP",
            "192.168.1.100:5025",
            "Trace 1",
            "1 MHz — 67 GHz",
            "2.450 GHz",
            "测试连接",
            "单次 Sweep",
            "读取 Trace",
        )
        ok = all(token in text for token in required)
        check.add("spectrum_card_ui", ok, card.objectName())
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("spectrum_card_ui", False, str(exc))
        return False


def check_spectrum_actions(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        win = ctx.win
        card = win.findChild(type(win._device_page._motion_card), "deviceCardSpectrum")
        spectrum = win._device_page._manager.spectrum
        statuses: list[str] = []
        for obj_name in (
            "spectrumTestButton",
            "spectrumSweepButton",
            "spectrumReadTraceButton",
        ):
            _click_button(card, object_name=obj_name)
            ctx.app.processEvents()
            statuses.append(_status_text(win))

        ok = (
            all("Mock" in s for s in statuses)
            and spectrum.is_connected()
            and spectrum.trace == "Trace 1"
        )
        check.add("spectrum_actions", ok, "; ".join(statuses))
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("spectrum_actions", False, str(exc))
        return False


def check_camera_card_ui(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        from nfs_scanner_pro.ui.widgets.camera_preview_mock import CameraPreviewMock

        navigate_to_device(ctx)
        card = ctx.win.findChild(type(ctx.win._device_page._motion_card), "deviceCardCamera")
        preview = card.findChild(CameraPreviewMock)
        text = _collect_text(card)
        required = (
            "相机",
            "USB3.0",
            "4096 × 3000",
            "预览就绪",
            "拍照",
            "刷新预览",
            "打开相机设置",
        )
        preview_ok = preview is not None and "预览" in _collect_text(preview)
        ok = all(token in text for token in required) and preview_ok
        check.add("camera_card_ui", ok, card.objectName())
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("camera_card_ui", False, str(exc))
        return False


def check_camera_actions(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        win = ctx.win
        card = win.findChild(type(win._device_page._motion_card), "deviceCardCamera")
        camera = win._device_page._manager.camera
        statuses: list[str] = []
        for obj_name in (
            "cameraCaptureButton",
            "cameraRefreshButton",
            "cameraSettingsButton",
        ):
            _click_button(card, object_name=obj_name)
            ctx.app.processEvents()
            statuses.append(_status_text(win))

        ok = all("Mock" in s for s in statuses) and camera.is_connected()
        check.add("camera_actions", ok, "; ".join(statuses))
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("camera_actions", False, str(exc))
        return False


def check_servo_card_ui(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        card = ctx.win.findChild(type(ctx.win._device_page._motion_card), "deviceCardServo")
        hxhy = ctx.win._device_page._hxhy
        text = _collect_text(card) + " " + _collect_text(hxhy)
        required = (
            "舵机系统",
            "当前探头",
            "Hx",
            "Hy",
            "待命",
            "旋转角度",
            "偏移补偿",
            "校准状态",
            "切换到 Hx",
            "切换到 Hy",
            "Hx/Hy 校准",
            "应用偏移补偿",
        )
        ok = all(token in text for token in required)
        check.add("servo_card_ui", ok, card.objectName())
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("servo_card_ui", False, str(exc))
        return False


def check_servo_actions(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        navigate_to_device(ctx)
        win = ctx.win
        hxhy = win._device_page._hxhy
        servo = win._device_page._manager.servo
        statuses: list[str] = []
        for obj_name in (
            "servoSwitchHxButton",
            "servoSwitchHyButton",
            "servoCalibrateButton",
            "servoApplyOffsetButton",
        ):
            _click_button(hxhy, object_name=obj_name)
            ctx.app.processEvents()
            statuses.append(_status_text(win))

        ok = (
            all("Mock" in s for s in statuses)
            and servo.current_probe == "Hy"
            and hxhy.current_probe == "Hy"
        )
        check.add(
            "servo_actions",
            ok,
            f"probe={servo.current_probe} status={statuses[-1]!r}",
        )
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("servo_actions", False, str(exc))
        return False


def check_page_switch_regression(check: CheckResult, ctx: DeviceUiContext) -> bool:
    try:
        from PySide6.QtWidgets import QDockWidget, QToolButton

        from nfs_scanner_pro.ui.main_window import MainWindow

        win = ctx.win
        ok = True
        details: list[str] = []
        for page_index in WORKFLOW_PAGES:
            win._switch_page(page_index)
            ctx.app.processEvents()
            expected = DOCK_TITLES[page_index]
            actual = win._right_dock.windowTitle() if win._right_dock else ""
            docks = win.findChildren(QDockWidget)
            nav_texts = [btn.text() for btn in win._nav.findChildren(QToolButton) if btn.text()]
            page_ok = (
                win._page_stack.currentIndex() == page_index
                and actual == expected
                and len(docks) == 1
                and not win._right_dock.isFloating()
                and "项目" not in nav_texts
            )
            if page_index == MainWindow.PAGE_REPORT:
                page_ok = page_ok and all(t in toolbar_texts(win) for t in REPORT_TOOLBAR)
            if page_index == MainWindow.PAGE_SCAN:
                page_ok = page_ok and all(t in toolbar_texts(win) for t in SCAN_TOOLBAR)
            if not page_ok:
                ok = False
            details.append(f"{page_index}:{actual!r}")
        win.close()
        check.add("page_switch_regression", ok, ", ".join(details))
        return ok
    except Exception as exc:  # noqa: BLE001
        check.add("page_switch_regression", False, str(exc))
        return False


def check_no_real_device_access(check: CheckResult) -> None:
    hits: list[str] = []
    for base in MOCK_DEVICE_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            for pattern in FORBIDDEN_PATTERNS:
                if pattern in text:
                    hits.append(f"{path.relative_to(ROOT)}: {pattern}")
    check.add("no_real_device_access", not hits, "; ".join(hits))


def write_acceptance_report(check: CheckResult) -> Path:
    report_path = (
        ROOT
        / "docs/product-spec/release/Release_029_Device_Page_UI_Interaction_Verification/ACCEPTANCE_REPORT.md"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Release_029 验收报告",
        "",
        "## 执行时间",
        "",
        now,
        "",
        "## 执行命令",
        "",
        "```bash",
        "python scripts/verify_release_029.py",
        "python scripts/verify_all.py",
        "```",
        "",
        "## 检查项",
        "",
    ]
    for name, ok, detail in check.results:
        status = "PASS" if ok else "FAIL"
        suffix = f" — {detail}" if detail else ""
        lines.append(f"- [{status}] `{name}`{suffix}")
    lines.extend(
        [
            "",
            "## 结果",
            "",
            "PASS" if check.passed else "FAIL",
            "",
            "## 是否接真实设备",
            "",
            "否",
            "",
            "## 是否打开串口",
            "",
            "否",
            "",
            "## 是否发送 SCPI",
            "",
            "否",
            "",
            "## 是否访问真实相机",
            "",
            "否",
            "",
            "## 是否控制真实舵机",
            "",
            "否",
            "",
            "## 是否修改 high_fidelity HTML",
            "",
            "否",
            "",
            "## 是否可以提交",
            "",
            "是" if check.passed else "否",
            "",
        ]
    )
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def main() -> int:
    setup_offscreen()
    setup_path()
    check = CheckResult("Release_029 Verification")
    ctx = DeviceUiContext()

    check_compileall_and_imports(check)
    if boot_mainwindow(check, ctx):
        check_device_navigation(check, ctx)
        check_device_config_dock(check, ctx)
        check_device_manager_mock(check, ctx)
        check_device_status_bar(check, ctx)
        check_motion_card_ui(check, ctx)
        check_motion_actions(check, ctx)
        check_spectrum_card_ui(check, ctx)
        check_spectrum_actions(check, ctx)
        check_camera_card_ui(check, ctx)
        check_camera_actions(check, ctx)
        check_servo_card_ui(check, ctx)
        check_servo_actions(check, ctx)
        check_page_switch_regression(check, ctx)
    check_no_real_device_access(check)

    report_path = write_acceptance_report(check)
    check.print_report()
    print(f"\nAcceptance report: {report_path.relative_to(ROOT)}")
    return 0 if check.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
