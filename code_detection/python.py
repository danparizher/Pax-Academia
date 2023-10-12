from __future__ import annotations

import re

from .base import DetectorBase

KEYWORDS = [
    "and",
    "as",
    "assert",
    "async",
    "await",
    "break",
    "class",
    "continue",
    "def",
    "del",
    "elif",
    "else",
    "except",
    "False",
    "finally",
    "for",
    "from",
    "global",
    "if",
    "import",
    "in",
    "is",
    "lambda",
    "None",
    "nonlocal",
    "not",
    "or",
    "pass",
    "raise",
    "return",
    "True",
    "try",
    "while",
    "with",
    "yield",
]
NOT_KEYWORD_LOOKBEHIND = "".join(f"(?<!{keyword})" for keyword in KEYWORDS)

NAME = rf"[a-zA-Z_][a-zA-Z_0-9]*{NOT_KEYWORD_LOOKBEHIND}"
COMMA_SEP_NAMES = rf"({NAME}\s*,\s*)*{NAME}"
CONTAINER_OPENER = r"(\(|\[|\{)"
CONTAINER_CLOSER = r"(\)|\]|\})"
NAME_OR_CONTAINER = rf"(({NAME})|{CONTAINER_OPENER}|{CONTAINER_CLOSER})"
COMMA_SEP_TOKEN = rf"({NAME_OR_CONTAINER}\s*,\s*)*{NAME_OR_CONTAINER}"
OPERATOR = r"(\+|\-|\/|\*|\/\/|\@|\&|\||\~|\^)"
CLAUSE_END = r"(\(|\[|:)$"

LINE_PATTERNS = [  # note that lines will first be stripped!
    re.compile(r"^assert\b"),
    re.compile(r"^async\s+(def|for|with)\b"),
    re.compile(rf"\bawait[\(\s]+{NAME}"),
    re.compile(r"^(break|continue|pass)$"),
    re.compile(rf"^class\s+{NAME}\s*(\(|:)"),
    re.compile(rf"^def\s+{NAME}\s*\("),
    re.compile(rf"^del\s+{NAME}"),
    re.compile(rf"^elif.*{CLAUSE_END}"),
    re.compile(r"^else\s*:$"),
    re.compile(rf"^except.*{CLAUSE_END}"),
    re.compile(r"^finally\s*:$"),
    re.compile(r"^from\b"),
    re.compile(rf"for\b\s*{COMMA_SEP_TOKEN}\s*in.+(\(|\[|\{{|{NAME})$"),
    re.compile(rf"^(global|nonlocal)\s+{COMMA_SEP_NAMES}"),
    re.compile(rf"^if.*{CLAUSE_END}"),
    re.compile(r"^import\b"),
    re.compile(r"\blambda.*:"),
    re.compile(r"^raise\b"),
    re.compile(r"^return\b"),
    re.compile(r"^try\s*:$"),
    re.compile(rf"^while.*{CLAUSE_END}"),
    re.compile(rf"^with.*{CLAUSE_END}"),
    re.compile(r"^yield\b"),
    re.compile(r"^#"),
    re.compile(
        rf"^({CONTAINER_OPENER}|\s)*(\*\s*{NAME}\s*,)?{COMMA_SEP_NAMES}(\s*,\s*\*\s*{NAME}\s*)?({CONTAINER_CLOSER}|\s)*{OPERATOR}?=",
    ),
    re.compile(rf"\.\s*{NAME}\s*{OPERATOR}?="),
    re.compile(rf"\.\s*{NAME}\s*\("),
    re.compile(rf"^{NAME}\s*\("),
    re.compile(rf"^({CONTAINER_CLOSER}|{CONTAINER_OPENER}|\s)+$"),
    re.compile(rf"^@{NAME}"),
    re.compile(r"\).*:$"),
    re.compile(r"\bif\b.*\belse\b"),
    re.compile(r"^\.\.\.$"),
    re.compile(r"\b(list|tuple|set|dict)\["),
    # The following are intentionally disabled because their usage is so common in English
    # re.compile(r"\band\b"),
    # re.compile(r"\bas\b"),
    # re.compile(r"\bin\b"),
    # re.compile(r"\bis\b"),
    # re.compile(r"\bor\b"),
    # re.compile(r"\bnot\b"),
]

LINE_PATTERNS_NO_STRIP = [  # text will NOT be stripped before testing these patterns
    re.compile(
        rf"^\s+{CONTAINER_OPENER}*\s*{COMMA_SEP_NAMES}\s*{CONTAINER_CLOSER}*\s*$",
    ),
]

PLAUSIBLE_LINE_PATTERNS = [
    re.compile(rf"""((?<!'')'|(?<!"")"|,|\d|{OPERATOR})$"""),
]


class PythonDetector(DetectorBase):
    @property
    def language(self) -> str:
        return "python"

    def block_is_probably_code(self: PythonDetector, block: str) -> bool:
        return (
            re.match("^[brf]*('''|\"\"\").*('''|\"\"\")", block.strip(), re.DOTALL)
            is not None
        )

    def line_is_probably_code(self: PythonDetector, line: str) -> bool:
        if any(pattern.search(line) for pattern in LINE_PATTERNS_NO_STRIP):
            return True

        line = line.strip()
        return any(pattern.search(line) for pattern in LINE_PATTERNS)

    def line_is_plausibly_code(self: PythonDetector, line: str) -> bool:
        if super().line_is_plausibly_code(line):
            return True

        line = line.strip()
        return any(pattern.search(line) for pattern in PLAUSIBLE_LINE_PATTERNS)
