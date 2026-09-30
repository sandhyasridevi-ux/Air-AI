"""Unit tests for FPS counter monitoring module."""

import pytest
from utils.fps import FPSCounter


def test_fps_initialization():
    fps_counter = FPSCounter(window_size=10)
    assert fps_counter.window_size == 10
    assert fps_counter.get_fps() == 0.0


def test_fps_calculation():
    fps_counter = FPSCounter(window_size=5)
    # Simulate frames spaced 0.0333 seconds apart (~30 FPS)
    t = 100.0
    fps_counter.update(now=t)
    fps_counter.update(now=t + 0.0333)
    fps_counter.update(now=t + 0.0666)
    fps_counter.update(now=t + 0.1000)

    fps = fps_counter.get_fps()
    assert 29.0 <= fps <= 31.0


def test_fps_reset():
    fps_counter = FPSCounter(window_size=5)
    fps_counter.update(now=100.0)
    fps_counter.update(now=100.033)
    assert fps_counter.get_fps() > 0

    fps_counter.reset()
    assert fps_counter.get_fps() == 0.0
    assert len(fps_counter.frame_times) == 0


def test_fps_high_low_rates():
    # Test 60 FPS (dt = 0.0166)
    fps_60 = FPSCounter(window_size=10)
    t = 0.0
    for i in range(11):
        fps_60.update(now=t + i * 0.01666)
    assert 59.0 <= fps_60.get_fps() <= 61.0

    # Test 10 FPS (dt = 0.1)
    fps_10 = FPSCounter(window_size=10)
    t = 0.0
    for i in range(11):
        fps_10.update(now=t + i * 0.1)
    assert 9.5 <= fps_10.get_fps() <= 10.5
