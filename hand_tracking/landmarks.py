"""Hand landmark models and constants."""

from dataclasses import dataclass
from enum import IntEnum
from typing import Dict, List, Optional


class LandmarkID(IntEnum):
    """MediaPipe 21 Hand Landmark Enums."""

    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


@dataclass
class LandmarkPoint:
    """Represents a single 2D/3D hand landmark point."""

    id: int
    x: int  # Pixel X coordinate
    y: int  # Pixel Y coordinate
    z: float = 0.0  # Depth coordinate relative to wrist
    normalized_x: float = 0.0
    normalized_y: float = 0.0

    @property
    def position(self) -> tuple[int, int]:
        """Return (x, y) pixel tuple."""
        return (self.x, self.y)


class HandLandmarks:
    """Wrapper around 21 hand landmark points for convenient access."""

    def __init__(self, points: List[LandmarkPoint], handedness: str = "Right") -> None:
        """Initialize HandLandmarks.

        Args:
            points: List of 21 LandmarkPoint objects.
            handedness: 'Right' or 'Left'.
        """
        self.points: List[LandmarkPoint] = points
        self.handedness: str = handedness
        self._point_map: Dict[int, LandmarkPoint] = {p.id: p for p in points}

    def get_point(self, landmark_id: int | LandmarkID) -> Optional[LandmarkPoint]:
        """Get landmark point by ID."""
        return self._point_map.get(int(landmark_id))

    @property
    def wrist(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.WRIST]

    @property
    def thumb_tip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.THUMB_TIP]

    @property
    def thumb_ip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.THUMB_IP]

    @property
    def index_tip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.INDEX_FINGER_TIP]

    @property
    def index_pip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.INDEX_FINGER_PIP]

    @property
    def index_mcp(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.INDEX_FINGER_MCP]

    @property
    def middle_tip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.MIDDLE_FINGER_TIP]

    @property
    def middle_pip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.MIDDLE_FINGER_PIP]

    @property
    def middle_mcp(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.MIDDLE_FINGER_MCP]

    @property
    def ring_tip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.RING_FINGER_TIP]

    @property
    def ring_pip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.RING_FINGER_PIP]

    @property
    def ring_mcp(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.RING_FINGER_MCP]

    @property
    def pinky_tip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.PINKY_TIP]

    @property
    def pinky_pip(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.PINKY_PIP]

    @property
    def pinky_mcp(self) -> LandmarkPoint:
        return self._point_map[LandmarkID.PINKY_MCP]
