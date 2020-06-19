from pyweather.location import geolocate
import requests
from pyweather.providers import WeatherProvider
from pprint import pprint
import pendulum


class WeatherBit(WeatherProvider):
    def __init__(self, lat, lon, key, date=None, units="metric"):
        if units in ["english", "imperial", "us"]:
            units = "I"
        elif units != "metric":
            units = "M"
        else:
            units = "S"
        super().__init__(lat, lon, date, units)
        self.key = key
        self.url = "https://api.weatherbit.io/v2.0/current"
        self._request()

    @staticmethod
    def from_address(address, key):
        lat, lon = geolocate(address)
        return WeatherBit(lat, lon, key)

    def _request_current(self):
        params = {"units": self.units,
                  "lat": self.latitude,
                  "lon":  self.longitude,
                  "key":self.key}
        entry = requests.get(self.url, params=params).json()
        entry = entry["data"][0]

        # TODO hour to timestamp
        sunriseTime = entry["sunrise"]
        sunsetTime = entry["sunset"]

        pressure = entry.get("pres")
        cloudCover = entry.get("clouds")
        visibility = entry.get("vis")

        # TODO check docs for key
        humidity = entry.get("humidity")

        temperature = entry.get("temp")
        ap_temperature = entry.get("app_temp") or temperature
        temperature_min = entry.get("temp_min") or temperature
        temperature_max = entry.get("temp_max") or temperature

        wind_speed = entry.get("wind_spd")
        wind_bearing = entry.get("wind_dir")
        _w = entry.get("weather", [])
        icon = ""
        summary = ""
        if _w:
            icon = _w.get("code", "") # TODO icon code to str
            code_to_ico = {

            }
            summary = _w.get("description") or icon

        uvIndex = entry.get("uv")
        solar_rad = entry.get("solar_rad")
        snow = entry.get("snow")
        sea_pressure = entry.get("slp")
        humidity = entry.get("rh")

        dewPoint = entry.get("dewpt")

        precip = entry.get("precip")

        timezone = entry["timezone"]

        lat = entry.get("coord", {}).get("lat") or self.latitude
        lon = entry.get("coord", {}).get("lat") or self.longitude

        date = pendulum.parse(entry["ob_time"], tz=timezone)
        w = {
            "time": date.timestamp(),
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
            "dewPoint": dewPoint,
            "uvIndex": uvIndex,
            "sunriseTime": sunriseTime,
            "sunsetTime": sunsetTime,
            "summary": summary,
            "icon": icon,
            "precipIntensity": precip
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
            ACUWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast?lat" \
                      "={lat}&lon={lon}&appid={key}"
            url = ACUWEATHER_URL.format(key=self.key, lat=self.latitude, lon=self.longitude)
        else:
            ACUWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast?lat" \
                      "={lat}&lon={lon}&appid={key}&units={units}"
            url = ACUWEATHER_URL.format(key=self.key, lat=self.latitude, lon=self.longitude,
                                 units=self.units)

        res = requests.get(url).json()

        lat = res.get("city", {}).get("coord", {}).get("lat") or self.latitude
        lon = res.get("city", {}).get("coord", {}).get("lon") or self.longitude
        sunriseTime = res.get("city", {}).get("sunrise")
        sunsetTime = res.get("city", {}).get("sunset")
        # TODO shift in seconds from UTC
        # mutate date object + update timezone
        # timezone = res.get("city", {}).get("timezone")
        timezone = "UTC"

        # ACUWEATHER returns 3h in 3h readings
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
            w = WeatherDataPoint().from_dict(w)

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
            day = day.as_dict()

            day["sunriseTime"] = sunriseTime
            day["sunsetTime"] = sunsetTime
            days += [day]

        daily_summary, daily_icon = self._calc_daily_summary(days)
        self.data["daily"] = {"summary": daily_summary,
                              "icon": daily_icon,
                              "data": days}

    def _request(self):
        self._request_current()
        #self._request_forecast()


if __name__ == "__main__":
    KEY = "fd088ec43bef4769b87d347d3dec83e5"
    lat, lon = 38.7222563442538, -9.1393314973889
    d = WeatherBit(lat, lon, KEY)

    print("##### CURRENT WEATHER ######")
    d.print()

    ## WIP ZONE
    exit()
    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()
