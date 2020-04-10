from pyweather.location import geolocate
import requests
from pyweather.providers import WeatherProvider
from pyweather import WeatherDataPoint
from pprint import pprint
from pendulum import now


class OWM(WeatherProvider):
    def __init__(self, lat, lon, key, date=None, units="metric"):
        if units in ["english", "imperial", "us"]:
            units = "imperial"
        elif units != "metric":
            units = "si"
        super().__init__(lat, lon, date, units)
        self.key = key
        self._request()

    @staticmethod
    def from_address(address, key):
        lat, lon = geolocate(address)
        return OWM(lat, lon, key)

    def _request_current(self):
        if self.units == "auto":
            API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={" \
                      "lat}&lon={lon}&appid={key}"
            url = API_URL.format(key=self.key, lat=self.latitude,
                                      lon=self.longitude)
        else:
            API_URL = "https://api.openweathermap.org/data/2.5/weather?lat={" \
                      "lat}&lon={lon}&appid={key}&units={units}"
            url = API_URL.format(key=self.key, lat=self.latitude,
                                      lon=self.longitude,
                                      units=self.units)
        entry = requests.get(url).json()

        sunriseTime = entry["sys"]["sunrise"]
        sunsetTime = entry["sys"]["sunset"]
        pressure = entry["main"].get("pressure")
        cloudCover = entry.get("clouds", {}).get("all")
        if cloudCover:
            cloudCover = cloudCover
        visibility = entry.get("visibility")
        if visibility:
            # meter -> km
            visibility = visibility / 1000
        humidity = entry["main"].get("humidity")
        if humidity:
            humidity = humidity
        temperature = entry["main"].get("temp")
        ap_temperature = entry["main"].get("feels_like") or temperature
        temperature_min = entry["main"].get("temp_min") or temperature
        temperature_max = entry["main"].get("temp_max") or temperature
        wind_speed = entry.get("wind", {}).get("speed")
        wind_bearing = entry.get("wind", {}).get("deg")
        _w = entry.get("weather", [])
        icon = ""
        summary = ""
        if _w:
            icon = _w[0].get("main", "").lower()
            summary = _w[0].get("description") or icon

        rain1h = entry.get("rain", {}).get("1h")
        rain3h = entry.get("rain", {}).get("3h")
        if rain3h and not rain1h:
            rain1h = rain3h / 3

        # TODO shift in seconds from UTC
        # timezone = entry["timezone"]
        timezone = "UTC"

        lat = entry.get("coord", {}).get("lat") or self.latitude
        lon = entry.get("coord", {}).get("lat") or self.longitude

        date = self._stamp_to_datetime(entry["dt"], timezone)
        w = {
            "time": entry["dt"],
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
            "sunriseTime": sunriseTime,
            "sunsetTime": sunsetTime,
            "summary": summary,
            "icon": icon,
            "precipIntensity": rain1h or rain3h
        }

        hour = w
        hour["time"] = date.replace(minute=0, microsecond=0, second=0).timestamp()
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

    def _request_forecast(self):
        if self.units == "auto":
            OWM_URL = "https://api.openweathermap.org/data/2.5/forecast?lat" \
                      "={lat}&lon={lon}&appid={key}"
            url = OWM_URL.format(key=self.key, lat=self.latitude, lon=self.longitude)
        else:
            OWM_URL = "https://api.openweathermap.org/data/2.5/forecast?lat" \
                      "={lat}&lon={lon}&appid={key}&units={units}"
            url = OWM_URL.format(key=self.key, lat=self.latitude, lon=self.longitude,
                                 units=self.units)

        res = requests.get(url).json()

        lat = res.get("city", {}).get("coord", {}).get("lat") or self.latitude
        lon = res.get("city", {}).get("coord", {}).get("lon") or self.longitude
        sunriseTime = res.get("city", {}).get("sunrise")
        sunsetTime = res.get("city", {}).get("sunset")
        timezone = "UTC"

        # OWM returns 3h in 3h readings
        hours = []
        _days = {}
        for entry in res["list"]:
            pressure = entry["main"].get("pressure")
            cloudCover = entry.get("clouds", {}).get("all")
            if cloudCover:
                cloudCover = cloudCover
            visibility = entry.get("visibility")
            if visibility:
                # meter -> km
                visibility = visibility / 1000
            humidity = entry["main"].get("humidity")
            if humidity:
                humidity = humidity
            temperature = entry["main"].get("temp")
            ap_temperature = entry["main"].get("feels_like") or temperature
            temperature_min = entry["main"].get("temp_min") or temperature
            temperature_max = entry["main"].get("temp_max") or temperature
            wind_speed = entry.get("wind", {}).get("speed")
            wind_bearing = entry.get("wind", {}).get("deg")
            _w = entry.get("weather", [])
            icon = ""
            summary = ""
            if _w:
                icon = _w[0].get("main", "").lower()
                summary = _w[0].get("description") or icon

            rain1h = entry.get("rain", {}).get("1h")
            rain3h = entry.get("rain", {}).get("3h")
            if rain3h and not rain1h:
                rain1h = rain3h / 3

            pprint(entry)
            w = {
                "time": entry["dt"],

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
                "icon": icon,
                "precipIntensity": rain1h or rain3h
            }
            hours.append(w)
            w = WeatherDataPoint().from_json(w)

            if w.datetime.day not in _days:
                _days[w.datetime.day] = []
            _days[w.datetime.day] += [w]

        # TODO
        hourly_summary, hourly_icon = self._calc_hourly_summary(hours)
        self.data["timezone"] = timezone
        self.data["latitude"] = lat
        self.data["longitude"] = lon

        self.data["hourly"] = {"summary": hourly_summary,
                               "icon": hourly_icon,
                               "data": hours}
        days = []
        for d in _days:
            day = self._calc_day_average(_days[d])
            day = day.as_json()

            day["sunriseTime"] = sunriseTime
            day["sunsetTime"] = sunsetTime
            days += [day]

        daily_summary, daily_icon = self._calc_daily_summary(days)
        self.data["daily"] = {"summary": daily_summary,
                              "icon": daily_icon,
                              "data": days}

    def _request(self):
        self._request_current()
        self._request_forecast()


if __name__ == "__main__":
    lat, lon = 38.7222563442538, -9.1393314973889
    OWM_KEY = "XXXX"
    d = OWM.from_address("Brussels", OWM_KEY)
    date = now()
    #d = OWM(lat, lon, OWM_KEY)

    print("##### CURRENT WEATHER ######")
    d.print()

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()
