import bs4
import requests


def request(word: str) -> bs4.BeautifulSoup:
    url = f"https://www.merriam-webster.com/dictionary/{word}"
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return soup


def define(soup) -> str:
    try:
        definition = soup.find("span", {"class": "dtText"}).text.split(":")[1]
    except (AttributeError, IndexError):
        definition = "No definition found"
    return definition.strip().capitalize()


def phonetisize(soup) -> str:
    try:
        phonetic = soup.find("span", {"class": "pr"}).text.replace(" ", "")
    except (AttributeError, IndexError):
        phonetic = "No phonetic found"
    return phonetic.strip()


def synonymize(soup) -> str:
    try:
        synonyms = soup.find("ul", {"class": "mw-list"}).find_all("li")
        synonyms = ", ".join(
            [
                synonym.text.replace(", ", "").capitalize()
                for synonym in synonyms
                if "(" not in synonym.text
            ]
        )
    except (AttributeError, IndexError):
        synonyms = "No synonyms found"
    return synonyms


def antonymize(soup) -> str:
    try:
        antonyms = soup.find_all("ul", {"class": "mw-list"})[1].find_all("li")
        antonyms = ", ".join(
            [
                antonym.text.replace(", ", "").capitalize()
                for antonym in antonyms
                if "(" not in antonym.text
            ]
        )
    except (AttributeError, IndexError):
        antonyms = "No antonyms found"
    return antonyms


def usage(soup) -> str:
    try:
        use = soup.find("p", {"class": "ety-sl"}).text
        use = use.split(",")[0]
    except (AttributeError, IndexError):
        use = "No use found"
    return use.capitalize()


def history_and_etymology(soup) -> str:
    try:
        history = soup.find_all("p", {"class": "et"})[0].text.split("—")[0]
    except (AttributeError, IndexError):
        history = "No history found"
    return history.strip().capitalize()


def spellcheck(word: str) -> str:
    soup = request(word.lower())
    spelling = soup.find("p", {"class": "spelling-suggestions"}).text
    return spelling.strip().capitalize()