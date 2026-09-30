"""Centralized application settings and configuration loader."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)


class Settings:
    """Application Settings."""

    def __init__(self) -> None:
        # Camera Settings
        self.CAMERA_INDEX: int = int(os.getenv("CAMERA_INDEX", "0"))
        self.FRAME_WIDTH: int = int(os.getenv("FRAME_WIDTH", "1280"))
        self.FRAME_HEIGHT: int = int(os.getenv("FRAME_HEIGHT", "720"))

        # Hand Tracking Settings
        self.MAX_HANDS: int = int(os.getenv("MAX_HANDS", "1"))
        self.DETECTION_CONFIDENCE: float = float(os.getenv("DETECTION_CONFIDENCE", "0.7"))
        self.TRACKING_CONFIDENCE: float = float(os.getenv("TRACKING_CONFIDENCE", "0.7"))

        # Drawing Engine Settings
        self.SMOOTHING_FACTOR: float = float(os.getenv("SMOOTHING_FACTOR", "0.5"))
        self.BRUSH_SIZE: int = int(os.getenv("BRUSH_SIZE", "8"))
        self.ERASER_SIZE: int = int(os.getenv("ERASER_SIZE", "30"))

        # Storage Settings
        self.SAVED_DRAWINGS_DIR: str = os.getenv("SAVED_DRAWINGS_DIR", "saved_drawings")

        # Project Paths
        self.BASE_DIR: Path = Path(__file__).resolve().parent.parent
        self.SAVED_DRAWINGS_PATH: Path = self.BASE_DIR / self.SAVED_DRAWINGS_DIR

        # Ensure output directory exists
        self.SAVED_DRAWINGS_PATH.mkdir(parents=True, exist_ok=True)


settings = Settings()
