from textwrap import dedent

from ..python import PythonDetector
from .helper import create_tester

test = create_tester(PythonDetector)


def run():
    print("code-only")
    test(
        dedent(
            """\
            age = int(input("How old are you?"))
            if age >= 18:
                print("You're old enough to vote in the US")
            else:
                print("You're too young to vote in the US")\
            """
        ),
        "5c",
    )
    test(
        dedent(
            """\
            import matplotlib.pyplot as plt

            def fib(n):
                if n <= 1:
                    return 1
                else:
                    return fib(n - 1) + fib(n - 2)

            x = list(range(10))
            y = []
            for xi in x:
                y.append(fib(xi))

            plt.scatter(x, y)
            plt.show()\
            """
        ),
        "15c",
    )

    print("mixed code and english")
    test(
        dedent(
            """\
            hey guys does anybody know python
            my code doesn't work and i need help....

            age = input("How old are you?")
            if age >= 18:
                print("You can vote!")
            
            i get this error for no reason, my code is fine
            TypeError: '>=' not supported between instances of 'str' and 'int'\
            """
        ),
        "3p 3c 3p",
    )

    test(
        dedent(
            """\
            can someone review my code please

            from pathlib import Path

            effects_path = Path(__file__).parent / "effects"
            effects_path.mkdir(exist_ok=True)

            Effect: TypeAlias = tuple[float, dict]
            def read_all(effect: str) -> list[Effect]:
                file_path = effects_path / f"{effect}.json"

                if file_path.exists():
                    with open(file_path) as f:
                        return json.load(f)
                else:
                    return []
            
            specifically I'm wondering if there's a better way deal with the file not existing
            is this better?
            try:
                with open(file_path) as f:
                    return json.load(f)
            except FileNotFoundError:
                return []
            please ping me to reply, thanks!\
            """
        ),
        "2p 14c 3p 5c 1p",
    )

    # these tests will expand as we fix issues found on production
    print("one-off cases from false positives in production")
    test(
        dedent(
            """\
            thanks again for these suggestions, i added most of the tkinter logic and it's lovely and easy

            i havent yet added the persistent storage and im not home and asking in advance - for sqlite, do i need like an external server or smth (im not too well-versed with DBs, i only know this from working with mysql)
            cause my intention is just to start my python app without additional servers or anything\
            """
        ),
        "4p",
    )
