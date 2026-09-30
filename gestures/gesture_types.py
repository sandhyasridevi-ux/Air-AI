"""Gesture types and data structures."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class GestureType(str, Enum):
    """Enumeration of supported air gestures."""

    IDLE = "IDLE"
    DRAW = "DRAW"
    ERASER = "ERASER"
    COLOR_SELECT = "COLOR_SELECT"
    CLEAR = "CLEAR"
    SAVE = "SAVE"


@dataclass
class GestureResult:
    """Structured result of gesture recognition pipeline."""

    type: GestureType
    position: Optional[Tuple[int, int]] = None  # Operating coordinate (e.g. index tip)
    confidence: float = 1.0
    fingers_up: List[bool] = field(default_factory=lambda: [False, False, False, False, False])
    details: Dict = field(default_factory=dict)
