from __future__ import annotations

from pathlib import Path

import cv2

from src.audio.clap_detector import ClapDetector
from src.audio.voice_listener import VoiceListener
from src.camera.camera_service import CameraService
from src.control.mouse_controller import MouseController
from src.control.system_actions import SystemActions
from src.core.app_state import AppState
from src.core.config_loader import load_config
from src.ui.overlay_renderer import OverlayRenderer
from src.vision.gesture_detector import GestureDetector
from src.vision.hand_tracker import HandTracker


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    config = load_config(project_root / "config" / "settings.yaml")
    voice_model_path = Path(str(config["voice"].get("model_path", "")))
    if voice_model_path and not voice_model_path.is_absolute():
        config["voice"]["model_path"] = str(project_root / voice_model_path)

    app_state = AppState()
    actions = SystemActions()

    def handle_voice_command(command: str, raw_text: str) -> None:
        app_state.set_last_voice_command(raw_text)
        app_state.set_last_command(f"voice: {raw_text}")
        if command == "activate":
            app_state.set_active(True, "voice")
        elif command == "deactivate":
            app_state.set_active(False, "voice")
        elif command == "open_browser":
            app_state.set_last_command("voice: abrir navegador")
            if not actions.open_default_browser():
                app_state.set_voice_error("browser open failed")
        elif command == "exit":
            app_state.request_exit("voice")

    def handle_clap() -> None:
        cooldown = float(config["clap"].get("cooldown_seconds", 1.2))
        if app_state.can_accept_clap(cooldown):
            app_state.toggle_active("clap")

    voice_listener = VoiceListener(
        config["voice"],
        on_command=handle_voice_command,
        on_status=app_state.set_voice_status,
        on_error=app_state.set_voice_error,
    )
    clap_detector = ClapDetector(
        config["clap"],
        on_clap=handle_clap,
        on_status=app_state.set_clap_status,
        on_error=app_state.set_clap_error,
        on_level=app_state.set_last_clap_level,
    )

    camera = CameraService(config["camera"])
    tracker = HandTracker(config["vision"])
    gesture_detector = GestureDetector()
    mouse = MouseController(config["mouse"])
    renderer = OverlayRenderer(config["ui"])

    camera.open()
    voice_listener.start()
    clap_detector.start()

    window_title = str(config["ui"].get("window_title", "RV Camera Controller"))
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                app_state.set_last_command("camera: frame unavailable")
                break

            tracking = tracker.process(frame)
            gesture = gesture_detector.detect(tracking.hand_landmarks)
            stable_gesture = app_state.observe_gesture(
                gesture,
                hold_seconds=float(config["vision"].get("gesture_hold_seconds", 0.7)),
            )

            if stable_gesture == "open":
                app_state.set_active(True, "gesture")
            elif stable_gesture == "closed":
                app_state.set_active(False, "gesture")
                mouse.reset()

            snapshot = app_state.snapshot()
            if snapshot["active"] and tracking.has_hand:
                pointer_index = int(config["vision"].get("pointer_landmark", 8))
                pointer = tracking.hand_landmarks.landmark[pointer_index]
                mouse.move_from_normalized(pointer.x, pointer.y)
            elif not snapshot["active"]:
                mouse.reset()

            renderer.draw(frame, tracking, app_state.snapshot())
            cv2.imshow(window_title, frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                app_state.request_exit("keyboard")

            snapshot = app_state.snapshot()
            if snapshot["should_exit"] or snapshot["shutdown_requested"]:
                break
    finally:
        voice_listener.stop()
        clap_detector.stop()
        tracker.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
