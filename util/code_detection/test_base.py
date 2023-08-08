assert __name__ == "__main__", "This file must be run directly!"

import time

from base import DetectorBase


class SimpleDetector(DetectorBase):
    @property
    def language(self) -> str:
        return "test"

    def line_is_probably_code(self, line: str) -> bool:
        return "code" in line


test_counter = 0


def test(text: str, expected_result: str) -> None:
    global test_counter
    test_counter += 1

    time_before = time.perf_counter_ns()
    actual_result = SimpleDetector(text).debug()
    execution_time_ns = time.perf_counter_ns() - time_before
    execution_time_ms = execution_time_ns / 1_000_000

    if actual_result != expected_result:
        print(f"TEST #{test_counter} FAILED in {execution_time_ms:.4f} milliseconds")
        print(f"    - Expected: {expected_result!r}")
        print(f"    -   Actual: {actual_result!r}")
    else:
        print(f"TEST #{test_counter} SUCCEEDED in {execution_time_ms:.4f} milliseconds")


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
    "4p",  # too short to be code
)

test(
    """\
    code
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
    "2p 10c 1p",
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
    "5p 14c 4p 10c 2p",
)
