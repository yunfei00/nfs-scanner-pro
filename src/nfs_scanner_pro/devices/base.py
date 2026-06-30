"""设备 Mock 基类 — Release 018。"""

from __future__ import annotations

from typing import Any, Callable

from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.device_types import DeviceType, device_type_label

StateChangedCallback = Callable[[DeviceState], None]
MessageCallback = Callable[[str], None]


class BaseDeviceMock:
    def __init__(self, device_type: DeviceType, *, name: str | None = None) -> None:
        self.device_type = device_type
        self.name = name or device_type_label(device_type)
        self.state = DeviceState.CONNECTED
        self.last_error = ""
        self.profile: dict[str, Any] = {}
        self._state_callbacks: list[StateChangedCallback] = []
        self._message_callbacks: list[MessageCallback] = []

    def add_state_listener(self, callback: StateChangedCallback) -> None:
        self._state_callbacks.append(callback)

    def add_message_listener(self, callback: MessageCallback) -> None:
        self._message_callbacks.append(callback)

    def connect(self) -> str:
        self._set_state(DeviceState.CONNECTING)
        self._set_state(DeviceState.CONNECTED)
        message = f"Mock：{self.name}已连接"
        self._emit_message(message)
        return message

    def disconnect(self) -> str:
        self._set_state(DeviceState.DISCONNECTED)
        message = f"Mock：{self.name}已断开"
        self._emit_message(message)
        return message

    def reset(self) -> str:
        self.last_error = ""
        self._set_state(DeviceState.CONNECTED)
        message = f"Mock：{self.name}已重置"
        self._emit_message(message)
        return message

    def snapshot(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "device_type": self.device_type.value,
            "state": self.state.value,
            "last_error": self.last_error,
            "profile": dict(self.profile),
        }

    def is_connected(self) -> bool:
        return self.state in (DeviceState.CONNECTED, DeviceState.BUSY)

    def status_text(self) -> str:
        return self.state.value

    def _set_state(self, state: DeviceState) -> None:
        self.state = state
        for callback in self._state_callbacks:
            callback(state)

    def _emit_message(self, message: str) -> None:
        for callback in self._message_callbacks:
            callback(message)

    def _fail(self, error: str) -> str:
        self.last_error = error
        self._set_state(DeviceState.ERROR)
        message = f"Mock：{self.name}错误 — {error}"
        self._emit_message(message)
        return message
