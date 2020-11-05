from temporalis.location import geolocate
from temporalis.providers import WeatherProvider
from temporalis import WeatherData, DataPoint


class OWM(WeatherProvider):
    default_key = "28fed22898afd4717ce5a1535da1f78c"

    def __init__(self, lat, lon, key=None,
                 date=None, units="metric"):
        if units in ["english", "imperial", "us"]:
            units = "imperial"
        elif units != "metric":
            units = "si"
        super().__init__(lat, lon, date, units)
        self.key = key or self.default_key
        self._request()

    @staticmethod
    def from_address(address, key=None):
        key = key or OWM.default_key
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
        entry = self.session.get(url).json()
        """
        {'base': 'stations',
         'clouds': {'all': 20},  # %
         'cod': 200,
         'coord': {'lat': 38.72, 'lon': -9.14},
         'dt': 1592522239,
         'id': 8012502,
         'main': {'feels_like': 15.59,
                  'humidity': 87,  # %
                  'pressure': 1019, # hPa
                  'temp': 16.67,  # Celsius, Kelvin, Fahrenheit
                  'temp_max': 17.78,
                  'temp_min': 15.56},
         'name': 'Socorro',
         'sys': {'country': 'PT',
                 'id': 6901,
                 'sunrise': 1592543502,
                 'sunset': 1592597056,
                 'type': 1},
         'timezone': 3600,  # Shift in seconds from UTC
         'visibility': 10000, #  meter
         'weather': [{'description': 'few clouds',
                      'icon': '02n',
                      'id': 801,
                      'main': 'Clouds'}],
         'wind': {'deg': 330, 
                  'speed': 3.6 # m/s
                  }}
        """

        pressure = entry["main"].get("pressure")
        if pressure is not None:
            pressure = DataPoint("Pressure", pressure, "hPa")

        cloudCover = entry.get("clouds", {}).get("all")
        if cloudCover is not None:
            cloudCover = DataPoint("CloudCover", cloudCover, "%")

        visibility = entry.get("visibility")
        if visibility is not None:
            visibility = DataPoint("Visibility", visibility, "m")

        humidity = entry["main"].get("humidity")
        if humidity is not None:
            humidity = DataPoint("Humidity", humidity, "%")

        temperature = entry["main"].get("temp")
        if temperature is not None:
            temperature_min = entry["main"].get("temp_min")
            temperature_max = entry["main"].get("temp_max")
            if self.units == "metric":
                unit = "ºC"
            elif self.units == "si":
                unit = "K"
            else:
                unit = "ºF"
            temperature = DataPoint("Temperature", temperature, unit,
                                    min_val=temperature_min,
                                    max_val=temperature_max)

        ap_temperature = entry["main"].get("feels_like") or temperature
        if ap_temperature is not None:
            if self.units == "metric":
                unit = "ºC"
            elif self.units == "si":
                unit = "K"
            else:
                unit = "ºF"
            ap_temperature = DataPoint("ApparentTemperature", ap_temperature,
                                       unit)

        wind_speed = entry.get("wind", {}).get("speed")
        if wind_speed is not None:
            wind_speed = DataPoint("WindSpeed", wind_speed, "m/s")

        wind_bearing = entry.get("wind", {}).get("deg")
        if wind_bearing is not None:
            wind_bearing = DataPoint("WindBearing", wind_bearing, "º")

        _w = entry.get("weather", [])
        icon = ""
        summary = ""
        if _w:
            icon = _w[0].get("main", "").lower()
            summary = _w[0].get("description") or icon

        # TODO precip
        rain1h = entry.get("rain", {}).get("1h")
        rain3h = entry.get("rain", {}).get("3h")
        if rain3h and not rain1h:
            rain1h = rain3h / 3

        ts = entry["dt"]  # - entry["timezone"]
        date = self._stamp_to_datetime(ts)
        w = {
            "datetime": date,
            "pressure": pressure,
            "cloudCover": cloudCover,
            "visibility": visibility,
            "humidity": humidity,
            "temperature": temperature,
            "apparentTemperature": ap_temperature,
            "windSpeed": wind_speed,
            "windBearing": wind_bearing,
            "summary": summary,
            "icon": icon,
            # "precipIntensity": rain1h or rain3h
        }

        hour = WeatherData.from_dict(w)

        self.data["timezone"] = self.timezone
        self.data["latitude"] = self.latitude
        self.data["longitude"] = self.longitude
        self.data["currently"] = w
        self.data["daily"] = {"summary": w["summary"],
                              "icon": w["icon"],
                              "data": [hour]}
        self.data["hourly"] = {"summary": w["summary"],
                               "icon": w["icon"],
                               "data": [hour]}

    def _request_forecast(self):
        if self.units == "auto":
            OWM_URL = "https://api.openweathermap.org/data/2.5/forecast?lat" \
                      "={lat}&lon={lon}&appid={key}"
            url = OWM_URL.format(key=self.key, lat=self.latitude,
                                 lon=self.longitude)
        else:
            OWM_URL = "https://api.openweathermap.org/data/2.5/forecast?lat" \
                      "={lat}&lon={lon}&appid={key}&units={units}"
            url = OWM_URL.format(key=self.key, lat=self.latitude,
                                 lon=self.longitude,
                                 units=self.units)

        res = self.session.get(url).json()

        # OWM returns 3h in 3h readings
        hours = []
        _days = {}
        for entry in res["list"]:
            pressure = entry["main"].get("pressure")
            if pressure is not None:
                pressure = DataPoint("Pressure", pressure, "hPa")

            cloudCover = entry.get("clouds", {}).get("all")
            if cloudCover is not None:
                cloudCover = DataPoint("CloudCover", cloudCover, "%")

            visibility = entry.get("visibility")
            if visibility is not None:
                visibility = DataPoint("Visibility", visibility, "m")

            humidity = entry["main"].get("humidity")
            if humidity is not None:
                humidity = DataPoint("Humidity", humidity, "%")

            temperature = entry["main"].get("temp")
            if self.units == "metric":
                unit = "ºC"
            elif self.units == "si":
                unit = "k"
            else:
                unit = "ºF"
            if temperature is not None:
                temperature_min = entry["main"].get("temp_min")
                temperature_max = entry["main"].get("temp_max")
                temperature = DataPoint("Temperature", temperature, unit,
                                        min_val=temperature_min,
                                        max_val=temperature_max)

            ap_temperature = entry["main"].get("feels_like")
            if ap_temperature is not None:
                ap_temperature = DataPoint("ApparentTemperature",
                                           ap_temperature,
                                           unit)
            else:
                ap_temperature = DataPoint("ApparentTemperature", temperature,
                                           unit,
                                           min_val=temperature_min,
                                           max_val=temperature_max)

            wind_speed = entry.get("wind", {}).get("speed")
            if wind_speed is not None:
                wind_speed = DataPoint("WindSpeed", wind_speed, "m/s")

            wind_bearing = entry.get("wind", {}).get("deg")
            if wind_bearing is not None:
                wind_bearing = DataPoint("WindBearing", wind_bearing, "º")

            _w = entry.get("weather", [])
            icon = ""
            summary = ""
            if _w:
                icon = _w[0].get("main", "").lower()
                summary = _w[0].get("description") or icon

            # TODO precip
            rain1h = entry.get("rain", {}).get("1h")
            rain3h = entry.get("rain", {}).get("3h")
            if rain3h and not rain1h:
                rain1h = rain3h / 3

            ts = entry["dt"]  # - offset
            date = self._stamp_to_datetime(ts)
            w = {
                "datetime": date,
                "pressure": pressure,
                "cloudCover": cloudCover,
                "visibility": visibility,
                "humidity": humidity,
                "temperature": temperature,
                "apparentTemperature": ap_temperature,
                "windSpeed": wind_speed,
                "windBearing": wind_bearing,
                "summary": summary,
                "icon": icon,
                # "precipIntensity": rain1h or rain3h
            }

            h = WeatherData().from_dict(w)
            hours.append(h)
            if h.datetime.day not in _days:
                _days[h.datetime.day] = []
            _days[h.datetime.day] += [h]

        hourly_summary, hourly_icon = self._calc_hourly_summary(hours)
        self.data["timezone"] = self.timezone
        self.data["latitude"] = self.latitude
        self.data["longitude"] = self.longitude
        self.data["hourly"] = {"summary": hourly_summary,
                               "icon": hourly_icon,
                               "data": hours}

        days = []
        for d in _days:
            day = self._calc_day_average(_days[d])
            day = WeatherData.from_dict(day)
            days += [day]

        daily_summary, daily_icon = self._calc_daily_summary(days)
        self.data["daily"] = {"summary": daily_summary,
                              "icon": daily_icon,
                              "data": days}

    def _request(self):
        self._request_current()
        self._request_forecast()

