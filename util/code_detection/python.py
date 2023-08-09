import re

from .base import DetectorBase

# not including those which must end with a `:` anyway
# note that the trailing space is important!
LINE_STARTING_KEYWORDS = (
    "and ",
    "as ",
    "assert ",
    "async ",
    "await ",
    "break ",
    "class ",
    "continue ",
    "def ",
    "del ",
    "elif ",
    "else:",
    "except ",
    "finally ",
    "for ",
    "from ",
    "global ",
    "if ",
    "import ",
    "in ",
    "is ",
    "lambda ",
    "nonlocal ",
    "not ",
    "or ",
    "pass ",
    "raise ",
    "return ",
    "try ",
    "while ",
    "with ",
    "yield ",
    "#",
)


class PythonDetector(DetectorBase):
    @property
    def language(self) -> str:
        return "python"

    @property
    def min_plain_text_lines_in_a_row(self) -> int:
        # Can reduce this to 1 for Python
        # since we're pretty confident that `line_is_probably_code` will
        # match every feasible line of python code
        return 1

    def line_is_probably_code(self, line: str) -> bool:
        return (
            (line.startswith(("  ", "\t")) and not line.isspace())
            or line.rstrip().endswith((":", "(", ")", "[", "]", "{", "}", ","))
            or line.lstrip().startswith(LINE_STARTING_KEYWORDS)
            or re.match(r"\s*[a-zA-Z_][a-zA-Z_0-9]*\s*=", line) is not None
        )
