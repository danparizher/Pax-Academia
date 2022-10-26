import deepl


def get_language_list() -> list[str]:
    languages = [
        "Bulgarian",
        "Chinese",
        "Czech",
        "Danish",
        "Dutch",
        "English",
        "Estonian",
        "Finnish",
        "French",
        "German",
        "Greek",
        "Hungarian",
        "Italian",
        "Japanese",
        "Latvian",
        "Lithuanian",
        "Polish",
        "Portuguese",
        "Romanian",
        "Russian",
        "Slovak",
        "Slovenian",
        "Spanish",
        "Swedish",
    ]
    return languages


formality = ["formal", "informal"]


async def translation(
    text, source_language, target_language, formality_tone=None
) -> str:

    languages = get_language_list()
    if source_language not in languages or target_language not in languages:
        return "Invalid Language"

    if formality_tone is not None:
        formality_tone = formality_tone.lower()

    if formality_tone is not None and formality_tone not in formality:
        return "Invalid Formality"

    return deepl.translate(
        text=text,
        source_language=source_language,
        target_language=target_language,
        formality_tone=formality_tone,
    )
