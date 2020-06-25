from pyweather.location import geolocate
from pyweather.providers import WeatherProvider


class AcuWeather(WeatherProvider):
    default_key = "fqsDinDA7J91HZCQZFIhprpY0ywvniGK"

    def __init__(self, lat, lon, key=None, date=None, units="metric"):
        super().__init__(lat, lon, date, units)
        self.key = key or self.default_key
        raise NotImplementedError
        self.url = "api_url".format(key=key, lat=lat, lon=lon)
        self.data = self._request()

    @staticmethod
    def from_address(address, key=None):
        lat, lon = geolocate(address)
        return AcuWeather(lat, lon, key)

    def _request(self):
        raise NotImplementedError


if __name__ == "__main__":
    lat, lon = 38.7222563442538, -9.1393314973889
    d = AcuWeather(lat, lon)

    from pprint import pprint

    pprint(d.data)

    while True:
        pass
    print("##### CURRENT WEATHER ######")
    d.print()

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()
