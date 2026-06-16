from __future__ import annotations

import threading
import time
from typing import Callable


ClapCallback = Callable[[], None]
StatusCallback = Callable[[str], None]
ErrorCallback = Callable[[str], None]
LevelCallback = Callable[[float], None]


class ClapDetector:
    """Detects a clap-like volume spike with a simple local RMS threshold."""

    def __init__(
        self,
        config: dict,
        on_clap: ClapCallback,
        on_status: StatusCallback,
        on_error: ErrorCallback | None = None,
        on_level: LevelCallback | None = None,
    ) -> None:
        self.enabled = bool(config.get("enabled", True))
        self.threshold = float(config.get("threshold", 0.65))
        self.cooldown_seconds = float(config.get("cooldown_seconds", 1.2))
        self.sample_rate = int(config.get("sample_rate", 44100))
        self.block_size = int(config.get("block_size", 1024))
        self.on_clap = on_clap
        self.on_status = on_status
        self.on_error = on_error
        self.on_level = on_level
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._last_detected_at = 0.0

    def start(self) -> None:
        if not self.enabled:
            self.on_status("disabled")
            return
        self.on_status("starting")
        self._thread = threading.Thread(target=self._run, name="clap-detector", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    @staticmethod
    def _classify_error(exc: Exception) -> str:
        msg = str(exc).lower()
        if "numpy" in msg and ("importerror" in msg or "modulenotfound" in msg):
            return "numpy not installed"
        if "sounddevice" in msg and ("importerror" in msg or "modulenotfound" in msg):
            return "sounddevice not installed"
        if "device" in msg and ("not found" in msg or "unavailable" in msg):
            return "microphone not available"
        if "device" in msg and ("busy" in msg or "permission" in msg or "denied" in msg):
            return "device busy or no permission"
        return f"{type(exc).__name__}: {str(exc)[:50]}"

    def _run(self) -> None:
        try:
            import numpy as np
            import sounddevice as sd
        except Exception as exc:  # noqa: BLE001
            error_msg = self._classify_error(exc)
            self.on_status("error")
            if self.on_error:
                self.on_error(error_msg)
            return

        try:
            def callback(indata, frames, time_info, status) -> None:  # noqa: ARG001
                if status:
                    self.on_status(f"audio warning: {status}")
                rms = float(np.sqrt(np.mean(np.square(indata))))
                if self.on_level:
                    self.on_level(rms)
                now = time.monotonic()
                if rms >= self.threshold and now - self._last_detected_at >= self.cooldown_seconds:
                    self._last_detected_at = now
                    self.on_clap()

            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                channels=1,
                dtype="float32",
                callback=callback,
            ):
                self.on_status("listening")
                while not self._stop_event.is_set():
                    time.sleep(0.1)
        except Exception as exc:  # noqa: BLE001
            error_msg = self._classify_error(exc)
            self.on_status("error")
            if self.on_error:
                self.on_error(error_msg)
