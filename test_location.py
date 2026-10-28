import unittest
from unittest.mock import Mock, patch

from app import app


class LocationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.weather_response = Mock(status_code=200)
        self.weather_response.json.return_value = {
            "name": "Boston", "main": {"temp": 12},
            "weather": [{"description": "clear sky", "icon": "01d"}],
        }

    @patch("app.requests.get")
    def test_default_waits_for_browser_location_without_weather_request(self, get):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="location-status"', response.data)
        self.assertIn(b'/static/location.js', response.data)
        self.assertNotIn(b'New Haven', response.data)
        get.assert_not_called()

    @patch("app.requests.get")
    def test_coordinates_are_forwarded_without_city(self, get):
        get.return_value = self.weather_response
        response = self.client.get("/?lat=42.36&lon=-71.06")
        self.assertIn(b'Boston', response.data)
        self.assertNotIn(b'/static/location.js', response.data)
        params = get.call_args.kwargs["params"]
        self.assertEqual((params["lat"], params["lon"]), (42.36, -71.06))
        self.assertNotIn("q", params)

    @patch("app.requests.get")
    def test_zero_coordinates_are_valid(self, get):
        get.return_value = self.weather_response
        self.assertEqual(self.client.get("/?lat=0&lon=0").status_code, 200)
        self.assertEqual(get.call_args.kwargs["params"]["lat"], 0)

    @patch("app.requests.get")
    def test_city_search_takes_precedence_and_does_not_detect_again(self, get):
        get.return_value = self.weather_response
        response = self.client.get("/?city=Boston&lat=99&lon=bad")
        self.assertIn(b'Boston', response.data)
        self.assertNotIn(b'/static/location.js', response.data)
        self.assertEqual(get.call_args.kwargs["params"]["q"], "Boston")
        self.assertNotIn("lat", get.call_args.kwargs["params"])

    @patch("app.requests.get")
    def test_invalid_coordinates_do_not_call_provider_or_retry_detection(self, get):
        for query in ("lat=abc&lon=1", "lat=91&lon=0", "lat=0&lon=-181",
                      "lat=nan&lon=0", "lat=0&lon=inf", "lat=1", "lon=1",
                      "lat=&lon=0"):
            with self.subTest(query=query):
                response = self.client.get("/?" + query)
                self.assertIn(b'Invalid location coordinates', response.data)
                self.assertNotIn(b'/static/location.js', response.data)
        get.assert_not_called()

    @patch("app.requests.get")
    def test_provider_failure_keeps_city_search_available(self, get):
        get.return_value = Mock(status_code=404)
        response = self.client.get("/?lat=42&lon=-71")
        self.assertIn(b'Weather data for your location was not found', response.data)
        self.assertIn(b'class="search"', response.data)
        self.assertNotIn(b'/static/location.js', response.data)

    def test_detection_script_is_served(self):
        response = self.client.get("/static/location.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'getCurrentPosition', response.data)
        response.close()

    @patch("app.requests.get")
    def test_strip_keeps_all_weather_details_and_search_layout(self, get):
        get.return_value = self.weather_response
        response = self.client.get("/?layout=strip&city=Boston")
        for text in (b'class="weather-strip"', b'Boston', b'clear sky',
                     b'12&deg;C', b'Feels like', b'Humidity', b'Min / Max', b'Wind',
                     b'name="layout" value="strip"', b'/static/embed.js',
                     b'aria-label="City"'):
            self.assertIn(text, response.data)
        self.assertNotIn(b'/static/location.js', response.data)

    @patch("app.requests.get")
    def test_strip_retains_detection_and_error_fallback(self, get):
        initial = self.client.get("/?layout=strip")
        self.assertIn(b'/static/location.js', initial.data)
        self.assertIn(b'/static/embed.js', initial.data)
        get.assert_not_called()
        get.return_value = Mock(status_code=404)
        failed = self.client.get("/?layout=strip&city=UnknownCity")
        self.assertIn(b'not found', failed.data)
        self.assertIn(b'name="layout" value="strip"', failed.data)

    def test_standalone_page_does_not_enable_embedding(self):
        response = self.client.get("/")
        self.assertNotIn(b'<body class="weather-strip">', response.data)
        self.assertNotIn(b'/static/embed.js', response.data)
        self.assertNotIn(b'name="layout" value="strip"', response.data)


if __name__ == "__main__":
    unittest.main()
