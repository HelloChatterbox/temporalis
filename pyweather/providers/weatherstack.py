from pyweather.location import geolocate
from pyweather.providers import WeatherProvider
from pendulum import now


class WeatherStack(WeatherProvider):
    default_key = "2b534b0a564059057f525a1add1157e3"

    def __init__(self, lat, lon, key=None,
                 date=None, units="metric", lang="en"):
        if units in ["english", "imperial", "us"]:
            units = "f"
        elif units != "metric":
            units = "s"
        else:
            units = "m"
        # m for Metric
        #   s for Scientific
        #   f for Fahrenheit
        super().__init__(lat, lon, date, units, lang)
        self.key = key or self.default_key
        self._request()

    @staticmethod
    def from_address(address, key=None):
        key = key or WeatherStack.default_key
        lat, lon = geolocate(address)
        return WeatherStack(lat, lon, key)

    def _request_current(self):
        url = "http://api.weatherstack.com/current"
        params = {
            "access_key": self.default_key,
            "query": "{lat}, {lon}".format(lat=self.latitude,
                                           lon=self.longitude),
            "units": self.units,
            "lang": self.lang
        }
        entry = self.session.get(url, params=params).json()

        # {
        #     "request": {
        #         "type": "City",
        #         "query": "New York, United States of America",
        #         "language": "en",
        #         "unit": "m"
        #     },
        #     "location": {
        #         "name": "New York",
        #         "country": "United States of America",
        #         "region": "New York",
        #         "lat": "40.714",
        #         "lon": "-74.006",
        #         "timezone_id": "America/New_York",
        #         "localtime": "2019-09-07 08:14",
        #         "localtime_epoch": 1567844040,
        #         "utc_offset": "-4.0"
        #     },
        #     "current": {
        #         "observation_time": "12:14 PM",
        #         "temperature": 13,
        #         "weather_code": 113,
        #         "weather_icons": [
        #             "https://assets.weatherstack.com/images/wsymbols01_png_64/wsymbol_0001_sunny.png"
        #         ],
        #         "weather_descriptions": [
        #             "Sunny"
        #         ],
        #         "wind_speed": 0,
        #         "wind_degree": 349,
        #         "wind_dir": "N",
        #         "pressure": 1010,
        #         "precip": 0,
        #         "humidity": 90,
        #         "cloudcover": 0,
        #         "feelslike": 13,
        #         "uv_index": 4,
        #         "visibility": 16
        #     }
        # }
        temperature = entry["current"].get("temperature")
        visibility = entry["current"].get("visibility")
        cloudCover = entry["current"].get("cloudcover")
        pressure = entry["current"].get("pressure")
        humidity = entry["current"].get("humidity")
        ap_temperature = entry["current"].get("feelslike") or temperature
        uv = entry["current"].get("uv_index")
        precip = entry["current"].get("precip")
        wind_speed = entry["current"].get("wind_speed")
        wind_bearing = entry["current"].get("wind_degree")
        summary = entry["current"]["weather_descriptions"][0]
        icon = entry["current"]["weather_code"]

        temperature_min = temperature
        temperature_max = temperature

        # timezone = entry["location"]["timezone_id"]
        timezone = "UTC"
        ts = entry["location"]["localtime_epoch"]
        lat = entry["location"]["lat"] or self.latitude
        lon = entry["location"]["lon"] or self.longitude

        w = {
            "time": ts,
            "timezone": timezone,
            "pressure": pressure,
            "cloudCover": cloudCover,
            "visibility": visibility,
            "humidity": humidity,
            "temperature": temperature,
            "apparentTemperature": ap_temperature,
            "temperatureMin": temperature_min,
            "temperatureMax": temperature_max,
            "windSpeed": wind_speed,
            "windBearing": wind_bearing,
            "summary": summary,
            "uvIndex": uv,
            "precipIntensity": precip,
            "icon": icon
        }

        hour = w
        date = self._stamp_to_datetime(ts, timezone)
        hour["time"] = date.replace(minute=0, microsecond=0,
                                    second=0).timestamp()
        self.data["timezone"] = timezone
        self.data["latitude"] = lat
        self.data["longitude"] = lon
        self.data["currently"] = w
        self.data["daily"] = {"summary": w["summary"],
                              "icon": w["icon"],
                              "data": [w]}
        self.data["hourly"] = {"summary": w["summary"],
                               "icon": w["icon"],
                               "data": [hour]}

    def _request(self):
        self._request_current()


if __name__ == "__main__":
    date = now()
    print(date)

    d = WeatherStack.from_address("Lisbon")
    lat, lon = 38.7222563442538, -9.1393314973889
    #d = WeatherStack(lat, lon)

    print("##### CURRENT WEATHER ######")
    d.print()

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()
