from __future__ import annotations

import json
import queue
import threading
from pathlib import Path
from typing import Callable


VoiceCommandCallback = Callable[[str, str], None]
StatusCallback = Callable[[str], None]
ErrorCallback = Callable[[str], None]


class VoiceListener:
    """Offline Spanish voice command listener powered by a local Vosk model."""

    def __init__(
        self,
        config: dict,
        on_command: VoiceCommandCallback,
        on_status: StatusCallback,
        on_error: ErrorCallback | None = None,
    ) -> None:
        self.enabled = bool(config.get("enabled", True))
        self.model_path = Path(str(config.get("model_path", "models/vosk-es")))
        self.sample_rate = int(config.get("sample_rate", 16000))
        self.block_size = int(config.get("block_size", 8000))
        self.commands = config.get("commands", {})
        self.on_command = on_command
        self.on_status = on_status
        self.on_error = on_error
        self._audio_queue: queue.Queue[bytes] = queue.Queue()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if not self.enabled:
            self.on_status("disabled")
            return
        if not self.model_path.exists():
            error_msg = f"model not found at {self.model_path}"
            self.on_status("error")
            self.on_error(error_msg)
            return

        self.on_status("starting")
        self._thread = threading.Thread(target=self._run, name="voice-listener", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    @staticmethod
    def _classify_error(exc: Exception) -> str:
        msg = str(exc).lower()
        if "vosk" in msg and ("importerror" in msg or "modulenotfound" in msg):
            return "vosk not installed"
        if "sounddevice" in msg and ("importerror" in msg or "modulenotfound" in msg):
            return "sounddevice not installed"
        if "no such file" in msg or "not found" in msg or "does not exist" in msg:
            return "model not found"
        if "model" in msg and ("load" in msg or "invalid" in msg or "corrupt" in msg):
            return "model load failed"
        if "device" in msg and ("not found" in msg or "unavailable" in msg):
            return "microphone not available"
        if "device" in msg and ("busy" in msg or "permission" in msg or "denied" in msg):
            return "device busy or no permission"
        return f"{type(exc).__name__}: {str(exc)[:50]}"

    def _run(self) -> None:
        try:
            import sounddevice as sd
            from vosk import KaldiRecognizer, Model
        except Exception as exc:  # noqa: BLE001 - optional runtime dependency
            error_msg = self._classify_error(exc)
            self.on_status("error")
            if self.on_error:
                self.on_error(error_msg)
            return

        try:
            model = Model(str(self.model_path))
            recognizer = KaldiRecognizer(model, self.sample_rate)
            recognizer.SetWords(False)

            def callback(indata, frames, time_info, status) -> None:  # noqa: ARG001
                if status:
                    self.on_status(f"audio warning: {status}")
                self._audio_queue.put(bytes(indata))

            with sd.RawInputStream(
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                dtype="int16",
                channels=1,
                callback=callback,
            ):
                self.on_status("listening")
                while not self._stop_event.is_set():
                    try:
                        data = self._audio_queue.get(timeout=0.2)
                    except queue.Empty:
                        continue

                    if recognizer.AcceptWaveform(data):
                        payload = json.loads(recognizer.Result())
                        text = self._normalize(payload.get("text", ""))
                        command = self._match_command(text)
                        if command:
                            self.on_command(command, text)
        except Exception as exc:  # noqa: BLE001 - audio/model failures must not kill the app
            error_msg = self._classify_error(exc)
            self.on_status("error")
            if self.on_error:
                self.on_error(error_msg)

    def _match_command(self, text: str) -> str | None:
        if not text:
            return None
        for command, phrases in self.commands.items():
            for phrase in phrases:
                if self._normalize(str(phrase)) in text:
                    return str(command)
        return None

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.lower().strip().split())
