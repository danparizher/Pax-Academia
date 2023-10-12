from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .python import PythonDetector

if TYPE_CHECKING:
    from .base import DetectedSection, DetectorBase

DETECTOR_CLASSES: list[type[DetectorBase]] = [
    PythonDetector,
    # More languages coming soon!
]

formatting_example_image_path = Path(__file__).parent / "formatting-example.gif"


def detect(text: str) -> tuple[str, tuple[DetectedSection, ...]] | None:
    detectors = [detector_class(text) for detector_class in DETECTOR_CLASSES]
    best_match = max(
        detectors,
        key=lambda d: (d.probable_lines_of_code, d.lines_of_code),
    )

    if best_match.lines_of_code == 0:
        return None

    return best_match.language, best_match.detect()
