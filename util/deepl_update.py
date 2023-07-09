import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def get_soup(url: str) -> BeautifulSoup:
    r = requests.get(url, timeout=5)
    return BeautifulSoup(r.text, "html.parser")


url = "https://raw.githubusercontent.com/DeepLcom/deepl-python/main/deepl/translator.py"
soup = get_soup(url)


soup = soup.text[
    soup.text.find("class Language:") : soup.text.find("class GlossaryLanguagePair:")
]


string = "return str(language).upper()[0:2]"
start = soup.index(string) + len(string)
soup = soup[start:]

new_format = re.findall(r"([A-Z]+) = \"([a-z]+)\"", soup)
new_format = [
    {"code": code.upper(), "language": language.title()}
    for language, code in new_format
]


def overwrite_deepl_settings(new_format: list[dict[str, str]]) -> None:
    PACKAGE_PATH = ".venv\\Lib\\site-packages\\deepl\\settings.py"
    PAX_PATH = "cogs\\DeepL.py"
    # Updating the settings.py file in the deepl package
    with Path(PACKAGE_PATH).open() as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "SUPPORTED_LANGUAGES" in line:
            start = i
            break

    for i, line in enumerate(lines[start:]):
        if "]" in line:
            end = i + start
            break

    lines[start + 1 : end] = [f"    {language},\n" for language in new_format]
    with Path(PACKAGE_PATH).open("w") as f:
        f.writelines(lines)

    # Updating the available languages in the DeepL cog
    with Path(PAX_PATH).open() as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if "LANGUAGES = [" in line:
            start = i
            break

    for i, line in enumerate(lines[start:]):
        if "]" in line:
            end = i + start
            break

    lines[start + 1 : end] = [
        f'    "{language}",\n'
        for language in [language["language"] for language in new_format]
    ]

    with Path(PAX_PATH).open("w") as f:
        f.writelines(lines)


overwrite_deepl_settings(new_format)
