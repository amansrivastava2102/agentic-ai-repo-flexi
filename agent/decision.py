"""Rule-based task router.

decide() looks at the user's text and picks one task using regular
expressions. It does NOT use an LLM, so it is fast, free and predictable.
"""

import re
from dataclasses import dataclass
from typing import Optional

SUMMARIZE = "summarize"
TRANSLATE = "translate"
SENTIMENT = "sentiment"
WEATHER = "weather"
GENERAL = "general"

FLAGS = re.IGNORECASE | re.DOTALL


@dataclass
class Decision:
    task: str
    text: str = ""                 # text the task should work on
    city: Optional[str] = None     # only used by the weather task


# ---- Patterns -------------------------------------------------------------
# Summarize / translate / sentiment must appear at the START of the message
# (or as an explicit phrase), so "What is the weather summary?" is not
# mistaken for a summarization request.
_SUMMARIZE_START = re.compile(
    r"^\s*(?:please\s+|can you\s+|could you\s+)?(?:summari[sz]e|tl;?dr)\b"
    r"(?:\s+(?:this|the following(?:\s+text)?|the text|following text|below))?\s*[:\-]?\s*", FLAGS)
_TRANSLATE_START = re.compile(
    r"^\s*(?:please\s+|can you\s+|could you\s+)?translate\b", FLAGS)
_TRANSLATE_TEXT_TO_HINDI = re.compile(
    r"^\s*(?:please\s+|can you\s+|could you\s+)?translate\s+(?P<text>.+?)\s+(?:in)?to\s+hindi\s*[.?!]?\s*$", FLAGS)
_TRANSLATE_TO_HINDI_COLON = re.compile(
    r"^\s*(?:please\s+|can you\s+|could you\s+)?translate\s+(?:in)?to\s+hindi\s*[:\-]\s*(?P<text>.+)$", FLAGS)
_HOW_TO_SAY = re.compile(
    r"^\s*how (?:do (?:you|i) )?say\s+(?P<text>.+?)\s+in\s+hindi\s*\??\s*$", FLAGS)
_SENTIMENT = re.compile(
    r"\b(?:sentiment|positive or negative|(?:analy[sz]e|detect|classify)\s+(?:the\s+)?(?:tone|mood|emotion))\b", FLAGS)

_STRONG_WEATHER = re.compile(r"\b(?:weather|forecast|raining|snowing)\b", FLAGS)
_WEAK_WEATHER = re.compile(
    r"\b(?:temperature|humidity|wind speed|how hot|how cold|is it (?:hot|cold|sunny|raining))\b", FLAGS)
_TIME_CUE = re.compile(r"\b(?:today|now|currently|current|right now|tonight|outside)\b", FLAGS)

_CITY_AFTER_PREPOSITION = re.compile(
    r"\b(?:in|at|for)\s+(?P<city>[A-Za-z][A-Za-z .'\-]*?)"
    r"(?=\s+(?:today|now|right now|currently|tonight|tomorrow|this\s+\w+)\b|\s*[?.!,]|\s*$)", FLAGS)
_CITY_OF = re.compile(
    r"\b(?:weather|forecast)\s+of\s+(?P<city>[A-Za-z][A-Za-z .'\-]*?)(?=\s+(?:today|now)\b|\s*[?.!,]|\s*$)", FLAGS)
_CITY_BEFORE_WEATHER = re.compile(
    r"^\s*(?P<city>[A-Za-z]+(?:\s[A-Za-z]+){0,2})\s+(?:weather|temperature|forecast)\b", FLAGS)

_STOP_WORDS = {"what", "whats", "what's", "how", "is", "the", "tell", "me", "show", "give",
               "get", "check", "current", "today", "todays", "today's", "and", "a", "an"}
_NOT_CITIES = {"the", "a", "an", "it", "this", "that", "general", "my area", "my city",
               "here", "there", "today", "now", "celsius", "fahrenheit"}


def _strip_quotes(text: str) -> str:
    return text.strip().strip("\"'\u201c\u201d\u2018\u2019").strip()


def extract_city(message: str) -> Optional[str]:
    """Best-effort city extraction from a weather question."""
    match = _CITY_AFTER_PREPOSITION.search(message)
    if not match:
        match = _CITY_OF.search(message)
    if not match:
        match = _CITY_BEFORE_WEATHER.match(message)
    if not match:
        return None
    city = match.group("city").strip(" .,'-")
    city = re.sub(r"^(?:the|current|today's)\s+", "", city, flags=re.IGNORECASE).strip()
    if not city or city.lower() in _NOT_CITIES:
        return None
    if any(word.lower() in _STOP_WORDS for word in city.split()):
        return None
    return city


def _is_weather_request(message: str) -> bool:
    if _STRONG_WEATHER.search(message):
        return True
    if _WEAK_WEATHER.search(message):
        # "temperature of boiling water" must NOT count as weather,
        # so require a place or a time cue as well.
        return bool(extract_city(message) or _TIME_CUE.search(message))
    return False


def decide(message: str) -> Decision:
    """Choose the task for one user message."""
    message = (message or "").strip()

    # 1. Summarization
    match = _SUMMARIZE_START.match(message)
    if match:
        return Decision(SUMMARIZE, text=_strip_quotes(message[match.end():]))

    # 2. Translation (Hindi is the only supported target language)
    if _TRANSLATE_START.match(message) or _HOW_TO_SAY.match(message):
        for pattern in (_TRANSLATE_TEXT_TO_HINDI, _TRANSLATE_TO_HINDI_COLON, _HOW_TO_SAY):
            match = pattern.match(message)
            if match:
                return Decision(TRANSLATE, text=_strip_quotes(match.group("text")))
        # Looks like a translate request but no recognisable "to Hindi" part.
        body = _TRANSLATE_START.sub("", message, count=1)
        return Decision(TRANSLATE, text=_strip_quotes(body))

    # 3. Sentiment analysis
    match = _SENTIMENT.search(message)
    if match:
        if ":" in message:
            body = message.split(":", 1)[1]
        else:
            body = message[match.end():]
        return Decision(SENTIMENT, text=_strip_quotes(body))

    # 4. Weather
    if _is_weather_request(message):
        return Decision(WEATHER, text=message, city=extract_city(message))

    # 5. Fallback: let Gemini answer
    return Decision(GENERAL, text=message)
