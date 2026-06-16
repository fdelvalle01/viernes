from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AppState:
    """Thread-safe state shared by the camera loop and optional audio threads."""

    active: bool = False
    last_gesture: str = "none"
    last_command: str = "none"
    voice_status: str = "disabled"
    voice_error: str = ""
    last_voice_command: str = "none"
    clap_status: str = "disabled"
    clap_error: str = ""
    last_clap_level: float = 0.0
    last_clap_at: float = 0.0
    should_exit: bool = False
    shutdown_requested: bool = False
    last_state_change_at: float = field(default_factory=time.monotonic)
    _gesture_candidate: str | None = None
    _gesture_candidate_since: float = 0.0
    _gesture_latched: bool = False
    _lock: threading.RLock = field(default_factory=threading.RLock, init=False, repr=False)

    def set_active(self, active: bool, source: str) -> None:
        with self._lock:
            if self.active != active:
                self.active = active
                self.last_state_change_at = time.monotonic()
            self.last_command = f"{source}: {'ACTIVE' if active else 'INACTIVE'}"

    def toggle_active(self, source: str) -> None:
        with self._lock:
            self.active = not self.active
            self.last_state_change_at = time.monotonic()
            self.last_command = f"{source}: {'ACTIVE' if self.active else 'INACTIVE'}"

    def set_last_command(self, command: str) -> None:
        with self._lock:
            self.last_command = command

    def set_voice_status(self, status: str) -> None:
        with self._lock:
            self.voice_status = status

    def set_voice_error(self, error: str) -> None:
        with self._lock:
            self.voice_error = error

    def set_last_voice_command(self, command: str) -> None:
        with self._lock:
            self.last_voice_command = command

    def set_clap_status(self, status: str) -> None:
        with self._lock:
            self.clap_status = status

    def set_clap_error(self, error: str) -> None:
        with self._lock:
            self.clap_error = error

    def set_last_clap_level(self, level: float) -> None:
        with self._lock:
            self.last_clap_level = level

    def request_shutdown(self, source: str) -> None:
        with self._lock:
            self.shutdown_requested = True
            self.last_command = f"{source}: shutdown"

    def request_exit(self, source: str) -> None:
        with self._lock:
            self.should_exit = True
            self.shutdown_requested = True
            self.last_command = f"{source}: salir"

    def observe_gesture(self, gesture: str, hold_seconds: float) -> str | None:
        """Return a stable gesture once it has been held long enough."""
        now = time.monotonic()
        with self._lock:
            self.last_gesture = gesture
            if gesture not in {"open", "closed"}:
                self._gesture_candidate = None
                self._gesture_candidate_since = 0.0
                self._gesture_latched = False
                return None

            if gesture != self._gesture_candidate:
                self._gesture_candidate = gesture
                self._gesture_candidate_since = now
                self._gesture_latched = False
                return None

            if not self._gesture_latched and now - self._gesture_candidate_since >= hold_seconds:
                self._gesture_latched = True
                return gesture

            return None

    def can_accept_clap(self, cooldown_seconds: float) -> bool:
        now = time.monotonic()
        with self._lock:
            if now - self.last_clap_at < cooldown_seconds:
                return False
            self.last_clap_at = now
            return True

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "active": self.active,
                "last_gesture": self.last_gesture,
                "last_command": self.last_command,
                "voice_status": self.voice_status,
                "voice_error": self.voice_error,
                "last_voice_command": self.last_voice_command,
                "clap_status": self.clap_status,
                "clap_error": self.clap_error,
                "last_clap_level": self.last_clap_level,
                "last_clap_at": self.last_clap_at,
                "should_exit": self.should_exit,
                "shutdown_requested": self.shutdown_requested,
            }
