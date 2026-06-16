from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import cv2
import mediapipe as mp


@dataclass
class HandTrackingResult:
    hand_landmarks: Any | None
    handedness: Any | None
    raw_result: Any

    @property
    def has_hand(self) -> bool:
        return self.hand_landmarks is not None


class HandTracker:
    def __init__(self, config: dict) -> None:
        self._mp_hands = mp.solutions.hands
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=int(config.get("max_num_hands", 1)),
            min_detection_confidence=float(config.get("min_detection_confidence", 0.65)),
            min_tracking_confidence=float(config.get("min_tracking_confidence", 0.55)),
        )

    def process(self, frame) -> HandTrackingResult:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        result = self._hands.process(rgb_frame)
        hand_landmarks = result.multi_hand_landmarks[0] if result.multi_hand_landmarks else None
        handedness = result.multi_handedness[0] if result.multi_handedness else None
        return HandTrackingResult(hand_landmarks=hand_landmarks, handedness=handedness, raw_result=result)

    def close(self) -> None:
        self._hands.close()
