"""Virtual Drawing Canvas managing drawing layers and camera compositing."""

from typing import Optional, Tuple
import cv2
import numpy as np

from drawing.brush import Brush
from drawing.eraser import Eraser
from utils.logger import get_logger

logger = get_logger("canvas")


class Canvas:
    """Independent virtual drawing canvas layer."""

    def __init__(self, width: int = 1280, height: int = 720) -> None:
        """Initialize empty drawing canvas.

        Args:
            width: Width in pixels.
            height: Height in pixels.
        """
        self.width: int = width
        self.height: int = height
        self.layer: np.ndarray = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        self.brush: Brush = Brush()
        self.eraser: Eraser = Eraser()

    def draw(self, p1: Tuple[int, int], p2: Tuple[int, int], color: Optional[Tuple[int, int, int]] = None, size: Optional[int] = None) -> None:
        """Draw line from p1 to p2 using current or specified brush.

        Args:
            p1: Previous point.
            p2: Current point.
            color: Optional override BGR color tuple.
            size: Optional override brush size.
        """
        if color is not None:
            self.brush.color = color
        if size is not None:
            self.brush.size = size

        self.brush.draw_stroke(self.layer, p1, p2)

    def erase(self, p1: Tuple[int, int], p2: Tuple[int, int], size: Optional[int] = None) -> None:
        """Erase content from p1 to p2.

        Args:
            p1: Previous point.
            p2: Current point.
            size: Optional override eraser size.
        """
        if size is not None:
            self.eraser.size = size

        self.eraser.erase_stroke(self.layer, p1, p2)

    def clear(self) -> None:
        """Clear all content from the drawing canvas."""
        self.layer.fill(0)
        logger.info("Canvas cleared.")

    def get_layer(self) -> np.ndarray:
        """Return raw drawing layer array."""
        return self.layer

    def composite(self, camera_frame: np.ndarray) -> np.ndarray:
        """Overlay drawing canvas onto camera frame cleanly.

        Args:
            camera_frame: OpenCV BGR webcam frame.

        Returns:
            Composite image frame.
        """
        if camera_frame is None:
            return self.layer.copy()

        # Resize camera frame if dimensions do not match
        ch, cw = camera_frame.shape[:2]
        if cw != self.width or ch != self.height:
            camera_frame = cv2.resize(camera_frame, (self.width, self.height))

        # Create binary mask of non-black drawing pixels
        gray = cv2.cvtColor(self.layer, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)

        # Cut out drawing area from webcam frame and combine with vibrant drawing layer
        frame_bg = cv2.bitwise_and(camera_frame, camera_frame, mask=mask_inv)
        drawing_fg = cv2.bitwise_and(self.layer, self.layer, mask=mask)

        return cv2.add(frame_bg, drawing_fg)
