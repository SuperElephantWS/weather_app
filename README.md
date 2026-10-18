# Weather App

A small Flask web app that fetches current weather for a city from the
OpenWeatherMap API and displays it in a clean, styled web page.

It shows the current temperature, "feels like", humidity, min/max temperature,
and wind speed, plus the weather condition. It also handles API failures
(missing key, unknown city, network errors) with a friendly error message
instead of crashing.

## Features

- Current weather for a city (defaults to **New Haven**)
- Look up any city via the on-page search box or a `?city=` query param
- Rich data: temperature, feels-like, min/max, humidity, wind, condition
- Graceful error handling (bad API key, unknown city, network timeout)
- Styled, responsive web UI

## Project structure

```
weather_app/
├── app.py                  # Flask app + weather logic
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── .env                    # API key (do NOT commit this file)
├── templates/
│   └── index.html          # Jinja2 page that renders the weather
└── weather_env/            # Python virtual environment
```

## Prerequisites

- Python 3.10+ (tested on Python 3.13)
- An OpenWeatherMap API key — sign up for a free one and copy the key from
  [https://home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys)
- Internet access (the app calls the live weather service)

## 1. Set up your environment

### Create & activate the virtual environment

The repo already ships with a `weather_env/` virtual environment. If you are
starting fresh, create one first:

```bash
python3 -m venv weather_env
```

Activate it:

```bash
source weather_env/bin/activate        # macOS / Linux
# weather_env\Scripts\activate         # Windows (PowerShell / CMD)
```

> Your prompt will change to show `(weather_env)` while the environment is active.
> You only need to re-run the activation command in each new terminal session.

### Install the dependencies

```bash
pip install -r requirements.txt
```

This installs:

| Package         | Purpose                         |
| --------------- | ------------------------------- |
| `Flask`         | Web framework & routing         |
| `requests`      | HTTP client for the weather API |
| `python-dotenv` | Loads `API_KEY` from `.env`     |

### Add your API key

Create a `.env` file in the project root (it is already present in this repo)
with a single line:

```
API_KEY=your_openweathermap_api_key_here
```

> **Security note:** `.env` contains a secret. Do not commit it to version
> control — add `.env`, `weather_env/`, and `__pycache__/` to `.gitignore`.

## 2. Run the app

Make sure the virtual environment is active, then run either of these:

```bash
flask --app app run --host 127.0.0.1 --port 5000 --debug
```

or

```bash
python app.py
```

You should see output like:

```text
 * Running on http://127.0.0.1:5000
```

## 3. View the weather

Open the Flask server URL in your browser:

```
http://127.0.0.1:5000
```

You will see the current weather for the default city (**New Haven**).

To check a different city:

- Type the city name into the **search box** and click **Search**, **or**
- Use a `?city=` query parameter, e.g.:

```
http://127.0.0.1:5000/?city=Paris
http://127.0.0.1:5000/?city=London
http://127.0.0.1:5000/?city=Tokyo
```

> **Important:** view the page through the Flask server URL above, not a static
> "Go Live" preview. A static preview does not run Jinja2, so it would show
> literal `{{ city }}` / `{{ temp }}` placeholders instead of real values.

### What you will see

| Field        | Meaning                                     |
| ------------ | ------------------------------------------- |
| Temperature  | Current air temperature (°C)                |
| Feels like   | Perceived temperature (°C)                  |
| Humidity     | Relative humidity (%)                       |
| Min / Max    | Day's low / high temperature (°C)           |
| Wind         | Wind speed (m/s)                            |
| Condition    | Short description (e.g. "scattered clouds") |

If a value is unavailable from the API it is shown as `—` rather than breaking the page.

## Stopping the app

- In the terminal, press `Ctrl + C`, **or**
- Kill the process:

```bash
pkill -f "flask --app app run"
```

## Troubleshooting

| Symptom                                    | Likely cause & fix                                                                                              |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------- |
| Page shows raw `{{ city }}` / `{{ temp }}`  | You opened the file via a static "Go Live" preview. Open `http://127.0.0.1:5000` instead — Jinja renders only through Flask. |
| "The weather API key is invalid or missing." | Check `API_KEY` in `.env`. Restart the app after editing it.                                                    |
| "…was not found."                           | The city name is not recognized. Try a different spelling (e.g. "New York" → "New York City").                  |
| "Could not reach the weather service…"      | No internet / network block, or the request timed out (the app has a 10 s limit). Retry.                        |
| `ModuleNotFoundError: flask` / `dotenv`     | The venv isn't active or deps are missing. Run `source weather_env/bin/activate` then `pip install -r requirements.txt`. |
| `Address already in use` / port 5000 busy   | Another app is using port 5000. Kill it (`pkill -f "flask --app app run"`) or use another port.                 |

## Notes

- The app requests the **metric** unit system (°C, m/s).
- Requests to the weather service use a **10 second timeout**, so failures surface quickly.
- To change the default city, edit the fallback in `home()` in `app.py`:
  `city = request.args.get("city") or "New Haven"`.
