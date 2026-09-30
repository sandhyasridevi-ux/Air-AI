"""Brush object for rendering smooth stroke lines."""

from typing import Tuple
import cv2
import numpy as np


class Brush:
    """Configurable drawing brush."""

    def __init__(self, color: Tuple[int, int, int] = (0, 0, 255), size: int = 8) -> None:
        """Initialize Brush.

        Args:
            color: BGR tuple (e.g. (0, 0, 255) for Red).
            size: Brush stroke thickness in pixels.
        """
        self.color: Tuple[int, int, int] = color
        self.size: int = max(1, min(100, int(size)))

    def draw_stroke(
        self,
        canvas: np.ndarray,
        p1: Tuple[int, int],
        p2: Tuple[int, int]
    ) -> None:
        """Render anti-aliased line stroke from p1 to p2 on canvas layer.

        Args:
            canvas: OpenCV BGR canvas image array.
            p1: Start (x, y) point.
            p2: End (x, y) point.
        """
        if canvas is None or p1 is None or p2 is None:
            return

        # Draw anti-aliased stroke line
        cv2.line(canvas, p1, p2, self.color, self.size, cv2.LINE_AA)
        # Round joint cap at p2
        radius = max(1, self.size // 2)
        cv2.circle(canvas, p2, radius, self.color, -1, cv2.LINE_AA)
