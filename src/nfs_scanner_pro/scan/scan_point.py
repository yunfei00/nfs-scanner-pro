"""扫描点 Mock — Release 019。"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass
class ScanPointMock:
    index: int
    x: float
    y: float
    z: float
    frequency: str
    amplitude: float
    phase: float
    timestamp: str = ""

    @classmethod
    def build(
        cls,
        index: int,
        x: float,
        y: float,
        z: float,
        frequency: str,
        *,
        timestamp: str = "",
    ) -> ScanPointMock:
        amp = -23.45 + math.sin(index * 0.07) * 1.8 + random.uniform(-0.8, 0.8)
        phase = 112.3 + math.cos(index * 0.05) * 12.0 + random.uniform(-3.0, 3.0)
        return cls(
            index=index,
            x=x,
            y=y,
            z=z,
            frequency=frequency,
            amplitude=amp,
            phase=phase,
            timestamp=timestamp,
        )
