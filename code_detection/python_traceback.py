import re

from .python import NAME, PythonDetector

COMMON_ERROR_CLASSES = [
    # from https://docs.python.org/3/library/exceptions.html
    "Exception",
    "ArithmeticError",
    "BufferError",
    "LookupError",
    "AssertionError",
    "AttributeError",
    "EOFError",
    "GeneratorExit",
    "ImportError",
    "ModuleNotFoundError",
    "IndexError",
    "KeyError",
    "KeyboardInterrupt",
    "MemoryError",
    "NameError",
    "NotImplementedError",
    "OSError",
    "OverflowError",
    "RecursionError",
    "ReferenceError",
    "RuntimeError",
    "StopIteration",
    "StopAsyncIteration",
    "SyntaxError",
    "IndentationError",
    "TabError",
    "SystemError",
    "SystemExit",
    "TypeError",
    "UnboundLocalError",
    "UnicodeError",
    "UnicodeEncodeError",
    "UnicodeDecodeError",
    "UnicodeTranslateError",
    "ValueError",
    "ZeroDivisionError",
    # a few of the more common OSErrors
    "FileExistsError",
    "FileNotFoundError",
    "IsADirectoryError",
    "NotADirectoryError",
    "PermissionError",
    "TimeoutError",
]

LINE_PATTERNS = [
    re.compile(r"^Traceback\s*\(\s*most\s*recent\s*call\s*last\s*\)", re.IGNORECASE),
    re.compile(
        rf"^File.*,\s*line\s*\d+(,\s*in\s*(?:<[^<>]+>|{NAME}))?$",
        re.IGNORECASE,
    ),
    re.compile(rf"^({'|'.join(COMMON_ERROR_CLASSES)})(:|$)"),
    re.compile(
        r"^During handling of the above exception, another exception occurred:?$",
    ),
    re.compile(
        r"^The above exception was the direct cause of the following exception:?$",
    ),
    re.compile(r"^\[Previous line repeated \d+ more times\]$"),
    re.compile(r"^\^+$"),
]


class PythonTracebackDetector(PythonDetector):
    @property
    def language(self) -> str:
        # no idea what language "1c" is, but it correctly highlights paths + numbers
        # https://highlightjs.org/demo
        return "1c"

    def line_is_probably_code(self, line: str) -> bool:
        if super().line_is_probably_code(line):
            return True

        line = line.strip()
        return any(pattern.search(line) for pattern in LINE_PATTERNS)
