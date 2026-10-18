"""Gemini access layer.

Every call to the language model goes through ask_gemini(), so API-key
handling, model selection and error handling live in exactly one place.
"""

import os

from dotenv import load_dotenv

load_dotenv()  # reads GOOGLE_API_KEY (and optional GEMINI_MODEL) from .env

# Change this, or set GEMINI_MODEL in .env, if Google retires the model.
DEFAULT_MODEL = "gemini-3.8-flash"
# Tried in order if the chosen model returns "404 not found".
FALLBACK_MODELS = ("gemini-flash-latest",)


class LLMError(Exception):
    """Raised with a user-friendly message when Gemini cannot be used."""


def _get_api_key() -> str:
    key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not key or key == "your_api_key_here":
        raise LLMError(
            "GOOGLE_API_KEY is missing. Copy .env.example to .env, paste your "
            "key from https://aistudio.google.com/apikey, and restart."
        )
    return key


def _model_candidates() -> list:
    first = os.getenv("GEMINI_MODEL", "").strip() or DEFAULT_MODEL
    names = [first]
    for name in FALLBACK_MODELS:
        if name not in names:
            names.append(name)
    return names


def _describe_api_error(exc) -> str:
    code = getattr(exc, "code", None)
    detail = str(getattr(exc, "message", "") or "")[:200]
    if code in (400, 401, 403) and "key" in detail.lower():
        return "Gemini rejected the API key. Check GOOGLE_API_KEY in your .env file."
    if code in (401, 403):
        return "Gemini denied access (HTTP %s). Check your API key and permissions." % code
    if code == 429:
        return "Gemini quota or rate limit reached (HTTP 429). Wait a minute and retry."
    if code is not None and code >= 500:
        return "Gemini is temporarily unavailable (HTTP %s). Try again shortly." % code
    return "Gemini API error (HTTP %s): %s" % (code, detail)


def ask_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the reply text.

    Raises LLMError (never a raw SDK exception) so callers need one except.
    """
    if not prompt or not prompt.strip():
        raise LLMError("Cannot send an empty prompt to Gemini.")

    api_key = _get_api_key()

    try:
        from google import genai
        from google.genai import errors
    except ImportError as exc:
        raise LLMError(
            "The 'google-genai' package is not installed. "
            "Activate your virtual environment and run: pip install -r requirements.txt"
        ) from exc

    client = genai.Client(api_key=api_key)
    tried = []

    for model in _model_candidates():
        tried.append(model)
        try:
            response = client.models.generate_content(model=model, contents=prompt)
        except errors.APIError as exc:
            if getattr(exc, "code", None) == 404:
                continue  # model unavailable: try the next candidate
            raise LLMError(_describe_api_error(exc)) from exc
        except Exception as exc:  # network down, SSL problems, etc.
            raise LLMError(
                "Could not reach Gemini (%s). Check your internet connection."
                % type(exc).__name__
            ) from exc

        text = (getattr(response, "text", None) or "").strip()
        if not text:
            raise LLMError(
                "Gemini returned an empty response (it may have been blocked "
                "by a safety filter). Try rephrasing your request."
            )
        return text

    raise LLMError(
        "No Gemini model was available (tried: %s). Set GEMINI_MODEL in .env "
        "to a model listed at https://ai.google.dev/gemini-api/docs/models"
        % ", ".join(tried)
    )
