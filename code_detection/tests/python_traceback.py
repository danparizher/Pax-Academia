from textwrap import dedent

from code_detection.python_traceback import PythonTracebackDetector

from .helpers import create_tester

test = create_tester(PythonTracebackDetector)


def run() -> None:
    print("code-only")
    test(
        dedent(
            """\
            Traceback (most recent call last):
                File "test.py", line 1
            TypeError: unsupported operand type(s) for +: 'int' and 'str'\
            """,
        ),
        "3c",
    )
    test(
        dedent(
            r"""Traceback (most recent call last):
                File "C:\...\Pax-Academia\venv\lib\site-packages\discord\client.py", line 378, in _run_event
                    await coro(*args, **kwargs)
                File "C:\...\Pax-Academia\cogs\detect_code.py", line 133, in on_message
                    if autoformat and (detection_result := code_detection.detect(message.content)):
                File "C:\...\Pax-Academia\code_detection\__init__.py", line 20, in detect
                    best_match = max(
                File "C:\...\Pax-Academia\code_detection\__init__.py", line 22, in <lambda>
                    key=lambda d: (d.probable_lines_of_code, d.lines_of_code),
                File "C:\...\Pax-Academia\code_detection\base.py", line 469, in probable_lines_of_code
                    for section in self.detect()
                File "C:\...\Pax-Academia\code_detection\base.py", line 451, in detect
                    self._cached_detection_result = tuple(self.detect_uncached())
                File "C:\...\Pax-Academia\code_detection\base.py", line 442, in detect_uncached
                    self.merge_short_sections(self.classify_lines()),
                File "C:\...\Pax-Academia\code_detection\base.py", line 136, in classify_lines
                    if self.line_is_probably_code(line):
                File "C:\...\Pax-Academia\code_detection\python_traceback.py", line 70, in line_is_probably_code
                    return any(patern.search(line) for pattern in LINE_PATTERNS)
                File "C:\...\Pax-Academia\code_detection\python_traceback.py", line 70, in <genexpr>
                    return any(patern.search(line) for pattern in LINE_PATTERNS)
                NameError: name 'patern' is not defined\
            """,
        ),
        "22c",
    )

    print("mixed code and english")
    test(
        dedent(
            """\
            help me
            i get an error

            Traceback (most recent call last):
                File "test.py", line 1
            TypeError: unsupported operand type(s) for +: 'int' and 'str'

            what the hell does this mean\
            """,
        ),
        "3p 3c 2p",
    )

    print("chained traceback")
    test(
        dedent(
            r"""\
                Traceback (most recent call last):
                File "C:\...\test.py", line 6, in another_function
                    function()
                File "C:\...\test.py", line 2, in function
                    raise TypeError("No good!")
                TypeError: No good!

                The above exception was the direct cause of the following exception:

                Traceback (most recent call last):
                File "C:\...\test.py", line 10, in <module>
                    another_function()
                File "C:\...\test.py", line 8, in another_function
                    raise ValueError("Really no good!") from e
                ValueError: Really no good!\
            """,
        ),
        "15c",
    )
