from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class Classification(Enum):
    PLAIN_TEXT = "p"
    CODE = "c"


@dataclass(frozen=True)
class DetectedSection:
    classification: Classification
    lines: tuple[str, ...]
    line_probability: tuple[bool, ...]  # True if probable, False if plausible

    @property
    def is_plain_text(self) -> bool:
        return self.classification is Classification.PLAIN_TEXT

    @property
    def is_code(self) -> bool:
        return self.classification is Classification.CODE

    @property
    def text(self) -> str:
        # there is little to no purpose for blank lines at the start or end of a section
        lines = list(self.lines)
        for end in (0, -1):
            while lines and not lines[end] or lines[end].isspace():
                del lines[end]

        return "\n".join(lines)

    @property
    def probable_lines_of_code(self) -> int:
        return sum(self.line_probability)

    def debug(self) -> str:
        """
        A simple string that describes the detection result. Useful for testing.
        - "8p" => 8 lines of plain text
        - "13c" => 13 lines of code
        """
        return f"{len(self.lines)}{self.classification.value}"


class DetectorBase(ABC):
    def __init__(self, text: str) -> None:
        self.text = text

    @property
    @abstractmethod
    def language(self) -> str:
        """
        The language that this Detector detects. Should be compatible with discord markdown codeblocks.
        Specifically, f"```{detector.language}\n{code}```" should enable correct syntax highlighting.
        """

    @property
    def min_code_lines_in_a_row(self) -> int:
        """
        The number of lines in a row that need to be code for it to be considered a "code section".
        For example, if this property returns 5 but only 3 lines of code in a row are detected,
        those lines will be categorized as plain text.
        """
        return 3

    @property
    def min_plain_text_lines_in_a_row(self) -> int:
        """
        Similar to `min_code_lines_in_a_row` but for plain text.
        This threshold *does not apply* to the beginning or end of the text. For example if this property
        returns 3, but there is only 2 lines of plain text at the *beginning of the text*, it will still
        be categorized as plain text.
        Intentionally left very low because your `line_is_probably_code` should be able to detect 100% of lines!
        Only increase if your code matcher frequently misses code lines.
        """
        return 2

    @abstractmethod
    def line_is_probably_code(self, line: str) -> bool:
        """
        Returns True if an only if the line of text is most likely code, with high certainty.
        For example, the line "class DetectorBase(ABC):" is 'probably code'.
        This method is used to tell when plain text stops and code begins.
        """

    def block_is_probably_code(self, block: str) -> bool:
        """
        Same as `line_is_probably_code` except processes multiple lines at once.
        This is called at the end with all of the plain-text sections, and if True,
        the plain-text block is converted into a code section. Useful to detect multiline comments!
        """
        return False

    def line_is_plausibly_code(self, line: str) -> bool:
        """
        Returns True if an only if the line of text _could_ be code (but could also not be).
        For example, a blank line is 'plausibly code'.
        This method is used to tell when code stops and plain text begins.
        NOTE: There is no need to duplicate checks from `line_is_probably_code`!
        """
        # Default implementation provided because this should be pretty common in all languages
        return not line or line.isspace() or line.startswith("  ")

    def classify_line(
        self,
        previous_classification: Classification,
        line: str,
    ) -> tuple[Classification, bool]:
        """
        Classifies the line within the context of the previous line.
        Lines immediately following a code line are held to a lower standard for code matching.
        Also returns whether or not the classification is probable or plausible.
        """
        is_code = self.line_is_probably_code(line)
        probable = True
        if not is_code and previous_classification is Classification.CODE:
            is_code = self.line_is_plausibly_code(line)
            probable = False

        return Classification.CODE if is_code else Classification.PLAIN_TEXT, probable

    def classify_lines(self) -> list[DetectedSection]:
        """
        Simply classifies each line of the text without applying any section-size limits.
        """
        lines = self.text.splitlines()
        sections: list[DetectedSection] = []

        # special case for first line
        line = lines.pop(0)
        if self.line_is_probably_code(line):
            current_section = DetectedSection(
                classification=Classification.CODE,
                lines=(line,),
                line_probability=(True,),
            )
        else:
            current_section = DetectedSection(
                classification=Classification.PLAIN_TEXT,
                lines=(line,),
                line_probability=(True,),
            )

        # rest of the lines...
        for line in lines:
            classification, probable = self.classify_line(
                current_section.classification,
                line,
            )
            if classification != current_section.classification:
                sections.append(current_section)
                current_section = DetectedSection(
                    classification=classification,
                    lines=(line,),
                    line_probability=(probable,),
                )
            else:
                current_section = DetectedSection(
                    classification=classification,
                    lines=(*current_section.lines, line),
                    line_probability=(*current_section.line_probability, probable),
                )
        sections.append(current_section)

        # remove blank lines from the end of code blocks and
        # move them to succeeding plain text sections
        for i in range(len(sections) - 1):
            section = sections[i]
            if not section.is_code:
                continue

            n_blank_lines = 0
            while n_blank_lines < len(section.lines):
                line = section.lines[-1 - n_blank_lines]
                if line and not line.isspace():
                    break
                n_blank_lines += 1

            if n_blank_lines > 0:
                sections[i] = DetectedSection(
                    classification=Classification.CODE,
                    lines=section.lines[:-n_blank_lines],
                    line_probability=current_section.line_probability[:-n_blank_lines],
                )
                sections[i + 1] = DetectedSection(
                    classification=Classification.PLAIN_TEXT,
                    lines=section.lines[-n_blank_lines:] + sections[i + 1].lines,
                    line_probability=(
                        section.line_probability[-n_blank_lines:]
                        + sections[i + 1].line_probability
                    ),
                )

        return sections

    def section_too_short(self, section: DetectedSection) -> bool:
        """
        Utility method to check if the section is shorter than the required minimums.
        """
        if section.is_code:
            return len(section.lines) < self.min_code_lines_in_a_row
        return len(section.lines) < self.min_plain_text_lines_in_a_row

    def reduce_section_group(self, sections: list[DetectedSection]) -> DetectedSection:
        """
        Simply merges a group of sections into a single section.
        The resultant `classification` is a simple MODE of the input sections' lines.
        """
        lines_of_code = sum(len(s.lines) for s in sections if s.is_code)
        lines_of_plain_text = sum(len(s.lines) for s in sections if s.is_plain_text)

        return DetectedSection(
            classification=(
                Classification.CODE
                if lines_of_code >= lines_of_plain_text
                else Classification.PLAIN_TEXT
            ),
            lines=tuple(line for section in sections for line in section.lines),
            line_probability=tuple(
                lp for section in sections for lp in section.line_probability
            ),
        )

    def merge_short_sections(
        self,
        sections: list[DetectedSection],
    ) -> list[DetectedSection]:
        """
        Merges together sections which are too short
        For example in this input:
        3 code lines
        2 plain text line
        1 code line
        8 plain text lines

        Will produce this output:
        6 code lines
        8 plain text lines

        Note that this code will never convert plain text at the start or end of the text,
        because it is extremely common to have plaintext before and after some code.

        So for example this input:
        1 plain text line
        3 code lines
        1 plain text line
        4 code lines
        1 plain text line

        Will return:
        1 plain text line
        8 code lines
        1 plain text line
        """

        if (
            not sections
            or sum(len(s.lines) for s in sections) < self.min_code_lines_in_a_row
        ):
            return [
                DetectedSection(
                    classification=Classification.PLAIN_TEXT,
                    lines=tuple(line for section in sections for line in section.lines),
                    line_probability=tuple(
                        lp for section in sections for lp in section.line_probability
                    ),
                ),
            ]

        # firstly, merge adjacent short sections into single sections
        # i.e. this:
        # 10 code
        # 2 plain
        # 2 code
        # 1 plain
        # 3 code
        # 12 plain
        #
        # is merged down to this:
        # 10 code
        # 8 code
        # 12 plain
        i = 0
        merged_short_sections: list[DetectedSection] = []

        # don't touch plain text at the start
        if sections[i].is_plain_text:
            merged_short_sections.append(sections[i])
            i += 1

        # middle sections are all normal
        adjacent_short_sections_group: list[DetectedSection] = []
        while i < len(sections) - 1:
            section = sections[i]

            if self.section_too_short(section):
                adjacent_short_sections_group.append(section)
            else:
                merged_short_sections.append(
                    self.reduce_section_group(adjacent_short_sections_group),
                )
                adjacent_short_sections_group.clear()
                merged_short_sections.append(section)

            i += 1

        # don't touch plain text at the end
        if i >= len(sections) or sections[i].is_plain_text:
            pass
        elif self.section_too_short(sections[i]):
            adjacent_short_sections_group.append(sections[i])

        if adjacent_short_sections_group:
            merged_short_sections.append(
                self.reduce_section_group(adjacent_short_sections_group),
            )
            adjacent_short_sections_group.clear()

        if i < len(sections) and (
            sections[i].is_plain_text or not self.section_too_short(sections[i])
        ):
            merged_short_sections.append(sections[i])

        # secondly, merge adjacent & similar sections
        # i.e. this:
        # 10 code
        # 8 code
        # 12 plain
        #
        # will merge into:
        # 18 code
        # 12 plain
        merged_similar_sections: list[DetectedSection] = []
        similar_section_group: list[DetectedSection] = [merged_short_sections[0]]
        for section in merged_short_sections[1:]:
            if section.classification != similar_section_group[0].classification:
                merged_similar_sections.append(
                    self.reduce_section_group(similar_section_group),
                )
                similar_section_group.clear()

            similar_section_group.append(section)
        merged_similar_sections.append(self.reduce_section_group(similar_section_group))

        # thirdly, merge sections that are still too small
        # i.e. this:
        # 10 code
        # 2 plain
        # 13 code
        # 12 plain
        # 3 code
        #
        # will become:
        # 25 code
        # 15 plain
        #
        # note:
        # - we still will not merge plaintext sections at the start of end of the text
        # - we can assume that section classifications will be alternating (from prev. step)
        merged_sections = merged_similar_sections.copy()

        # special handling to merge code at the top
        if len(merged_sections) >= 2 and merged_sections[0].is_code:
            before, after, *_ = merged_sections
            if self.section_too_short(before):
                merged_sections[:2] = (
                    DetectedSection(
                        classification=Classification.PLAIN_TEXT,
                        lines=before.lines + after.lines,
                        line_probability=(
                            before.line_probability + after.line_probability
                        ),
                    ),
                )

        # special handling to merge code at the bottom
        if len(merged_sections) >= 2 and merged_sections[-1].is_code:
            *_, before, after = merged_sections
            if self.section_too_short(after):
                merged_sections[-2:] = (
                    DetectedSection(
                        classification=Classification.PLAIN_TEXT,
                        lines=before.lines + after.lines,
                        line_probability=(
                            before.line_probability + after.line_probability
                        ),
                    ),
                )

        # merge middle sections normally
        i = 1
        while i < len(merged_sections) - 1:
            section = merged_sections[i]

            if not self.section_too_short(section):
                i += 1
                continue

            merged_sections.insert(
                i - 1,
                self.reduce_section_group(merged_sections[i - 1 : i + 2]),
            )
            del merged_sections[i : i + 3]

        return merged_sections

    def convert_plain_text_to_code(
        self,
        sections: list[DetectedSection],
    ) -> list[DetectedSection]:
        """
        Converts plain-text sections into code sections based on `block_is_probably_code`.
        Edits the list IN-PLACE.
        """
        i = 1
        while i < len(sections) - 1:
            section = sections[i]
            if section.is_plain_text and self.block_is_probably_code(section.text):
                sections[i] = DetectedSection(
                    classification=Classification.CODE,
                    lines=section.lines,
                    line_probability=(True,) * len(section.lines),
                )
                sections[i - 1 : i + 2] = (
                    self.reduce_section_group(sections[i - 1 : i + 2]),
                )
            else:
                i += 1

        return sections

    def detect_uncached(self) -> list[DetectedSection]:
        """
        Breaks down the provided text into sections which are or are not code.
        """
        return self.convert_plain_text_to_code(
            self.merge_short_sections(self.classify_lines()),
        )

    def detect(self) -> tuple[DetectedSection, ...]:
        """
        Same as detect_uncached, except the results will be cached for later use.
        Returns a tuple so that you don't accidentally modify the cache.
        """
        if not hasattr(self, "_cached_detection_result"):
            self._cached_detection_result = tuple(self.detect_uncached())
        return self._cached_detection_result

    @property
    def lines_of_code(self) -> int:
        """
        The total number of lines of code that were detected.
        """
        return sum(len(s.lines) for s in self.detect() if s.is_code)

    @property
    def probable_lines_of_code(self) -> float:
        """
        The number of lines that are probably code, as opposed to
        lines that are plausibly code.
        """
        return sum(
            section.probable_lines_of_code
            for section in self.detect()
            if section.is_code
        )

    def debug(self) -> str:
        """
        A simple string that describes the detection result. Useful for testing.
        For example, the string "2p 15c 8p" describes a result of:
        - two lines of plain text
        - fifteen lines of code
        - eight lines of plain text
        """
        return " ".join(section.debug() for section in self.detect())
