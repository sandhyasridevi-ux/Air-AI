"""Color definitions and palette utilities."""

from typing import Dict, List, Tuple


class Colors:
    """BGR Color constants for OpenCV rendering."""

    RED: Tuple[int, int, int] = (0, 0, 255)
    GREEN: Tuple[int, int, int] = (0, 255, 0)
    BLUE: Tuple[int, int, int] = (255, 0, 0)
    YELLOW: Tuple[int, int, int] = (0, 255, 255)
    CYAN: Tuple[int, int, int] = (255, 255, 0)
    MAGENTA: Tuple[int, int, int] = (255, 0, 255)
    WHITE: Tuple[int, int, int] = (255, 255, 255)
    BLACK: Tuple[int, int, int] = (0, 0, 0)
    ORANGE: Tuple[int, int, int] = (0, 165, 255)
    PURPLE: Tuple[int, int, int] = (128, 0, 128)
    DARK_GRAY: Tuple[int, int, int] = (40, 40, 40)
    LIGHT_GRAY: Tuple[int, int, int] = (200, 200, 200)

    _NAME_MAP: Dict[Tuple[int, int, int], str] = {
        (0, 0, 255): "RED",
        (0, 255, 0): "GREEN",
        (255, 0, 0): "BLUE",
        (0, 255, 255): "YELLOW",
        (255, 255, 0): "CYAN",
        (255, 0, 255): "MAGENTA",
        (255, 255, 255): "WHITE",
        (0, 0, 0): "BLACK",
        (0, 165, 255): "ORANGE",
        (128, 0, 128): "PURPLE",
    }

    @classmethod
    def get_name(cls, bgr: Tuple[int, int, int]) -> str:
        """Get color name string from BGR tuple."""
        return cls._NAME_MAP.get(bgr, f"BGR{bgr}")


class ColorPalette:
    """Palette manager containing standard active selection colors."""

    DEFAULT_COLORS: List[Tuple[Tuple[int, int, int], str]] = [
        (Colors.RED, "RED"),
        (Colors.GREEN, "GREEN"),
        (Colors.BLUE, "BLUE"),
        (Colors.YELLOW, "YELLOW"),
        (Colors.MAGENTA, "MAGENTA"),
        (Colors.WHITE, "WHITE"),
    ]
