from pathlib import Path
from src.core.config_loader import load_config


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_config() -> dict:
    return load_config(get_project_root() / "config" / "settings.yaml")