"""Camera manager module for handling OpenCV webcam streams cleanly and robustly."""

import sys
import time
from typing import Optional, Tuple
import cv2
import numpy as np

from utils.logger import get_logger

logger = get_logger("camera_manager")


class CameraManager:
    """Manages OpenCV webcam initialization, frame capture, processing, and cleanup."""

    def __init__(
        self,
        camera_index: int = 0,
        width: int = 1280,
        height: int = 720,
        mirror: bool = True
    ) -> None:
        """Initialize CameraManager configurations.

        Args:
            camera_index: Device index for webcam (default 0).
            width: Desired target frame width in pixels.
            height: Desired target frame height in pixels.
            mirror: Whether to flip frame horizontally.
        """
        self.camera_index: int = camera_index
        self.target_width: int = width
        self.target_height: int = height
        self.mirror: bool = mirror

        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running: bool = False
        self._last_frame: Optional[np.ndarray] = None

    def start(self) -> bool:
        """Open camera stream and set properties.

        Returns:
            True if camera started successfully, False otherwise.
        """
        logger.info(f"Opening camera index {self.camera_index}...")

        # Try DirectShow on Windows first for fast startup, fallback to default OpenCV backend
        if sys.platform.startswith("win"):
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                logger.warning("cv2.CAP_DSHOW failed, falling back to default OpenCV backend...")
                self.cap = cv2.VideoCapture(self.camera_index)
        else:
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap or not self.cap.isOpened():
            logger.error(f"Failed to open camera index {self.camera_index}")
            self.is_running = False
            return False

        # Set width & height
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(self.target_width))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(self.target_height))

        # Check actual dimensions
        actual_w = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Camera opened successfully ({actual_w}x{actual_h}).")

        self.is_running = True
        return True

    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Capture, mirror, and resize next webcam frame.

        Returns:
            Tuple of (success_flag, processed_bgr_frame).
        """
        if not self.is_running or self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None or frame.size == 0:
            logger.warning("Failed to read frame from camera.")
            return False, self._last_frame

        # Mirror frame horizontally for intuitive interaction
        if self.mirror:
            frame = cv2.flip(frame, 1)

        # Resize if dimensions differ from target
        h, w = frame.shape[:2]
        if w != self.target_width or h != self.target_height:
            frame = cv2.resize(frame, (self.target_width, self.target_height), interpolation=cv2.INTER_LINEAR)

        self._last_frame = frame
        return True, frame

    def is_opened(self) -> bool:
        """Check if camera is currently opened."""
        return self.cap is not None and self.cap.isOpened() and self.is_running

    def release(self) -> None:
        """Release camera resources cleanly."""
        if self.cap is not None:
            logger.info("Releasing camera resources...")
            self.cap.release()
            self.cap = None
        self.is_running = False
        logger.info("Camera released.")
