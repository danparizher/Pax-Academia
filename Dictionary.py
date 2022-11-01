import json

import requests

# API: https://api.dictionaryapi.dev/api/
# API Documentation: https://dictionaryapi.dev/


def request(word) -> str:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)
    data = json.loads(response.text)
    return data


def define(word) -> str:
    data = request(word)
    try:
        definition = data[0]["meanings"][0]["definitions"][0]["definition"]
    except (KeyError, IndexError):
        definition = "No definition found"
    return definition


def phonetisize(word) -> str:
    data = request(word)
    try:
        phonetic = data[0]["phonetics"][0]["text"]
    except (KeyError, IndexError):
        phonetic = ""
    return phonetic


def part_of_speech(word) -> str:
    data = request(word)
    try:
        part_of_speech = data[0]["meanings"][0]["partOfSpeech"]
    except (KeyError, IndexError):
        part_of_speech = ""
    return part_of_speech


def audiate(word) -> str:
    data = request(word)
    try:
        audio = data[0]["phonetics"][0]["audio"]
    except (KeyError, IndexError):
        audio = ""
    return audio
