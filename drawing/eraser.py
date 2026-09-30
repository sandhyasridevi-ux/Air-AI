"""Eraser object for clearing content from drawing canvas layer."""

from typing import Tuple
import cv2
import numpy as np


class Eraser:
    """Dedicated eraser tool for removing stroke content."""

    def __init__(self, size: int = 30) -> None:
        """Initialize Eraser.

        Args:
            size: Eraser width/diameter in pixels.
        """
        self.size: int = max(5, min(200, int(size)))

    def erase_stroke(
        self,
        canvas: np.ndarray,
        p1: Tuple[int, int],
        p2: Tuple[int, int]
    ) -> None:
        """Erase stroke along p1 to p2 path on canvas layer by overwriting with (0,0,0).

        Args:
            canvas: OpenCV BGR canvas image array.
            p1: Start (x, y) point.
            p2: End (x, y) point.
        """
        if canvas is None or p1 is None or p2 is None:
            return

        # Overwrite with black (transparent mask area)
        cv2.line(canvas, p1, p2, (0, 0, 0), self.size, cv2.LINE_AA)
        radius = max(1, self.size // 2)
        cv2.circle(canvas, p2, radius, (0, 0, 0), -1, cv2.LINE_AA)
