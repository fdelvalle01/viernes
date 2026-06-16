from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG: dict[str, Any] = {
    "camera": {
        "index": 0,
        "width": 1280,
        "height": 720,
        "fps": 30,
        "mirror": True,
        "use_dshow": True,
    },
    "vision": {
        "max_num_hands": 1,
        "min_detection_confidence": 0.65,
        "min_tracking_confidence": 0.55,
        "gesture_hold_seconds": 0.7,
        "pointer_landmark": 8,
    },
    "mouse": {
        "enabled": True,
        "smoothing": 0.25,
        "max_step_pixels": 85,
        "movement_margin": 0.08,
        "update_interval_seconds": 0.015,
    },
    "voice": {
        "enabled": True,
        "model_path": "models/vosk-es",
        "sample_rate": 16000,
        "block_size": 8000,
        "commands": {
            "activate": ["activar"],
            "deactivate": ["desactivar"],
            "open_browser": ["abrir navegador"],
            "exit": ["salir"],
        },
    },
    "clap": {
        "enabled": True,
        "threshold": 0.65,
        "cooldown_seconds": 1.2,
        "sample_rate": 44100,
        "block_size": 1024,
    },
    "ui": {
        "window_title": "RV Camera Controller",
        "show_audio_status": True,
    },
}


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_config(path: str | Path = "config/settings.yaml") -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        return deepcopy(DEFAULT_CONFIG)

    with config_path.open("r", encoding="utf-8") as file:
        raw_config = yaml.safe_load(file) or {}

    if not isinstance(raw_config, dict):
        raise ValueError(f"Config file must contain a YAML mapping: {config_path}")

    return deep_merge(DEFAULT_CONFIG, raw_config)
