from temporalis.location import geolocate
from temporalis.providers import WeatherProvider
from temporalis.location import geolocate
from temporalis.providers import WeatherProvider
from temporalis import WeatherData, DataPoint
from pendulum import now


class DarkSky(WeatherProvider):
    def __init__(self, lat, lon, key, date=None, units="metric"):
        print("WARNING: darksky is shutting down, see https://blog.darksky.net/")
        if units in ["english", "imperial", "us"]:
            units = "us"
        elif units == "metric":
            units = "si"
        elif units not in ["uk2", "ca", "si"]:
            units = "auto"
        super().__init__(lat, lon, date, units)
        self.key = key
        if date:
            DARKSKY_URL = "https://api.darksky.net/forecast/{key}/{latitude},{longitude},{time}"
            time = int(date.timestamp())
            self.url = DARKSKY_URL.format(key=key, latitude=lat,
                                          longitude=lon, time=time)
        else:
            DARKSKY_URL = "https://api.darksky.net/forecast/{key}/{latitude},{longitude}"
            self.url = DARKSKY_URL.format(key=key, latitude=lat, longitude=lon)
        self._request()

        """
        SI units are as follows:

        summary: Any summaries containing temperature or snow accumulation units will have their values in degrees Celsius or in centimeters (respectively).
        nearestStormDistance: Kilometers.
        precipIntensity: Millimeters per hour.
        precipIntensityMax: Millimeters per hour.
        precipAccumulation: Centimeters.
        temperature: Degrees Celsius.
        temperatureMin: Degrees Celsius.
        temperatureMax: Degrees Celsius.
        apparentTemperature: Degrees Celsius.
        dewPoint: Degrees Celsius.
        windSpeed: Meters per second.
        windGust: Meters per second.
        pressure: Hectopascals.
        visibility: Kilometers.
        """

    @staticmethod
    def from_address(address, key):
        lat, lon = geolocate(address)
        return DarkSky(lat, lon, key)

    def _request(self):
        params = {"units": self._units}
        data = self.session.get(self.url, params=params).json()

        current = data["currently"]
        daily = data["daily"]
        hourly = data["hourly"]

        def entry2point(entry):
            date = entry["time"]

            pressure = entry.get("pressure")
            if pressure is not None:
                pressure = DataPoint("Pressure", pressure, "hPa")

            cloudCover = entry.get("cloudCover")
            if cloudCover is not None:
                cloudCover = DataPoint("CloudCover", cloudCover, "%")

            visibility = entry.get("visibility")
            if visibility is not None:
                if self.units == "si":
                    visibility = DataPoint("Visibility", visibility, "km")
                elif self.units == "us":
                    # TODO  unit
                    visibility = DataPoint("Visibility", visibility, "km")

            precip = entry.get("precipIntensity")
            if precip is not None:
                maxprecip = entry.get("precipIntensityMax") or precip
                max_time = entry.get("precipIntensityMaxTime") or date
                max_time = self._stamp_to_datetime(max_time)
                prob = entry.get("precipProbability")
                if self.units == "si":
                    precip = DataPoint("PrecipitationIntensity", precip,
                                       "mm/hr", max_val=maxprecip,
                                       max_time=max_time, prob=prob)
                elif self.units == "us":
                    # TODO unit
                    precip = DataPoint("PrecipitationIntensity", precip,
                                       "mm/hr", max_val=maxprecip,
                                       max_time=max_time, prob=prob)

            humidity = entry.get("humidity")
            if humidity is not None:
                humidity = DataPoint("Humidity", humidity, "%")

            uv = entry.get("uvIndex")
            if uv is not None:
                uvtime = entry.get("uvIndexTime") or date
                uv = DataPoint("UV Index", uv, "dimensionless", time=uvtime)

            temperature = entry.get("temperature")
            if temperature is not None:
                high = entry.get('temperatureHigh') or temperature
                low = entry.get('temperatureLow') or temperature
                min_temp = entry.get('temperatureMin') or temperature
                max_temp = entry.get('temperatureMax') or temperature
                high_time = entry.get('temperatureHighTime') or date
                low_time = entry.get('temperatureLowTime') or date
                min_time = entry.get('temperatureMinTime') or date
                max_time = entry.get('temperatureMaxTime') or date
                high_time = self._stamp_to_datetime(high_time)
                low_time = self._stamp_to_datetime(low_time)
                min_time = self._stamp_to_datetime(min_time)
                max_time = self._stamp_to_datetime(max_time)

                if self.units == "si":
                    temperature = DataPoint("Temperature", temperature, "ºC",
                                            min_val=min_temp, max_val=max_temp,
                                            high_val=high,  low_val=low,
                                            min_time=min_time,
                                            max_time=max_time,
                                            low_time=low_time,
                                            high_time=high_time)
                elif self.units == "us":
                    temperature = DataPoint("Temperature", temperature, "ºF",
                                            min_val=min_temp, max_val=max_temp,
                                            high_val=high,  low_val=low,
                                            min_time=min_time,
                                            max_time=max_time,
                                            low_time=low_time,
                                            high_time=high_time)

            ap_temperature = entry.get("apparentTemperature") or temperature
            if ap_temperature is not None:
                high = entry.get('apparentTemperatureHigh') or ap_temperature
                low = entry.get('apparentTemperatureLow') or ap_temperature
                min_temp = entry.get('apparentTemperatureMin') or ap_temperature
                max_temp = entry.get('apparentTemperatureMax') or ap_temperature
                high_time = entry.get('apparentTemperatureHighTime') or date
                low_time = entry.get('apparentTemperatureLowTime') or date
                min_time = entry.get('apparentTemperatureMinTime') or date
                max_time = entry.get('apparentTemperatureMaxTime') or date
                high_time = self._stamp_to_datetime(high_time)
                low_time = self._stamp_to_datetime(low_time)
                min_time = self._stamp_to_datetime(min_time)
                max_time = self._stamp_to_datetime(max_time)

                if self.units == "si":
                    ap_temperature = DataPoint("ApparentTemperature",
                                               ap_temperature, "ºC",
                                            min_val=min_temp, max_val=max_temp,
                                            high_val=high,  low_val=low,
                                            min_time=min_time,
                                            max_time=max_time,
                                            low_time=low_time,
                                            high_time=high_time)
                elif self.units == "us":
                    ap_temperature = DataPoint("ApparentTemperature",
                                               ap_temperature, "ºF",
                                            min_val=min_temp, max_val=max_temp,
                                            high_val=high,  low_val=low,
                                            min_time=min_time,
                                            max_time=max_time,
                                            low_time=low_time,
                                            high_time=high_time)

            dew = entry.get("dewPoint")
            if dew is not None:
                if self.units == "si":
                    dew = DataPoint("DewPoint", dew, "ºC")
                elif self.units == "us":
                    dew = DataPoint("DewPoint", dew, "ºF")

            wind_speed = entry.get("windSpeed")
            if wind_speed is not None:
                if self.units == "si":
                    wind_speed = DataPoint("WindSpeed", wind_speed, "m/s")
                elif self.units == "us":
                    wind_speed = DataPoint("WindSpeed", wind_speed, "mph")

            wind_bearing = entry.get("windBearing")
            if wind_bearing is not None:
                wind_bearing = DataPoint("WindBearing", wind_bearing, "º")

            wind_gust = entry.get("windGust")
            if wind_gust is not None:
                gusttime = entry.get("windGustTime") or date
                gusttime = self._stamp_to_datetime(gusttime)
                if self.units == "si":
                    wind_gust = DataPoint("WindGust", wind_gust, "m/s",
                                          time=gusttime)
                elif self.units == "us":
                    wind_gust = DataPoint("WindGust", wind_gust, "mph",
                                          time=gusttime)

            icon = entry.get("icon", "").lower()
            summary = entry.get("summary") or icon
            date = self._stamp_to_datetime(entry["time"])

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
                "windGust": wind_gust,
                "summary": summary,
                "icon": icon,
                "precipitation": precip,
                "uvIndex": uv,
                "dewPoint": dew
            }
            return w

        current = entry2point(current)
        days = [entry2point(w) for w in daily["data"]]
        hours = [entry2point(w) for w in hourly["data"]]
        days = [WeatherData.from_dict(w) for w in days]
        hours = [WeatherData.from_dict(w) for w in hours]

        self.data["timezone"] = self.timezone
        self.data["latitude"] = self.latitude
        self.data["longitude"] = self.longitude
        self.data["currently"] = current
        self.data["daily"] = {"summary": daily["summary"],
                              "icon": daily["icon"],
                              "data": days}
        self.data["hourly"] = {"summary": hourly["summary"],
                               "icon": hourly["icon"],
                               "data": hours}


if __name__ == "__main__":
    from pprint import pprint

    lat, lon = 38.7222, -9.1393
    DARKSKY_KEY = ""
    d = DarkSky(lat, lon, DARKSKY_KEY)



    pprint(d.data)


    print("##### CURRENT WEATHER ######")
    d.print()

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()