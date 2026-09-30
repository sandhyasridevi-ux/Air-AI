"""MediaPipe Hand Tracking wrapper and landmark processor."""

import math
from typing import List, Optional, Tuple
import cv2
import mediapipe as mp
import numpy as np

from hand_tracking.landmarks import HandLandmarks, LandmarkID, LandmarkPoint
from utils.logger import get_logger

logger = get_logger("hand_detector")


class HandDetector:
    """Detects 21 3D hand landmarks from OpenCV BGR video frames using MediaPipe."""

    HAND_CONNECTIONS = [
        # Thumb
        (LandmarkID.WRIST, LandmarkID.THUMB_CMC),
        (LandmarkID.THUMB_CMC, LandmarkID.THUMB_MCP),
        (LandmarkID.THUMB_MCP, LandmarkID.THUMB_IP),
        (LandmarkID.THUMB_IP, LandmarkID.THUMB_TIP),
        # Index
        (LandmarkID.WRIST, LandmarkID.INDEX_FINGER_MCP),
        (LandmarkID.INDEX_FINGER_MCP, LandmarkID.INDEX_FINGER_PIP),
        (LandmarkID.INDEX_FINGER_PIP, LandmarkID.INDEX_FINGER_DIP),
        (LandmarkID.INDEX_FINGER_DIP, LandmarkID.INDEX_FINGER_TIP),
        # Middle
        (LandmarkID.INDEX_FINGER_MCP, LandmarkID.MIDDLE_FINGER_MCP),
        (LandmarkID.MIDDLE_FINGER_MCP, LandmarkID.MIDDLE_FINGER_PIP),
        (LandmarkID.MIDDLE_FINGER_PIP, LandmarkID.MIDDLE_FINGER_DIP),
        (LandmarkID.MIDDLE_FINGER_DIP, LandmarkID.MIDDLE_FINGER_TIP),
        # Ring
        (LandmarkID.MIDDLE_FINGER_MCP, LandmarkID.RING_FINGER_MCP),
        (LandmarkID.RING_FINGER_MCP, LandmarkID.RING_FINGER_PIP),
        (LandmarkID.RING_FINGER_PIP, LandmarkID.RING_FINGER_DIP),
        (LandmarkID.RING_FINGER_DIP, LandmarkID.RING_FINGER_TIP),
        # Pinky
        (LandmarkID.RING_FINGER_MCP, LandmarkID.PINKY_MCP),
        (LandmarkID.PINKY_MCP, LandmarkID.PINKY_PIP),
        (LandmarkID.PINKY_PIP, LandmarkID.PINKY_DIP),
        (LandmarkID.PINKY_DIP, LandmarkID.PINKY_TIP),
        (LandmarkID.WRIST, LandmarkID.PINKY_MCP),
    ]

    def __init__(
        self,
        max_hands: int = 1,
        detection_confidence: float = 0.7,
        tracking_confidence: float = 0.7,
    ) -> None:
        """Initialize MediaPipe Hands model.

        Args:
            max_hands: Maximum number of hands to detect.
            detection_confidence: Minimum detection confidence (0.0 to 1.0).
            tracking_confidence: Minimum tracking confidence (0.0 to 1.0).
        """
        self.max_hands: int = max_hands
        self.detection_confidence: float = detection_confidence
        self.tracking_confidence: float = tracking_confidence

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence,
        )

        self._last_primary_position: Optional[Tuple[int, int]] = None

    def detect(self, frame: np.ndarray) -> Optional[HandLandmarks]:
        """Detect hands in frame and return landmark point representation for the primary hand.

        Args:
            frame: OpenCV BGR image array.

        Returns:
            HandLandmarks object if hand detected, otherwise None.
        """
        if frame is None or frame.size == 0:
            return None

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            results = self.hands.process(rgb_frame)
        except Exception as e:
            logger.error(f"MediaPipe processing error: {e}")
            return None

        if not results.multi_hand_landmarks:
            self._last_primary_position = None
            return None

        # Determine primary hand if multiple detected
        primary_index = 0
        if len(results.multi_hand_landmarks) > 1 and self._last_primary_position is not None:
            best_dist = float("inf")
            for idx, hand_lms in enumerate(results.multi_hand_landmarks):
                # Calculate distance between wrist and last position
                wrist_x = int(hand_lms.landmark[0].x * w)
                wrist_y = int(hand_lms.landmark[0].y * h)
                dist = math.hypot(wrist_x - self._last_primary_position[0], wrist_y - self._last_primary_position[1])
                if dist < best_dist:
                    best_dist = dist
                    primary_index = idx

        target_hand = results.multi_hand_landmarks[primary_index]

        # Get handedness string if available
        handedness_str = "Right"
        if results.multi_handedness and len(results.multi_handedness) > primary_index:
            handedness_str = results.multi_handedness[primary_index].classification[0].label

        points: List[LandmarkPoint] = []
        for lm_id, lm in enumerate(target_hand.landmark):
            px = int(lm.x * w)
            py = int(lm.y * h)
            points.append(
                LandmarkPoint(
                    id=lm_id,
                    x=px,
                    y=py,
                    z=lm.z,
                    normalized_x=lm.x,
                    normalized_y=lm.y,
                )
            )

        hand_landmarks = HandLandmarks(points=points, handedness=handedness_str)
        self._last_primary_position = hand_landmarks.wrist.position
        return hand_landmarks

    def draw_landmarks(
        self,
        frame: np.ndarray,
        hand_landmarks: HandLandmarks,
        color_bones: Tuple[int, int, int] = (255, 200, 0),
        color_joints: Tuple[int, int, int] = (0, 255, 255),
    ) -> np.ndarray:
        """Draw aesthetic custom skeleton onto frame.

        Args:
            frame: OpenCV BGR image array.
            hand_landmarks: HandLandmarks object to render.
            color_bones: BGR color tuple for skeleton bones.
            color_joints: BGR color tuple for skeleton joint nodes.

        Returns:
            Image frame with rendered landmarks overlay.
        """
        if hand_landmarks is None or frame is None:
            return frame

        # Draw bone connection lines
        for start_id, end_id in self.HAND_CONNECTIONS:
            p1 = hand_landmarks.get_point(start_id)
            p2 = hand_landmarks.get_point(end_id)
            if p1 and p2:
                cv2.line(frame, p1.position, p2.position, color_bones, 2, cv2.LINE_AA)

        # Draw joint nodes
        for pt in hand_landmarks.points:
            # Highlight index tip distinctly
            if pt.id == LandmarkID.INDEX_FINGER_TIP:
                cv2.circle(frame, pt.position, 8, (0, 0, 255), -1, cv2.LINE_AA)
                cv2.circle(frame, pt.position, 12, (255, 255, 255), 2, cv2.LINE_AA)
            else:
                cv2.circle(frame, pt.position, 4, color_joints, -1, cv2.LINE_AA)

        return frame

    def close(self) -> None:
        """Release MediaPipe resources."""
        if hasattr(self, "hands") and self.hands:
            self.hands.close()
