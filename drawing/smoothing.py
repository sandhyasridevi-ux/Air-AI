"""Coordinate smoothing module to eliminate MediaPipe hand landmark jitter."""

from typing import Optional, Tuple


class CoordinateSmoother:
    """Exponential Moving Average (EMA) coordinate filter for smooth drawing lines."""

    def __init__(self, smoothing_factor: float = 0.5) -> None:
        """Initialize CoordinateSmoother.

        Args:
            smoothing_factor: Alpha factor between 0.0 (maximum smoothing) and 1.0 (raw input).
        """
        self.smoothing_factor: float = max(0.01, min(1.0, float(smoothing_factor)))
        self._prev_x: Optional[float] = None
        self._prev_y: Optional[float] = None

    def update(self, point: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Filter incoming (x, y) coordinate.

        Args:
            point: Tuple of (raw_x, raw_y) pixel coordinates or None.

        Returns:
            Smoothed (x, y) integer tuple or None.
        """
        if point is None:
            return None

        raw_x, raw_y = float(point[0]), float(point[1])

        if self._prev_x is None or self._prev_y is None:
            self._prev_x = raw_x
            self._prev_y = raw_y
            return (int(round(raw_x)), int(round(raw_y)))

        # EMA formula: S_t = alpha * P_t + (1 - alpha) * S_{t-1}
        alpha = self.smoothing_factor
        smoothed_x = alpha * raw_x + (1.0 - alpha) * self._prev_x
        smoothed_y = alpha * raw_y + (1.0 - alpha) * self._prev_y

        self._prev_x = smoothed_x
        self._prev_y = smoothed_y

        return (int(round(smoothed_x)), int(round(smoothed_y)))

    def reset(self) -> None:
        """Reset internal history when a drawing stroke ends."""
        self._prev_x = None
        self._prev_y = None

    def is_active(self) -> bool:
        """Check if filter has historical points loaded."""
        return self._prev_x is not None and self._prev_y is not None
