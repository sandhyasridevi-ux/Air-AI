"""Heads-Up Display (HUD) control panel rendering state information and shortcuts."""

from typing import Tuple
import cv2
import numpy as np

from ui.colors import Colors


class ControlPanel:
    """Renders application HUD stats, status banners, and shortcut key legends."""

    def __init__(self, width: int = 1280, height: int = 720) -> None:
        """Initialize ControlPanel.

        Args:
            width: Canvas width.
            height: Canvas height.
        """
        self.width: int = width
        self.height: int = height

    def render_hud(
        self,
        frame: np.ndarray,
        mode: str,
        color_bgr: Tuple[int, int, int],
        brush_size: int,
        fps: float,
        status_message: str = "",
    ) -> np.ndarray:
        """Draw sleek information overlay onto composite frame.

        Args:
            frame: OpenCV BGR image frame.
            mode: Active mode string (e.g. 'DRAW', 'ERASER', 'IDLE').
            color_bgr: Active brush BGR color tuple.
            brush_size: Active brush/eraser size in pixels.
            fps: Current FPS calculation.
            status_message: Temporary status message (e.g. 'Saved drawing to saved_drawings/...').

        Returns:
            Frame with HUD overlay.
        """
        if frame is None:
            return frame

        # Top-left HUD badge: App Title, Mode, Color, Brush Size
        badge_x, badge_y = 20, 105
        badge_w, badge_h = 340, 110

        # Semi-transparent background panel
        overlay = frame.copy()
        cv2.rectangle(overlay, (badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h), (15, 15, 15), -1)
        cv2.addWeighted(overlay, 0.75, frame, 0.25, 0, frame)
        cv2.rectangle(frame, (badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h), (80, 80, 80), 1)

        # Title
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, "AIR CANVAS AI", (badge_x + 15, badge_y + 25), font, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

        # Mode Badge
        mode_color = (0, 255, 0) if mode == "DRAW" else ((0, 165, 255) if mode == "ERASER" else (200, 200, 200))
        cv2.putText(frame, f"Mode: {mode}", (badge_x + 15, badge_y + 55), font, 0.55, mode_color, 2, cv2.LINE_AA)

        # Color Indicator circle & name
        color_name = Colors.get_name(color_bgr)
        cv2.putText(frame, f"Color: {color_name}", (badge_x + 15, badge_y + 85), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.circle(frame, (badge_x + 180, badge_y + 80), 8, color_bgr, -1, cv2.LINE_AA)
        cv2.circle(frame, (badge_x + 180, badge_y + 80), 9, (255, 255, 255), 1, cv2.LINE_AA)

        # Brush Size
        cv2.putText(frame, f"Brush: {brush_size}px", (badge_x + 215, badge_y + 85), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        # Top-Right FPS Counter
        fps_str = f"FPS: {fps:.1f}"
        fps_x = self.width - 150
        cv2.rectangle(frame, (fps_x - 10, 105), (self.width - 15, 140), (15, 15, 15), -1)
        cv2.rectangle(frame, (fps_x - 10, 105), (self.width - 15, 140), (80, 80, 80), 1)
        cv2.putText(frame, fps_str, (fps_x, 130), font, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

        # Status Message Toast Notification (if active)
        if status_message:
            toast_w, toast_h = 500, 40
            toast_x = (self.width - toast_w) // 2
            toast_y = self.height - 85
            cv2.rectangle(frame, (toast_x, toast_y), (toast_x + toast_w, toast_y + toast_h), (0, 120, 0), -1)
            cv2.rectangle(frame, (toast_x, toast_y), (toast_x + toast_w, toast_y + toast_h), (255, 255, 255), 1)
            cv2.putText(frame, status_message, (toast_x + 20, toast_y + 26), font, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        # Bottom Shortcut Key Bar
        bottom_y = self.height - 35
        cv2.rectangle(frame, (0, bottom_y), (self.width, self.height), (20, 20, 20), -1)
        cv2.line(frame, (0, bottom_y), (self.width, bottom_y), (80, 80, 80), 1)
        legend_text = "Shortcuts: [C] Clear | [S] Save | [+] Brush+ | [-] Brush- | [1-6] Colors | [E] Eraser | [Q/ESC] Quit"
        cv2.putText(frame, legend_text, (20, bottom_y + 22), font, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

        return frame
