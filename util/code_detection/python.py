import re

from .base import DetectorBase

# not including those which must end with a `:` anyway
# note that the trailing space is important!
LINE_STARTING_KEYWORDS = (
    "assert ",
    "break",
    "continue",
    "del ",
    "from ",
    "global ",
    "import ",
    "nonlocal ",
    "pass",
    "raise",
    "return",
    "yield",
)


class PythonDetector(DetectorBase):
    @property
    def language(self) -> str:
        return "python"

    def line_is_probably_code(self, line: str) -> bool:
        return (
            (line.startswith(("  ", "\t")) and not line.isspace())
            or line.rstrip().endswith((":", ")", ","))
            or line.lstrip().startswith(LINE_STARTING_KEYWORDS)
            or re.match(r"\s*[a-zA-Z_][a-zA-Z_0-9]*\s*=", line) is not None
        )
