"""Top interactive UI toolbar for color selection and action buttons."""

from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple
import cv2
import numpy as np

from ui.colors import ColorPalette, Colors


@dataclass
class UIButton:
    """Interactive UI Button metadata."""

    name: str
    x1: int
    y1: int
    x2: int
    y2: int
    color: Tuple[int, int, int]
    action_type: str  # 'COLOR', 'ERASER', 'CLEAR', 'SAVE'
    is_active: bool = False


class Toolbar:
    """Interactive top toolbar controller."""

    def __init__(self, width: int = 1280, height: int = 90) -> None:
        """Initialize Toolbar layout.

        Args:
            width: Frame width in pixels.
            height: Toolbar panel height in pixels.
        """
        self.width: int = width
        self.height: int = height
        self.buttons: List[UIButton] = []
        self._init_buttons()

    def _init_buttons(self) -> None:
        """Create buttons layout dynamically based on palette and actions."""
        self.buttons.clear()

        # Layout parameters
        button_height = 60
        margin = 15
        top_y = 15
        bottom_y = top_y + button_height

        # Calculate width per button slot
        palette = ColorPalette.DEFAULT_COLORS
        num_color_buttons = len(palette)
        action_names = ["ERASER", "CLEAR", "SAVE"]
        total_slots = num_color_buttons + len(action_names)

        slot_width = (self.width - (margin * (total_slots + 1))) // total_slots

        x_cursor = margin

        # Color Buttons
        for color_bgr, color_name in palette:
            self.buttons.append(
                UIButton(
                    name=color_name,
                    x1=x_cursor,
                    y1=top_y,
                    x2=x_cursor + slot_width,
                    y2=bottom_y,
                    color=color_bgr,
                    action_type="COLOR",
                    is_active=(color_name == "RED")
                )
            )
            x_cursor += slot_width + margin

        # Eraser Button
        self.buttons.append(
            UIButton(
                name="ERASER",
                x1=x_cursor,
                y1=top_y,
                x2=x_cursor + slot_width,
                y2=bottom_y,
                color=(60, 60, 60),
                action_type="ERASER",
                is_active=False
            )
        )
        x_cursor += slot_width + margin

        # Clear Button
        self.buttons.append(
            UIButton(
                name="CLEAR",
                x1=x_cursor,
                y1=top_y,
                x2=x_cursor + slot_width,
                y2=bottom_y,
                color=(0, 100, 200),
                action_type="CLEAR",
                is_active=False
            )
        )
        x_cursor += slot_width + margin

        # Save Button
        self.buttons.append(
            UIButton(
                name="SAVE",
                x1=x_cursor,
                y1=top_y,
                x2=x_cursor + slot_width,
                y2=bottom_y,
                color=(0, 150, 0),
                action_type="SAVE",
                is_active=False
            )
        )

    def set_active_color(self, color_bgr: Tuple[int, int, int]) -> None:
        """Mark corresponding color button as active."""
        for btn in self.buttons:
            if btn.action_type == "COLOR":
                btn.is_active = (btn.color == color_bgr)
            elif btn.action_type == "ERASER":
                btn.is_active = False

    def set_active_eraser(self, is_eraser: bool) -> None:
        """Mark eraser button as active."""
        for btn in self.buttons:
            if btn.action_type == "ERASER":
                btn.is_active = is_eraser
            elif is_eraser and btn.action_type == "COLOR":
                btn.is_active = False

    def check_interaction(self, point: Optional[Tuple[int, int]]) -> Optional[UIButton]:
        """Check if point (e.g. index tip) collides with any button in toolbar.

        Args:
            point: (x, y) tuple or None.

        Returns:
            Clicked UIButton or None.
        """
        if point is None:
            return None

        px, py = point
        if py > self.height:
            return None

        for btn in self.buttons:
            if btn.x1 <= px <= btn.x2 and btn.y1 <= py <= btn.y2:
                return btn
        return None

    def render(self, frame: np.ndarray, hover_point: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """Draw toolbar overlay onto image frame.

        Args:
            frame: OpenCV BGR image frame.
            hover_point: Current fingertip position to highlight hovered button.

        Returns:
            Rendered frame.
        """
        if frame is None:
            return frame

        # Glassmorphic top header bar overlay background
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (self.width, self.height), (20, 20, 20), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # Draw header dividing bottom line
        cv2.line(frame, (0, self.height), (self.width, self.height), (100, 100, 100), 2)

        # Render buttons
        for btn in self.buttons:
            is_hovered = False
            if hover_point is not None:
                px, py = hover_point
                if btn.x1 <= px <= btn.x2 and btn.y1 <= py <= btn.y2:
                    is_hovered = True

            # Button background box
            bg_color = btn.color
            if btn.action_type in ("CLEAR", "SAVE", "ERASER"):
                bg_color = (80, 80, 80) if not btn.is_active else (120, 120, 120)

            cv2.rectangle(frame, (btn.x1, btn.y1), (btn.x2, btn.y2), bg_color, -1)

            # Border highlighting (active or hovered)
            border_color = (255, 255, 255) if is_hovered else ((0, 255, 255) if btn.is_active else (50, 50, 50))
            border_thickness = 3 if (btn.is_active or is_hovered) else 1
            cv2.rectangle(frame, (btn.x1, btn.y1), (btn.x2, btn.y2), border_color, border_thickness)

            # Button text label
            text_color = (255, 255, 255) if btn.color in (Colors.BLACK, (60, 60, 60)) else (0, 0, 0)
            if btn.action_type in ("CLEAR", "SAVE", "ERASER"):
                text_color = (255, 255, 255)

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 2
            text_size = cv2.getTextSize(btn.name, font, font_scale, thickness)[0]

            tx = btn.x1 + (btn.x2 - btn.x1 - text_size[0]) // 2
            ty = btn.y1 + (btn.y2 - btn.y1 + text_size[1]) // 2
            cv2.putText(frame, btn.name, (tx, ty), font, font_scale, text_color, thickness, cv2.LINE_AA)

        return frame
