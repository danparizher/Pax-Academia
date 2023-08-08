from .base import DetectorBase


class JavaDetector(DetectorBase):
    @property
    def language(self) -> str:
        return "java"

    def line_is_probably_code(self, line: str) -> bool:
        return (
            (line.startswith(("  ", "\t")) and not line.isspace())
            or line.rstrip().endswith((";", "{", "}"))
            or line.lstrip().startswith(("public", "private", "class"))  # TODO
        )
