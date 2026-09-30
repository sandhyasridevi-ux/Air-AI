"""Unit tests for virtual canvas and drawing saver module."""

import numpy as np
import pytest
from pathlib import Path
from drawing.canvas import Canvas
from storage.drawing_saver import DrawingSaver


def test_canvas_initialization():
    canvas = Canvas(width=640, height=480)
    assert canvas.width == 640
    assert canvas.height == 480
    assert canvas.get_layer().shape == (480, 640, 3)
    assert np.all(canvas.get_layer() == 0)


def test_canvas_draw_stroke():
    canvas = Canvas(width=640, height=480)
    # Draw red line
    canvas.draw((100, 100), (200, 200), color=(0, 0, 255), size=10)
    layer = canvas.get_layer()
    # Check that layer is no longer empty black array
    assert np.sum(layer) > 0
    # Check specific drawn pixel region has non-zero red values
    assert layer[150, 150, 2] > 0  # BGR Red channel > 0


def test_canvas_erase_stroke():
    canvas = Canvas(width=640, height=480)
    canvas.draw((100, 100), (200, 200), color=(0, 0, 255), size=10)
    assert np.sum(canvas.get_layer()) > 0

    # Erase over the same line
    canvas.erase((100, 100), (200, 200), size=30)
    layer = canvas.get_layer()
    # Check erased region center is zero
    assert layer[150, 150, 2] == 0


def test_canvas_clear():
    canvas = Canvas(width=640, height=480)
    canvas.draw((50, 50), (100, 100), color=(255, 0, 0), size=5)
    assert np.sum(canvas.get_layer()) > 0

    canvas.clear()
    assert np.all(canvas.get_layer() == 0)


def test_canvas_composite():
    canvas = Canvas(width=640, height=480)
    canvas.draw((50, 50), (100, 100), color=(0, 255, 0), size=10)

    dummy_camera_frame = np.ones((480, 640, 3), dtype=np.uint8) * 100
    composite = canvas.composite(dummy_camera_frame)
    assert composite.shape == (480, 640, 3)
    # Check that drawing pixel area is green (0, 255, 0)
    assert np.array_equal(composite[75, 75], [0, 255, 0])
    # Check non-drawn area retains background frame (100, 100, 100)
    assert np.array_equal(composite[10, 10], [100, 100, 100])


def test_drawing_saver(tmp_path: Path):
    saver = DrawingSaver(output_dir=tmp_path)
    canvas = Canvas(width=100, height=100)
    canvas.draw((10, 10), (50, 50), color=(0, 0, 255), size=4)

    success, filepath, msg = saver.save_drawing(canvas.get_layer())
    assert success
    assert Path(filepath).exists()
    assert Path(filepath).suffix == ".png"
