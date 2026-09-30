"""Image persistence manager for exporting saved artwork."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import cv2
import numpy as np

from utils.logger import get_logger

logger = get_logger("drawing_saver")


class DrawingSaver:
    """Manages saving virtual canvas drawings to PNG image files on disk."""

    def __init__(self, output_dir: str | Path = "saved_drawings") -> None:
        """Initialize DrawingSaver.

        Args:
            output_dir: Directory path where exported artwork will be saved.
        """
        self.output_dir: Path = Path(output_dir)
        self.ensure_directory()

    def ensure_directory(self) -> None:
        """Create target output directory if it does not exist."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create saved drawings directory '{self.output_dir}': {e}")

    def save_drawing(
        self,
        canvas_layer: np.ndarray,
        filename_prefix: str = "drawing",
        save_composite: bool = False,
        composite_frame: Optional[np.ndarray] = None
    ) -> Tuple[bool, str, str]:
        """Save current drawing layer or composite image as PNG file.

        Args:
            canvas_layer: OpenCV BGR canvas drawing array.
            filename_prefix: Prefix for timestamped filename.
            save_composite: If True and composite_frame is provided, save camera composite.
            composite_frame: Optional composite frame to save.

        Returns:
            Tuple of (success_boolean, saved_filepath_string, user_status_message).
        """
        if canvas_layer is None or canvas_layer.size == 0:
            return False, "", "Cannot save empty or invalid canvas image."

        self.ensure_directory()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.png"
        filepath = self.output_dir / filename

        target_image = composite_frame if (save_composite and composite_frame is not None) else canvas_layer

        try:
            success = cv2.imwrite(str(filepath), target_image)
            if success:
                msg = f"Saved drawing successfully to {filepath.name}"
                logger.info(msg)
                return True, str(filepath), msg
            else:
                msg = f"OpenCV failed to write image file to {filepath}"
                logger.error(msg)
                return False, "", msg
        except Exception as e:
            msg = f"Error saving drawing file: {e}"
            logger.error(msg)
            return False, "", msg
