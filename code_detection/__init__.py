from .base import DetectedSection, DetectorBase
from .python import PythonDetector

DETECTOR_CLASSES: list[type[DetectorBase]] = [
    PythonDetector,
    # More languages coming soon!
]


def detect(text: str) -> tuple[str, tuple[DetectedSection, ...]] | None:
    detectors = [detector_class(text) for detector_class in DETECTOR_CLASSES]
    best_match = max(
        detectors, key=lambda d: (d.probable_lines_of_code, d.lines_of_code)
    )

    if best_match.lines_of_code == 0:
        return None

    return best_match.language, best_match.detect()
