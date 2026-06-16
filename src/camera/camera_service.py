from __future__ import annotations

import cv2


class CameraService:
    def __init__(self, config: dict) -> None:
        self.index = int(config.get("index", 0))
        self.width = int(config.get("width", 1280))
        self.height = int(config.get("height", 720))
        self.fps = int(config.get("fps", 30))
        self.mirror = bool(config.get("mirror", True))
        self.use_dshow = bool(config.get("use_dshow", True))
        self._capture: cv2.VideoCapture | None = None

    def open(self) -> None:
        backend = cv2.CAP_DSHOW if self.use_dshow else cv2.CAP_ANY
        self._capture = cv2.VideoCapture(self.index, backend)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self._capture.set(cv2.CAP_PROP_FPS, self.fps)

        if not self._capture.isOpened():
            raise RuntimeError(f"Could not open camera index {self.index}")

    def read(self):
        if self._capture is None:
            raise RuntimeError("Camera is not open")

        ok, frame = self._capture.read()
        if not ok:
            return False, None

        if self.mirror:
            frame = cv2.flip(frame, 1)

        return True, frame

    def release(self) -> None:
        if self._capture is not None:
            self._capture.release()
            self._capture = None
