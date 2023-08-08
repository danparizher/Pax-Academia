from typing import TYPE_CHECKING, Type

from .java import JavaDetector
from .python import PythonDetector

if TYPE_CHECKING:
    from base import DetectedSection, DetectorBase

DETECTOR_CLASSES: list[Type[DetectorBase]] = [
    JavaDetector,
    PythonDetector,
]


def detect(text: str) -> tuple[str, tuple[DetectedSection, ...]] | None:
    detectors = [detector_class(text) for detector_class in DETECTOR_CLASSES]
    best_match = max(detectors, key=lambda d: d.lines_of_code)

    if best_match.lines_of_code == 0:
        return None

    return best_match.language, best_match.detect()
