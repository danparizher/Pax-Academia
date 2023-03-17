# !SKA#0001 24/10/2022

import datetime


class Log:
    def __init__(self, message: str) -> None:
        with open("log.txt", "a", encoding="utf-8") as log_file:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            now_str: str = now.strftime("%Y-%m-%d %H:%M:%S")
            log_file.write(f"{now_str} - {message}\n")
