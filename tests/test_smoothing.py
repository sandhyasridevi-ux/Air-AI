"""Unit tests for coordinate smoothing module."""

import pytest
from drawing.smoothing import CoordinateSmoother


def test_smoother_initialization():
    smoother = CoordinateSmoother(smoothing_factor=0.5)
    assert smoother.smoothing_factor == 0.5
    assert not smoother.is_active()


def test_smoother_stable_input():
    smoother = CoordinateSmoother(smoothing_factor=0.5)
    # First point initializes filter
    p1 = smoother.update((100, 100))
    assert p1 == (100, 100)

    # Repeating same point remains constant
    p2 = smoother.update((100, 100))
    assert p2 == (100, 100)


def test_smoother_noisy_input():
    smoother = CoordinateSmoother(smoothing_factor=0.5)
    smoother.update((100, 100))

    # Single noisy spike to (120, 100) with alpha=0.5:
    # 0.5 * 120 + 0.5 * 100 = 110
    smoothed = smoother.update((120, 100))
    assert smoothed == (110, 100)


def test_smoother_sudden_movement():
    smoother = CoordinateSmoother(smoothing_factor=0.5)
    smoother.update((10, 10))
    # Jump to (100, 100)
    p2 = smoother.update((100, 100))
    assert p2 == (55, 55)  # 0.5*100 + 0.5*10


def test_smoother_reset():
    smoother = CoordinateSmoother(smoothing_factor=0.5)
    smoother.update((10, 10))
    smoother.update((20, 20))
    assert smoother.is_active()

    smoother.reset()
    assert not smoother.is_active()

    # Next point after reset should not interpolate from (20, 20)
    fresh_point = smoother.update((500, 500))
    assert fresh_point == (500, 500)


def test_smoother_none_input():
    smoother = CoordinateSmoother(smoothing_factor=0.5)
    assert smoother.update(None) is None
