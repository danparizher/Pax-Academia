from __future__ import annotations

# Note: this file is currently unused
# TODO: update it to use regex like python.py
from .base import DetectorBase

# unique starting keywords for java that don't appear in other languages
LINE_STARTING_KEYWORDS = (
    "abstract ",
    "assert ",
    "boolean ",
    "break",
    "break;",
    "byte ",
    "case ",
    "catch ",
    "char ",
    "class ",
    "continue",
    "default ",
    "do ",
    "double ",
    "else ",
    "enum ",
    "extends ",
    "final ",
    "finally ",
    "float ",
    "for ",
    "if ",
    "implements ",
    "import ",
    "instanceof ",
    "int ",
    "interface ",
    "long ",
    "native ",
    "new ",
    "null",
    "package ",
    "private ",
    "protected ",
    "public ",
    "return",
    "short ",
    "static ",
    "strictfp ",
    "super ",
    "switch ",
    "synchronized ",
    "this",
    "throw ",
    "throws ",
    "transient ",
    "try ",
    "void ",
    "volatile ",
    "while ",
    "//",
)


class JavaDetector(DetectorBase):
    @property
    def language(self) -> str:
        return "java"

    def line_is_probably_code(self: JavaDetector, line: str) -> bool:
        return (
            (line.startswith(("  ", "\t")) and not line.isspace())
            or line.rstrip().endswith((";", "{", "}"))
            or line.lstrip().startswith(LINE_STARTING_KEYWORDS)
        )
