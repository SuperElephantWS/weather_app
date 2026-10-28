from flask import Flask, render_template, request
import requests
import os
import math
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")


def fetch_weather(city=None, *, latitude=None, longitude=None):
    """Fetch weather for a city and return a clean dict of values.

    Returns a tuple (data: dict, error: str | None). On any failure, `data`
    is an empty dict and `error` is a human-readable message.
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"appid": API_KEY, "units": "metric"}
    if city:
        params["q"] = city
    else:
        params.update(lat=latitude, lon=longitude)
    location = city or "your location"

    try:
        response = requests.get(url, params=params, timeout=10)
    except requests.RequestException as exc:
        return {}, f"Could not reach the weather service ({exc.__class__.__name__})."

    if response.status_code == 404:
        return {}, f"Weather data for {location} was not found. Try searching by city."
    if response.status_code == 401:
        return {}, "The weather API key is invalid or missing. Check the API_KEY in your .env file."
    if response.status_code != 200:
        return {}, f"The weather service returned an unexpected status code ({response.status_code})."

    try:
        payload = response.json()
    except ValueError:
        return {}, "The weather service returned data we could not understand."

    main = payload.get("main", {})
    weather = payload.get("weather", [{}])
    weather_desc = weather[0].get("description", "n/a") if weather else "n/a"
    icon = weather[0].get("icon") if weather else None
    valid_icons = {f"{code}{period}" for code in ("01", "02", "03", "04", "09", "10", "11", "13", "50") for period in ("d", "n")}
    icon = icon if isinstance(icon, str) and icon in valid_icons else None
    wind = payload.get("wind", {})

    return {
        "city": payload.get("name") or location,
        "temp": main.get("temp"),
        "feels_like": main.get("feels_like"),
        "temp_min": main.get("temp_min"),
        "temp_max": main.get("temp_max"),
        "humidity": main.get("humidity"),
        "description": weather_desc,
        "icon": icon,
        "wind_speed": wind.get("speed"),
    }, None


@app.route("/", methods=["GET"])
def home():
    city = request.args.get("city", "").strip()
    latitude = request.args.get("lat")
    longitude = request.args.get("lon")
    data, error = {}, None
    has_coordinates = latitude is not None or longitude is not None
    if city:
        data, error = fetch_weather(city)
    elif has_coordinates:
        try:
            latitude, longitude = float(latitude), float(longitude)
            if not (math.isfinite(latitude) and math.isfinite(longitude)
                    and -90 <= latitude <= 90 and -180 <= longitude <= 180):
                raise ValueError
        except (TypeError, ValueError):
            error = "Invalid location coordinates. Try searching by city."
        else:
            data, error = fetch_weather(latitude=latitude, longitude=longitude)
    return render_template(
        "index.html", data=data, error=error,
        requested_city=city or "Local weather",
        detect_location=not city and not has_coordinates,
    )


def main():
    app.run()


if __name__ == "__main__":
    main()
