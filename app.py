"""Air Canvas AI — Real-Time Touchless Drawing System Main Application."""

import sys
import time
import cv2
import numpy as np

from camera.camera_manager import CameraManager
from config.settings import settings
from drawing.canvas import Canvas
from drawing.smoothing import CoordinateSmoother
from gestures.gesture_detector import GestureDetector
from gestures.gesture_types import GestureType
from hand_tracking.hand_detector import HandDetector
from storage.drawing_saver import DrawingSaver
from ui.colors import ColorPalette, Colors
from ui.controls import ControlPanel
from ui.toolbar import Toolbar
from utils.fps import FPSCounter
from utils.logger import get_logger

logger = get_logger("app")


def main() -> None:
    """Initialize modules and execute the main real-time computer vision loop."""
    logger.info("Initializing Air Canvas AI Application...")

    # 1. Initialize Components
    camera = CameraManager(
        camera_index=settings.CAMERA_INDEX,
        width=settings.FRAME_WIDTH,
        height=settings.FRAME_HEIGHT,
        mirror=True
    )

    if not camera.start():
        logger.error("Failed to start camera stream. Exiting.")
        sys.exit(1)

    hand_detector = HandDetector(
        max_hands=settings.MAX_HANDS,
        detection_confidence=settings.DETECTION_CONFIDENCE,
        tracking_confidence=settings.TRACKING_CONFIDENCE,
    )

    toolbar = Toolbar(width=settings.FRAME_WIDTH, height=90)
    gesture_detector = GestureDetector(toolbar_height=toolbar.height)
    canvas = Canvas(width=settings.FRAME_WIDTH, height=settings.FRAME_HEIGHT)
    smoother = CoordinateSmoother(smoothing_factor=settings.SMOOTHING_FACTOR)
    saver = DrawingSaver(output_dir=settings.SAVED_DRAWINGS_PATH)
    control_panel = ControlPanel(width=settings.FRAME_WIDTH, height=settings.FRAME_HEIGHT)
    fps_counter = FPSCounter(window_size=30)

    # 2. Application State Variables
    active_color = Colors.RED
    is_eraser_active = False
    brush_size = settings.BRUSH_SIZE
    eraser_size = settings.ERASER_SIZE

    prev_point = None
    status_message = ""
    status_timer = 0  # Frame counter for showing toast message

    # Cooldown counters for gestures
    save_cooldown = 0
    clear_cooldown = 0

    window_name = "Air Canvas AI"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    logger.info("Application loop started. Press 'q' or 'ESC' to exit.")

    try:
        while True:
            # Step 1: Capture Frame from Camera
            ret, frame = camera.read()
            if not ret or frame is None:
                logger.warning("Camera frame unavailable. Waiting...")
                time.sleep(0.01)
                continue

            # Update cooldowns and status timers
            if save_cooldown > 0:
                save_cooldown -= 1
            if clear_cooldown > 0:
                clear_cooldown -= 1
            if status_timer > 0:
                status_timer -= 1
                if status_timer == 0:
                    status_message = ""

            # Step 2: Hand Tracking & Landmark Extraction
            hand_landmarks = hand_detector.detect(frame)

            # Draw Hand Skeleton on Raw Camera Frame
            if hand_landmarks:
                hand_detector.draw_landmarks(frame, hand_landmarks)

            # Step 3: Gesture Engine Recognition
            gesture_res = gesture_detector.detect(hand_landmarks)

            # Step 4: Handle Toolbar Touchless Interaction
            hover_btn = toolbar.check_interaction(gesture_res.position)
            if hover_btn and gesture_res.type == GestureType.COLOR_SELECT:
                if hover_btn.action_type == "COLOR":
                    active_color = hover_btn.color
                    is_eraser_active = False
                    toolbar.set_active_color(active_color)
                    toolbar.set_active_eraser(False)
                    status_message = f"Selected Color: {Colors.get_name(active_color)}"
                    status_timer = 45
                elif hover_btn.action_type == "ERASER":
                    is_eraser_active = True
                    toolbar.set_active_eraser(True)
                    status_message = "Eraser Tool Active"
                    status_timer = 45
                elif hover_btn.action_type == "CLEAR" and clear_cooldown == 0:
                    canvas.clear()
                    clear_cooldown = 30
                    status_message = "Canvas Cleared!"
                    status_timer = 60
                elif hover_btn.action_type == "SAVE" and save_cooldown == 0:
                    success, filepath, msg = saver.save_drawing(canvas.get_layer())
                    save_cooldown = 45
                    status_message = msg if success else "Failed to Save"
                    status_timer = 90

            # Step 5: Process Active Drawing / Action State
            current_mode = "IDLE"

            if gesture_res.type == GestureType.DRAW and not is_eraser_active:
                current_mode = "DRAW"
                smoothed_pt = smoother.update(gesture_res.position)
                if prev_point is not None and smoothed_pt is not None:
                    canvas.draw(prev_point, smoothed_pt, color=active_color, size=brush_size)
                prev_point = smoothed_pt

            elif (gesture_res.type == GestureType.ERASER) or (gesture_res.type == GestureType.DRAW and is_eraser_active):
                current_mode = "ERASER"
                smoothed_pt = smoother.update(gesture_res.position)
                if prev_point is not None and smoothed_pt is not None:
                    canvas.erase(prev_point, smoothed_pt, size=eraser_size)
                prev_point = smoothed_pt

            elif gesture_res.type == GestureType.CLEAR and clear_cooldown == 0:
                current_mode = "CLEAR"
                canvas.clear()
                clear_cooldown = 30
                status_message = "Canvas Cleared (Gesture)"
                status_timer = 60
                smoother.reset()
                prev_point = None

            elif gesture_res.type == GestureType.SAVE and save_cooldown == 0:
                current_mode = "SAVE"
                success, filepath, msg = saver.save_drawing(canvas.get_layer())
                save_cooldown = 45
                status_message = msg if success else "Failed to Save (Gesture)"
                status_timer = 90
                smoother.reset()
                prev_point = None

            else:
                current_mode = "IDLE" if not hover_btn else "TOOLBAR"
                smoother.reset()
                prev_point = None

            # Step 6: Layer Compositing & Output Rendering
            composite_frame = canvas.composite(frame)

            # Step 7: UI Toolbar & Controls HUD Overlay
            composite_frame = toolbar.render(composite_frame, hover_point=gesture_res.position)
            fps_val = fps_counter.update()
            composite_frame = control_panel.render_hud(
                composite_frame,
                mode=current_mode,
                color_bgr=active_color if not is_eraser_active else Colors.DARK_GRAY,
                brush_size=brush_size if not is_eraser_active else eraser_size,
                fps=fps_val,
                status_message=status_message
            )

            # Display Window
            cv2.imshow(window_name, composite_frame)

            # Step 8: Keyboard Event Handling
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q"), ord("Q")):
                logger.info("Exit requested by user.")
                break
            elif key in (ord("c"), ord("C")):
                canvas.clear()
                status_message = "Canvas Cleared (Key C)"
                status_timer = 60
            elif key in (ord("s"), ord("S")):
                success, filepath, msg = saver.save_drawing(canvas.get_layer())
                status_message = msg if success else "Save Failed"
                status_timer = 90
            elif key in (ord("e"), ord("E")):
                is_eraser_active = not is_eraser_active
                toolbar.set_active_eraser(is_eraser_active)
                status_message = "Eraser Mode Enabled" if is_eraser_active else "Brush Mode Enabled"
                status_timer = 45
            elif key in (ord("+"), ord("=")):
                if is_eraser_active:
                    eraser_size = min(150, eraser_size + 5)
                    status_message = f"Eraser Size: {eraser_size}px"
                else:
                    brush_size = min(50, brush_size + 2)
                    status_message = f"Brush Size: {brush_size}px"
                status_timer = 45
            elif key in (ord("-"), ord("_")):
                if is_eraser_active:
                    eraser_size = max(5, eraser_size - 5)
                    status_message = f"Eraser Size: {eraser_size}px"
                else:
                    brush_size = max(1, brush_size - 2)
                    status_message = f"Brush Size: {brush_size}px"
                status_timer = 45
            # Hotkeys 1-6 for quick color picking
            elif ord("1") <= key <= ord("6"):
                color_idx = key - ord("1")
                if color_idx < len(ColorPalette.DEFAULT_COLORS):
                    active_color = ColorPalette.DEFAULT_COLORS[color_idx][0]
                    is_eraser_active = False
                    toolbar.set_active_color(active_color)
                    toolbar.set_active_eraser(False)
                    status_message = f"Color: {ColorPalette.DEFAULT_COLORS[color_idx][1]}"
                    status_timer = 45

    except Exception as e:
        logger.error(f"Unexpected error in application loop: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up resources...")
        camera.release()
        hand_detector.close()
        cv2.destroyAllWindows()
        logger.info("Application shut down cleanly.")


if __name__ == "__main__":
    main()
