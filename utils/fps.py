"""FPS calculation and performance monitoring module."""

import time
from collections import deque


class FPSCounter:
    """Real-time Frames Per Second (FPS) counter with moving average smoothing."""

    def __init__(self, window_size: int = 30) -> None:
        """Initialize FPS counter.

        Args:
            window_size: Number of recent frame timestamps to hold in moving average window.
        """
        self.window_size: int = max(1, window_size)
        self.frame_times: deque = deque(maxlen=self.window_size)
        self._last_timestamp: float = time.perf_counter()
        self._current_fps: float = 0.0

    def update(self, now: float | None = None) -> float:
        """Record frame update and return current smoothed FPS.

        Args:
            now: Optional explicit timestamp (seconds), defaults to time.perf_counter().

        Returns:
            Current calculated FPS.
        """
        timestamp = now if now is not None else time.perf_counter()
        dt = timestamp - self._last_timestamp
        self._last_timestamp = timestamp

        if dt > 0:
            self.frame_times.append(dt)

        if len(self.frame_times) > 0:
            avg_dt = sum(self.frame_times) / len(self.frame_times)
            self._current_fps = 1.0 / avg_dt if avg_dt > 0 else 0.0
        else:
            self._current_fps = 0.0

        return self._current_fps

    def get_fps(self) -> float:
        """Get current FPS value.

        Returns:
            Current FPS float rounded to 1 decimal place or raw.
        """
        return round(self._current_fps, 1)

    def reset(self) -> None:
        """Reset internal frame history and timers."""
        self.frame_times.clear()
        self._last_timestamp = time.perf_counter()
        self._current_fps = 0.0
