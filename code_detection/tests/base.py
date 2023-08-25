from code_detection.base import DetectorBase

from .helpers import create_tester


class SimpleDetector(DetectorBase):
    @property
    def language(self) -> str:
        return "test"

    def line_is_probably_code(self, line: str) -> bool:
        return "code" in line

    def line_is_plausibly_code(self, line: str) -> bool:
        return not line or line.isspace()


test_counter = 0


test = create_tester(SimpleDetector)


def run() -> None:
    print("Testing code-only scenarios...")

    test(
        """\
        code\
        """,
        "1p",  # too short to be code
    )

    test(
        """\
        code
        code
        code
        code\
        """,
        "4c",
    )

    test(
        """\
        code
        code
        code
        code
        code
        code
        code\
        """,
        "7c",
    )

    test(
        """\
        code
        code

        code
        code\
        """,
        "5c",
    )

    test(
        """\
        code
        code






        code
        code\
        """,
        "10c",
    )

    test(
        """\
        code
        code






        code
        code\
        """,
        "10c",
    )

    test(
        """\
        code

        code

        code

        code\
        """,
        "7c",
    )

    print("Testing plaintext-only scenarios...")

    test(
        """\
        text\
        """,
        "1p",
    )

    test(
        """\
        text
        text\
        """,
        "2p",
    )

    test(
        """\
        text
        text
        text\
        """,
        "3p",
    )

    test(
        """\
        text
        text
        text
        text
        text\
        """,
        "5p",
    )

    test(
        """\
        text
        text

        text
        text\
        """,
        "5p",
    )

    test(
        """\
        text



        text\
        """,
        "5p",
    )

    test(
        """\
        text


        text


        text\
        """,
        "7p",
    )

    test(
        """\
        text







        text







        text\
        """,
        "17p",
    )

    print("Testing mixed scenarios...")

    test(
        """\
        code
        code
        code
        code
        code
        text
        text
        text
        text
        text\
        """,
        "5c 5p",
    )

    test(
        """\
        code



        code
        text
        text
        text
        text
        text\
        """,
        "5c 5p",
    )

    test(
        """\
        code
        text
        code
        text
        code
        text
        code\
        """,
        "7c",
    )

    test(
        """\
        text
        code
        text
        code
        text
        code
        text
        code\
        """,
        "1p 7c",
    )

    test(
        """\
        code
        text
        code
        text
        code
        text
        code
        text\
        """,
        "7c 1p",
    )

    test(
        """\
        text
        code
        text
        code
        text
        code
        text
        code
        text\
        """,
        "1p 7c 1p",
    )

    test(
        """\
        text

        code
        code
        code

        text

        code
        code
        code

        text\
        """,
        "2p 3c 3p 3c 2p",
    )

    test(
        """\
        text
        text
        text


        code
        code
        code
        code
        code
        code
        code
        code
        code
        code
        code
        code
        code

        text
        text
        text

        code
        code
        code
        code
        code
        code
        code
        code
        code

        text
        text\
        """,
        "5p 13c 5p 9c 3p",
    )
