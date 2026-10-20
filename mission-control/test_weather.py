import unittest
from unittest import mock

import weather

PAYLOAD = {"daily": {
    "time": ["2026-10-19", "2026-10-20"],
    "weather_code": [0, 95],
    "temperature_2m_max": [12.5, 9.0],
    "temperature_2m_min": [1.0, 3.5],
    "precipitation_probability_max": [0, 80],
}}


class ParseForecastTests(unittest.TestCase):
    def test_parses_each_day_with_plain_label(self):
        days = weather.parse_forecast(PAYLOAD)
        self.assertEqual(days[0], {"date": "2026-10-19", "summary": "Clear", "high": 12.5, "low": 1.0, "rain_chance": 0})
        self.assertEqual(days[1]["summary"], "Thunderstorm")

    def test_unknown_code_is_labelled_unknown(self):
        payload = {"daily": {**PAYLOAD["daily"], "weather_code": [123, 0]}}
        self.assertEqual(weather.parse_forecast(payload)[0]["summary"], "Unknown")


class FetchAllTests(unittest.TestCase):
    def test_one_city_failing_does_not_hide_the_other(self):
        def fake(name, now=None):
            if name == "Calgary":
                raise OSError("down")
            return [{"date": "2026-10-19"}]
        with mock.patch.object(weather, "fetch_city", fake):
            out = weather.fetch_all()
        self.assertEqual(out["Calgary"]["error"], "forecast unavailable")
        self.assertEqual(out["Shenzhen"]["days"], [{"date": "2026-10-19"}])


if __name__ == "__main__":
    unittest.main()
