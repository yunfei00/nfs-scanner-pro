"""频谱仪 Mock — Release 018。"""

from __future__ import annotations

from typing import Any

from nfs_scanner_pro.devices.base import BaseDeviceMock
from nfs_scanner_pro.devices.device_state import DeviceState
from nfs_scanner_pro.devices.device_types import DeviceType


class SpectrumAnalyzerMock(BaseDeviceMock):
    def __init__(self) -> None:
        super().__init__(DeviceType.SPECTRUM)
        self.model = "ZNA67"
        self.connection = "TCP/IP"
        self.address = "192.168.1.100:5025"
        self.trace = "Trace 1"
        self.freq_range = "1 MHz — 67 GHz"
        self.current_freq = "2.450 GHz"
        self.profile = {
            "model": self.model,
            "connection": self.connection,
            "address": self.address,
        }

    def test_connection(self) -> str:
        self._set_state(DeviceState.BUSY)
        message = "Mock：频谱仪连接测试成功"
        self._emit_message(message)
        self._set_state(DeviceState.CONNECTED)
        return message

    def single_sweep(self) -> str:
        self._set_state(DeviceState.BUSY)
        message = "Mock：单次 Sweep 完成"
        self._emit_message(message)
        self._set_state(DeviceState.CONNECTED)
        return message

    def read_trace(self) -> str:
        message = f"Mock：{self.trace} @ {self.current_freq}（{self.freq_range}）"
        self._emit_message(message)
        return message

    def set_frequency(self, freq: str) -> str:
        self.current_freq = freq
        message = f"Mock：频谱仪频率已设为 {freq}"
        self._emit_message(message)
        return message

    def snapshot(self) -> dict[str, Any]:
        data = super().snapshot()
        data.update(
            {
                "model": self.model,
                "connection": self.connection,
                "address": self.address,
                "trace": self.trace,
                "freq_range": self.freq_range,
                "current_freq": self.current_freq,
            }
        )
        return data
