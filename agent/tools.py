"""External tools. Currently one: live weather from Open-Meteo (no API key)."""

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
TIMEOUT_SECONDS = 10


class WeatherError(Exception):
    """Raised with a user-friendly message when weather cannot be fetched."""


def _get_json(url: str, params: dict) -> dict:
    try:
        response = requests.get(url, params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout as exc:
        raise WeatherError("The weather service timed out. Please try again.") from exc
    except requests.exceptions.ConnectionError as exc:
        raise WeatherError("Could not connect to the weather service. Check your internet.") from exc
    except requests.exceptions.HTTPError as exc:
        raise WeatherError("The weather service returned an error (%s)." % exc.response.status_code) from exc
    except requests.exceptions.RequestException as exc:
        raise WeatherError("Weather request failed (%s)." % type(exc).__name__) from exc
    except ValueError as exc:  # response was not valid JSON
        raise WeatherError("The weather service sent an unreadable response.") from exc
    if not isinstance(data, dict):
        raise WeatherError("The weather service sent an unexpected response.")
    return data


def _find_city(city: str) -> dict:
    data = _get_json(GEOCODING_URL, {"name": city, "count": 1, "language": "en", "format": "json"})
    results = data.get("results")
    if not results:
        raise WeatherError("I could not find a city named '%s'. Check the spelling." % city)
    place = results[0]
    if "latitude" not in place or "longitude" not in place:
        raise WeatherError("The location data for '%s' was incomplete." % city)
    return place


def get_weather(city: str) -> str:
    """Return a formatted weather report for `city`, or raise WeatherError."""
    city = (city or "").strip()
    if not city:
        raise WeatherError("Please tell me which city, e.g. 'weather in Pune'.")

    place = _find_city(city)
    data = _get_json(FORECAST_URL, {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "timezone": "auto",
    })

    current = data.get("current")
    units = data.get("current_units") or {}
    try:
        temperature = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
    except (TypeError, KeyError) as exc:
        raise WeatherError("The weather data was missing expected fields.") from exc

    location = ", ".join(
        part for part in (place.get("name"), place.get("admin1"), place.get("country")) if part
    )
    return (
        "Current weather for %s\n"
        "  Temperature : %s %s\n"
        "  Humidity    : %s %s\n"
        "  Wind speed  : %s %s\n"
        "  Observed at : %s (local time)"
        % (
            location,
            temperature, units.get("temperature_2m", "\u00b0C"),
            humidity, units.get("relative_humidity_2m", "%"),
            wind, units.get("wind_speed_10m", "km/h"),
            current.get("time", "unknown"),
        )
    )
