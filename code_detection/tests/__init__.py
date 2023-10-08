from . import base, python


def run() -> None:
    print("Running tests for code_detection.base")
    base.run()

    print("\nRunning tests for code_detection.python")
    python.run()
