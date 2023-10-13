from __future__ import annotations

import time
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from code_detection.base import DetectorBase


def create_tester(detector: type[DetectorBase]) -> Callable[[str, str], None]:
    test_counter = 0

    def test(text: str, expected_result: str) -> None:
        nonlocal test_counter
        test_counter += 1

        time_before = time.perf_counter_ns()
        actual_result = detector(text).debug()
        execution_time_ns = time.perf_counter_ns() - time_before
        execution_time_ms = execution_time_ns / 1_000_000

        if actual_result != expected_result:
            print(
                f"  TEST #{test_counter} FAILED in {execution_time_ms:.4f} milliseconds",
            )
            print(f"    - Expected: {expected_result!r}")
            print(f"    -   Actual: {actual_result!r}")
        else:
            print(
                f"  TEST #{test_counter} SUCCEEDED in {execution_time_ms:.4f} milliseconds",
            )

    return test
