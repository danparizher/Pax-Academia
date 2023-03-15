"""
This file should be used to migrate the db from its current state to the
new state. This file should only be used once.
"""

import base64

def b64ify(x: str) -> str:
    return base64.b64encode(x.encode()).decode()


def deb64ify(y: str) -> str:
    return base64.b64decode(y.encode()).decode()