"""Unit tests for gesture recognition engine."""

import pytest
from gestures.gesture_detector import GestureDetector
from gestures.gesture_types import GestureType
from hand_tracking.landmarks import HandLandmarks, LandmarkPoint


def create_mock_hand(
    index_up: bool = False,
    middle_up: bool = False,
    ring_up: bool = False,
    pinky_up: bool = False,
    thumb_up: bool = False,
    index_y: int = 200,
) -> HandLandmarks:
    """Helper factory for building mock HandLandmarks objects for testing."""
    points = []
    # Build 21 dummy points
    for i in range(21):
        points.append(LandmarkPoint(id=i, x=400, y=300, z=0.0))

    # Wrist
    points[0] = LandmarkPoint(id=0, x=400, y=500)

    # Thumb: Pinky MCP is at x=450, y=400
    points[17] = LandmarkPoint(id=17, x=450, y=400)  # Pinky MCP
    points[3] = LandmarkPoint(id=3, x=350, y=420)  # Thumb IP
    if thumb_up:
        points[4] = LandmarkPoint(id=4, x=250, y=420)  # Thumb Tip far from pinky mcp
    else:
        points[4] = LandmarkPoint(id=4, x=380, y=420)  # Thumb Tip close to pinky mcp

    # Index finger PIP (6) & Tip (8)
    pip_y = index_y + 50
    tip_y = index_y if index_up else index_y + 100
    points[6] = LandmarkPoint(id=6, x=400, y=pip_y)
    points[8] = LandmarkPoint(id=8, x=400, y=tip_y)

    # Middle finger PIP (10) & Tip (12)
    points[10] = LandmarkPoint(id=10, x=420, y=350)
    points[12] = LandmarkPoint(id=12, x=420, y=300 if middle_up else 400)

    # Ring finger PIP (14) & Tip (16)
    points[14] = LandmarkPoint(id=14, x=440, y=350)
    points[16] = LandmarkPoint(id=16, x=440, y=300 if ring_up else 400)

    # Pinky finger PIP (18) & Tip (20)
    points[18] = LandmarkPoint(id=18, x=460, y=350)
    points[20] = LandmarkPoint(id=20, x=460, y=300 if pinky_up else 400)

    return HandLandmarks(points=points)


def test_draw_gesture():
    detector = GestureDetector(toolbar_height=100)
    # Index finger extended UP, others folded
    hand = create_mock_hand(index_up=True, middle_up=False, ring_up=False, pinky_up=False, index_y=200)
    result = detector.detect(hand)
    assert result.type == GestureType.DRAW
    assert result.position == (400, 200)


def test_eraser_gesture():
    detector = GestureDetector(toolbar_height=100)
    # Index AND Middle fingers extended UP (scissors gesture)
    hand = create_mock_hand(index_up=True, middle_up=True, ring_up=False, pinky_up=False, index_y=200)
    result = detector.detect(hand)
    assert result.type == GestureType.ERASER


def test_clear_gesture():
    detector = GestureDetector(toolbar_height=100)
    # All fingers extended UP (open palm)
    hand = create_mock_hand(index_up=True, middle_up=True, ring_up=True, pinky_up=True, index_y=200)
    result = detector.detect(hand)
    assert result.type == GestureType.CLEAR


def test_save_gesture():
    detector = GestureDetector(toolbar_height=100)
    # Closed fist (all fingers folded)
    hand = create_mock_hand(index_up=False, middle_up=False, ring_up=False, pinky_up=False, thumb_up=False)
    result = detector.detect(hand)
    assert result.type == GestureType.SAVE


def test_color_select_toolbar_gesture():
    detector = GestureDetector(toolbar_height=100)
    # Index finger inside top toolbar region (index_y = 50 < 100)
    hand = create_mock_hand(index_up=True, middle_up=False, ring_up=False, pinky_up=False, index_y=50)
    result = detector.detect(hand)
    assert result.type == GestureType.COLOR_SELECT


def test_no_hand_gesture():
    detector = GestureDetector(toolbar_height=100)
    result = detector.detect(None)
    assert result.type == GestureType.IDLE
    assert result.position is None
