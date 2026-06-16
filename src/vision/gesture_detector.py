from __future__ import annotations

from math import hypot
from typing import Any


class GestureDetector:
    """Classifies a single hand as open, closed or unknown from MediaPipe landmarks."""

    WRIST = 0
    FINGERS = {
        "thumb": (2, 3, 4),
        "index": (5, 6, 8),
        "middle": (9, 10, 12),
        "ring": (13, 14, 16),
        "pinky": (17, 18, 20),
    }

    def detect(self, hand_landmarks: Any | None) -> str:
        if hand_landmarks is None:
            return "none"

        landmarks = hand_landmarks.landmark
        wrist = landmarks[self.WRIST]
        extended = 0

        for name, (mcp_index, pip_index, tip_index) in self.FINGERS.items():
            mcp = landmarks[mcp_index]
            pip = landmarks[pip_index]
            tip = landmarks[tip_index]

            if name == "thumb":
                if self._distance(tip, wrist) > self._distance(pip, wrist) * 1.08:
                    extended += 1
                continue

            if self._distance(tip, wrist) > self._distance(pip, wrist) * 1.12 and tip.y < mcp.y + 0.08:
                extended += 1

        if extended >= 4:
            return "open"
        if extended <= 1:
            return "closed"
        return "unknown"

    @staticmethod
    def _distance(a: Any, b: Any) -> float:
        return hypot(a.x - b.x, a.y - b.y)
