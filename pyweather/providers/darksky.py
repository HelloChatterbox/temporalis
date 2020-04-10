from pyweather.location import geolocate
import requests
from pyweather.providers import WeatherProvider


class DarkSky(WeatherProvider):
    def __init__(self, lat, lon, key, date=None, units="metric"):
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
        self.data = self._request()

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

    @property
    def units(self):
        return self.data["flags"]["units"]

    @staticmethod
    def from_address(address, key):
        lat, lon = geolocate(address)
        return DarkSky(lat, lon, key)

    def _request(self):
        params = {"units": self._units}
        return requests.get(self.url, params=params).json()


if __name__ == "__main__":
    lat, lon = 38.7222, -9.1393
    DARKSKY_KEY = "XXXXX"
    #d = DarkSky.from_address("Campbell California", DARKSKY_KEY)
    #date = now()
    d = DarkSky(lat, lon, DARKSKY_KEY)
    print("##### CURRENT WEATHER ######")
    d.print()

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()