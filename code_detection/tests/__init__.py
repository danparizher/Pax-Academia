from . import base, python, python_traceback


def run() -> None:
    print("Running tests for code_detection.base")
    base.run()

    print("\nRunning tests for code_detection.python")
    python.run()

    print("\nRunning tests for code_detection.python_traceback")
    python_traceback.run()
