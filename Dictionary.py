import bs4
import requests

def request(word: str) -> bs4.BeautifulSoup:
    url = f"https://www.merriam-webster.com/dictionary/{word}"
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, "html.parser")
    return soup

def spellcheck(word: str) -> str:
    soup = request(word.lower())
    spelling = soup.find("p", {"class": "spelling-suggestions"}).text
    return spelling.strip().capitalize()

def get_word_info(word: str) -> dict:
    word_data = {}
    soup = request(word.lower())
    word_data['word'] = word
    try:
        word_data['definition'] = soup.find("span", {"class": "dtText"}).text.split(":")[1]
    except (AttributeError, IndexError):
        word_data['definition'] = "No definition found"
    try: 
        word_data['phonetic'] = soup.find("span", {"class": "pr"}).text.replace(" ", "")
    except (AttributeError, IndexError):
        word_data['phonetic'] = "No phonetic found"
    try:
        word_data['synonyms'] = soup.find("ul", {"class": "mw-list"}).find_all("li")
        word_data['synonyms'] = ", ".join(
            [
                synonym.text.replace(", ", "").capitalize()
                for synonym in word_data['synonyms']
                if "(" not in synonym.text
            ]
        )
    except (AttributeError, IndexError):
        word_data['synonyms'] = "No synonyms found"
    try:
        word_data['antonyms'] = soup.find_all("ul", {"class": "mw-list"})[1].find_all("li")
        word_data['antonyms'] = ", ".join(
            [
                antonym.text.replace(", ", "").capitalize()
                for antonym in word_data['antonyms']
                if "(" not in antonym.text
            ]
        )
    except (AttributeError, IndexError):
        word_data['antonyms'] = "No antonyms found"
    try:
        word_data['usage'] = soup.find("p", {"class": "ety-sl"}).text
        word_data['usage'] = word_data['usage'].split(",")[0]
    except (AttributeError, IndexError):
        word_data['usage'] = "No use found"
    try:
        word_data['etymology'] = soup.find_all("p", {"class": "et"})[0].text.split("—")[0]
    except (AttributeError, IndexError):
        word_data['etymology'] = "No etymology found"
    return word_data