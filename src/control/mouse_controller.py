from __future__ import annotations

import time
from dataclasses import dataclass

import pyautogui


@dataclass
class Point:
    x: float
    y: float


class MouseController:
    def __init__(self, config: dict) -> None:
        pyautogui.FAILSAFE = True
        self.enabled = bool(config.get("enabled", True))
        self.smoothing = self._clamp(float(config.get("smoothing", 0.25)), 0.01, 1.0)
        self.max_step_pixels = int(config.get("max_step_pixels", 85))
        self.margin = self._clamp(float(config.get("movement_margin", 0.08)), 0.0, 0.35)
        self.update_interval_seconds = float(config.get("update_interval_seconds", 0.015))
        self.screen_width, self.screen_height = pyautogui.size()
        self._last_position: Point | None = None
        self._last_move_at = 0.0

    def move_from_normalized(self, x: float, y: float) -> None:
        if not self.enabled:
            return

        now = time.monotonic()
        if now - self._last_move_at < self.update_interval_seconds:
            return
        self._last_move_at = now

        target = self._map_to_screen(x, y)
        if self._last_position is None:
            self._last_position = target

        smooth = Point(
            x=self._last_position.x + (target.x - self._last_position.x) * self.smoothing,
            y=self._last_position.y + (target.y - self._last_position.y) * self.smoothing,
        )
        limited = self._limit_step(self._last_position, smooth)
        self._last_position = limited
        pyautogui.moveTo(int(limited.x), int(limited.y), duration=0)

    def reset(self) -> None:
        self._last_position = None

    def _map_to_screen(self, x: float, y: float) -> Point:
        x = self._normalize_with_margin(x)
        y = self._normalize_with_margin(y)
        return Point(x=x * (self.screen_width - 1), y=y * (self.screen_height - 1))

    def _normalize_with_margin(self, value: float) -> float:
        if self.margin <= 0:
            return self._clamp(value, 0.0, 1.0)
        scaled = (value - self.margin) / (1.0 - self.margin * 2.0)
        return self._clamp(scaled, 0.0, 1.0)

    def _limit_step(self, previous: Point, target: Point) -> Point:
        dx = target.x - previous.x
        dy = target.y - previous.y
        if abs(dx) <= self.max_step_pixels and abs(dy) <= self.max_step_pixels:
            return target
        return Point(
            x=previous.x + self._clamp(dx, -self.max_step_pixels, self.max_step_pixels),
            y=previous.y + self._clamp(dy, -self.max_step_pixels, self.max_step_pixels),
        )

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, value))
