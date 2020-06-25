from pyweather.exceptions import InvalidKey
from pyweather.location import geolocate
from pyweather.providers import WeatherProvider
from pyweather import WeatherData, DataPoint


class WeatherBit(WeatherProvider):
    default_key = "fd088ec43bef4769b87d347d3dec83e5"

    def __init__(self, lat, lon, key=None, date=None, units="metric"):
        if units in ["english", "imperial", "us"]:
            units = "I"
        elif units.startswith("m"):
            units = "M"
        else:
            units = "S"
        super().__init__(lat, lon, date, units)
        self.key = key or self.default_key
        self.url = "https://api.weatherbit.io/v2.0/current"
        self._request()

    @staticmethod
    def from_address(address, key=None):
        lat, lon = geolocate(address)
        return WeatherBit(lat, lon, key)

    def _request_current(self):
        params = {"units": self.units,
                  "lat": self.latitude,
                  "lon": self.longitude,
                  "key": self.key}
        entry = self.session.get(self.url, params=params).json()
        entry = entry["data"][0]
        # {'rh': 84, 'pod': 'n', 'lon': -9.14, 'pres': 1003,
        # 'timezone': 'Europe/Lisbon', 'ob_time': '2020-06-25 00:20',
        # 'country_code': 'PT', 'clouds': 68, 'ts': 1593044400, 'solar_rad': 0,
        # 'state_code': '14', 'city_name': 'Lisbon', 'wind_spd': 1.79,
        # 'last_ob_time': '2020-06-25T00:20:00', 'wind_cdir_full': 'northwest',
        # 'wind_cdir': 'NW', 'slp': 1015.5, 'vis': 5, 'h_angle': -90,
        # 'sunset': '20:05', 'dni': 0, 'dewpt': 14.5, 'snow': 0, 'uv': 0,
        # 'precip': 0, 'wind_dir': 326, 'sunrise': '05:12', 'ghi': 0, 'dhi': 0,
        # 'aqi': 45, 'lat': 38.72, 'weather': {'icon': 'c02n', 'code': '802',
        # 'description': 'Scattered clouds'}, 'datetime': '2020-06-25:00',
        # 'temp': 17.2, 'station': 'C3643', 'elev_angle': -27.23,
        # 'app_temp': 17.3}
        """
    TODO 
    
    slp: Sea level pressure (mb).
    wind_cdir: Abbreviated wind direction.
    wind_cdir_full: Verbal wind direction.
    dewpt: Dew point (default Celcius).
    aqi: Air Quality Index [US - EPA standard 0 - +500]
    dhi: Diffuse horizontal solar irradiance (W/m^2) [Clear Sky]
    dni: Direct normal solar irradiance (W/m^2) [Clear Sky]
    ghi: Global horizontal solar irradiance (W/m^2) [Clear Sky]
    solar_rad: Estimated Solar Radiation (W/m^2).
    elev_angle: Solar elevation angle (degrees).
    h_angle: Solar hour angle (degrees).
        """
        pressure = entry.get("pres")
        if pressure is not None:
            pressure = DataPoint("Pressure", pressure, "mb")

        cloudCover = entry.get("clouds")
        if cloudCover is not None:
            cloudCover = DataPoint("CloudCover", cloudCover, "%")

        visibility = entry.get("vis")
        if visibility is not None:
            if self.units == "M" or self.units == "S":
                visibility = DataPoint("Visibility", visibility, "km")
            elif self.units == "I":
                # TODO  unit
                visibility = DataPoint("Visibility", visibility, "km")

        precip = entry.get("precip")
        if precip is not None:
            if self.units == "M" or self.units == "S":
                precip = DataPoint("PrecipitationIntensity", precip, "mm/hr")
            elif self.units == "I":
                # TODO unit
                precip = DataPoint("PrecipitationIntensity", precip, "mm/hr")

        snow = entry.get("snow")
        if snow is not None:
            if self.units == "M" or self.units == "S":
                snow = DataPoint("SnowIntensity", snow, "mm/hr")
            elif self.units == "I":
                # TODO  unit
                snow = DataPoint("SnowIntensity", snow, "mm/hr")

        humidity = entry.get("rh")
        if humidity is not None:
            humidity = DataPoint("Humidity", humidity, "%")

        uv = entry.get("uv")
        if uv is not None:
            uv = DataPoint("UV Index", uv, "dimensionless")

        temperature = entry.get("temp")
        if temperature is not None:
            if self.units == "M":
                temperature = DataPoint("Temperature", temperature, "ºC")
            elif self.units == "S":
                temperature = DataPoint("Temperature", temperature, "K")
            elif self.units == "I":
                temperature = DataPoint("Temperature", temperature, "ºF")

        ap_temperature = entry.get("app_temp")
        if ap_temperature is not None:
            if self.units == "M":
                ap_temperature = DataPoint("ApparentTemperature",
                                           ap_temperature, "ºC")
            elif self.units == "S":
                ap_temperature = DataPoint("ApparentTemperature",
                                           ap_temperature, "K")
            elif self.units == "I":
                ap_temperature = DataPoint("ApparentTemperature",
                                           ap_temperature, "ºF")

        dew = entry.get("dewpt")
        if dew is not None:
            if self.units == "M":
                dew = DataPoint("DewPoint", dew, "ºC")
            elif self.units == "S":
                dew = DataPoint("DewPoint", dew, "K")
            elif self.units == "I":
                dew = DataPoint("DewPoint", dew, "ºF")

        wind_speed = entry.get("wind_spd")
        if wind_speed is not None:
            if self.units == "M" or self.units == "S":
                wind_speed = DataPoint("WindSpeed", wind_speed, "m/s")
            elif self.units == "I":
                wind_speed = DataPoint("WindSpeed", wind_speed, "mph")

        wind_bearing = entry.get("wind_dir")
        if wind_bearing is not None:
            wind_bearing = DataPoint("WindBearing", wind_bearing, "º")

        _w = entry.get("weather", {})
        icon = ""
        summary = ""
        if _w:
            icon = _w.get("code", "").lower()
            summary = _w.get("description") or icon

        ts = entry["ts"]
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
            "precipitation": precip,
            "uvIndex": uv,
            "snow": snow,
            "dewPoint": dew
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
        params = {"units": self.units,
                  "lat": self.latitude,
                  "lon": self.longitude,
                  "key": self.key}
        res = self.session.get(
            "https://api.openweathermap.org/data/2.5/forecast",
            params=params).json()

        if res["cod"] == 401:
            raise InvalidKey(res["message"])

        raise NotImplementedError

    def _request(self):
        self._request_current()
        # TODO - need paid key
        # self._request_forecast()


if __name__ == "__main__":
    lat, lon = 38.7222563442538, -9.1393314973889
    d = WeatherBit(lat, lon)

    print("##### CURRENT WEATHER ######")
    d.print()

    ## WIP ZONE

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()
