from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
API_KEY = os.getenv("API_KEY")


def fetch_weather(city):
    """Fetch weather for a city and return a clean dict of values.

    Returns a tuple (data: dict, error: str | None). On any failure, `data`
    is an empty dict and `error` is a human-readable message.
    """
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        f"?q={requests.utils.quote(city)}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException as exc:
        return {}, f"Could not reach the weather service ({exc.__class__.__name__})."

    if response.status_code == 404:
        return {}, f"Weather data for {city} was not found. Check the city name and try again."
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
        "city": payload.get("name", city),
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
    city = request.args.get("city") or "New Haven"
    data, error = fetch_weather(city)
    return render_template("index.html", data=data, error=error, requested_city=city)


def main():
    app.run()


if __name__ == "__main__":
    main()
