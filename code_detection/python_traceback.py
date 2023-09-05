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
    re.compile(rf"^Traceback\s*\(\s*most\s*recent\s*call\s*last\s*\)", re.IGNORECASE),
    re.compile(
        rf"^File.*,\s*line\s*\d+(,\s*in\s*(?:<[^<>]+>|{NAME}))?$:",
        re.IGNORECASE,
    ),
    re.compile(rf"^({'|'.join(COMMON_ERROR_CLASSES)})(:|$)"),
]


class PythonTracebackDetector(PythonDetector):
    @property
    def language(self) -> str:
        return "text"

    def line_is_probably_code(self, line: str) -> bool:
        if super().line_is_probably_code(line):
            return True

        line = line.strip()
        return any(pattern.search(line) for pattern in LINE_PATTERNS)
