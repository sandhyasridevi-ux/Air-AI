"""Gesture recognition engine analyzing hand landmark geometry and finger states."""

import math
from typing import List, Optional, Tuple

from gestures.gesture_types import GestureResult, GestureType
from hand_tracking.landmarks import HandLandmarks, LandmarkID
from utils.logger import get_logger

logger = get_logger("gesture_detector")


class GestureDetector:
    """Analyzes hand landmarks to detect active drawing or control gestures."""

    def __init__(self, toolbar_height: int = 90) -> None:
        """Initialize GestureDetector.

        Args:
            toolbar_height: Y-boundary in pixels defining upper UI toolbar area.
        """
        self.toolbar_height: int = toolbar_height

    def get_finger_states(self, hand: HandLandmarks) -> List[bool]:
        """Determine which of the 5 fingers are extended (open).

        Uses distance from wrist to tip vs wrist to PIP joint for orientation-independent detection.

        Returns:
            List of 5 booleans: [Thumb, Index, Middle, Ring, Pinky]
        """
        if hand is None:
            return [False, False, False, False, False]

        wrist = hand.wrist
        pinky_mcp = hand.pinky_mcp

        # 1. Thumb State: Compare distance from thumb tip to pinky MCP vs thumb IP to pinky MCP
        thumb_tip_dist = math.hypot(hand.thumb_tip.x - pinky_mcp.x, hand.thumb_tip.y - pinky_mcp.y)
        thumb_ip_dist = math.hypot(hand.thumb_ip.x - pinky_mcp.x, hand.thumb_ip.y - pinky_mcp.y)
        thumb_up = thumb_tip_dist > (thumb_ip_dist * 1.1)

        # 2. Index Finger: Tip further from wrist than PIP joint (and Y < PIP Y when upright)
        dist_index_tip = math.hypot(hand.index_tip.x - wrist.x, hand.index_tip.y - wrist.y)
        dist_index_pip = math.hypot(hand.index_pip.x - wrist.x, hand.index_pip.y - wrist.y)
        index_up = dist_index_tip > dist_index_pip and (hand.index_tip.y < hand.index_pip.y + 15)

        # 3. Middle Finger
        dist_middle_tip = math.hypot(hand.middle_tip.x - wrist.x, hand.middle_tip.y - wrist.y)
        dist_middle_pip = math.hypot(hand.middle_pip.x - wrist.x, hand.middle_pip.y - wrist.y)
        middle_up = dist_middle_tip > dist_middle_pip and (hand.middle_tip.y < hand.middle_pip.y + 15)

        # 4. Ring Finger
        dist_ring_tip = math.hypot(hand.ring_tip.x - wrist.x, hand.ring_tip.y - wrist.y)
        dist_ring_pip = math.hypot(hand.ring_pip.x - wrist.x, hand.ring_pip.y - wrist.y)
        ring_up = dist_ring_tip > dist_ring_pip and (hand.ring_tip.y < hand.ring_pip.y + 15)

        # 5. Pinky Finger
        dist_pinky_tip = math.hypot(hand.pinky_tip.x - wrist.x, hand.pinky_tip.y - wrist.y)
        dist_pinky_pip = math.hypot(hand.pinky_pip.x - wrist.x, hand.pinky_pip.y - wrist.y)
        pinky_up = dist_pinky_tip > dist_pinky_pip and (hand.pinky_tip.y < hand.pinky_pip.y + 15)

        return [thumb_up, index_up, middle_up, ring_up, pinky_up]

    def detect(self, hand: Optional[HandLandmarks]) -> GestureResult:
        """Process hand landmarks and determine the current active gesture.

        Args:
            hand: HandLandmarks object or None.

        Returns:
            GestureResult dataclass object.
        """
        if hand is None:
            return GestureResult(
                type=GestureType.IDLE,
                position=None,
                confidence=0.0,
                fingers_up=[False, False, False, False, False]
            )

        fingers = self.get_finger_states(hand)
        thumb_up, index_up, middle_up, ring_up, pinky_up = fingers
        index_pos = hand.index_tip.position

        # Check if fingertip is inside upper UI toolbar zone
        in_toolbar = index_pos[1] < self.toolbar_height

        # Rule 1: Toolbar Selection Mode (Index finger inside top toolbar region)
        if in_toolbar and index_up:
            return GestureResult(
                type=GestureType.COLOR_SELECT,
                position=index_pos,
                confidence=0.95,
                fingers_up=fingers,
                details={"in_toolbar": True}
            )

        # Rule 2: Clear Gesture (Open Palm: all 4 main fingers extended UP)
        if index_up and middle_up and ring_up and pinky_up:
            return GestureResult(
                type=GestureType.CLEAR,
                position=index_pos,
                confidence=0.95,
                fingers_up=fingers,
                details={"open_palm": True}
            )

        # Rule 3: Eraser Gesture (Index AND Middle fingers UP, Ring and Pinky DOWN)
        if index_up and middle_up and not ring_up and not pinky_up:
            eraser_center = (
                (hand.index_tip.x + hand.middle_tip.x) // 2,
                (hand.index_tip.y + hand.middle_tip.y) // 2
            )
            return GestureResult(
                type=GestureType.ERASER,
                position=eraser_center,
                confidence=0.95,
                fingers_up=fingers,
                details={"scissors_pose": True}
            )

        # Rule 4: Draw Gesture (Index finger UP, Middle, Ring, Pinky DOWN)
        if index_up and not middle_up and not ring_up and not pinky_up:
            return GestureResult(
                type=GestureType.DRAW,
                position=index_pos,
                confidence=0.98,
                fingers_up=fingers,
                details={"pointing": True}
            )

        # Rule 5: Save Gesture (Closed Fist: no fingers extended up)
        if not index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
            return GestureResult(
                type=GestureType.SAVE,
                position=hand.wrist.position,
                confidence=0.85,
                fingers_up=fingers,
                details={"fist": True}
            )

        # Default IDLE state
        return GestureResult(
            type=GestureType.IDLE,
            position=index_pos if index_up else None,
            confidence=0.5,
            fingers_up=fingers
        )
