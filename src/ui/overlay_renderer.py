from __future__ import annotations

from typing import Any

import cv2
import mediapipe as mp


class OverlayRenderer:
    def __init__(self, config: dict) -> None:
        self.window_title = str(config.get("window_title", "RV Camera Controller"))
        self.show_audio_status = bool(config.get("show_audio_status", True))
        self._drawing_utils = mp.solutions.drawing_utils
        self._drawing_styles = mp.solutions.drawing_styles
        self._hands = mp.solutions.hands

    def draw(self, frame, tracking_result: Any, state_snapshot: dict) -> None:
        if tracking_result and tracking_result.hand_landmarks:
            self._drawing_utils.draw_landmarks(
                frame,
                tracking_result.hand_landmarks,
                self._hands.HAND_CONNECTIONS,
                self._drawing_styles.get_default_hand_landmarks_style(),
                self._drawing_styles.get_default_hand_connections_style(),
            )

        active = bool(state_snapshot.get("active", False))
        status_text = "ACTIVE" if active else "INACTIVE"
        status_color = (40, 220, 80) if active else (60, 60, 255)
        command = str(state_snapshot.get("last_command", "none"))
        gesture = str(state_snapshot.get("last_gesture", "none"))

        show_errors = bool(state_snapshot.get("voice_error")) or bool(state_snapshot.get("clap_error"))
        self._draw_panel(frame, show_errors)
        cv2.putText(frame, f"State: {status_text}", (18, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.85, status_color, 2)
        cv2.putText(frame, f"Gesture: {gesture}", (18, 72), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (245, 245, 245), 2)
        cv2.putText(frame, f"Last command: {command}", (18, 104), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (245, 245, 245), 2)

        if self.show_audio_status:
            voice_status = str(state_snapshot.get("voice_status", "unknown"))
            voice_error = str(state_snapshot.get("voice_error", ""))
            clap_status = str(state_snapshot.get("clap_status", "unknown"))
            clap_error = str(state_snapshot.get("clap_error", ""))
            clap_level = state_snapshot.get("last_clap_level", 0.0)

            voice_color = (80, 80, 255) if voice_error else (210, 210, 210)
            cv2.putText(frame, f"Voice: {voice_status}", (18, 136), cv2.FONT_HERSHEY_SIMPLEX, 0.5, voice_color, 1)
            if voice_error:
                cv2.putText(frame, f"  {voice_error}", (18, 156), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 255), 1)

            clap_color = (80, 80, 255) if clap_error else (210, 210, 210)
            clap_y = 176 if voice_error else 162
            cv2.putText(frame, f"Clap: {clap_status} {clap_level:.2f}", (18, clap_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, clap_color, 1)
            if clap_error:
                cv2.putText(frame, f"  {clap_error}", (18, clap_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (80, 80, 255), 1)

        height = frame.shape[0]
        cv2.putText(frame, "q / esc: exit", (18, height - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 230, 230), 1)

    @staticmethod
    def _draw_panel(frame, show_errors: bool = False) -> None:
        overlay = frame.copy()
        height = 178 if not show_errors else 220
        cv2.rectangle(overlay, (8, 8), (560, height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
