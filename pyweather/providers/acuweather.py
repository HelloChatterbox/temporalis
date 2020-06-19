from pyweather.location import geolocate
import requests
from pyweather.providers import WeatherProvider
from pprint import pprint
from pendulum import now, timezone
import pendulum

ACUWEATHER_KEY = "fqsDinDA7J91HZCQZFIhprpY0ywvniGK"


class AcuWeather(WeatherProvider):
    def __init__(self, lat, lon, key=ACUWEATHER_KEY, date=None, units="metric"):
        super().__init__(lat, lon, date, units)
        self.key = key
        OWM_URL = "https://api.openweathermap.org/data/2.5/weather?lat={" \
                  "lat}&lon={lon}&appid={key}"
        self.url = OWM_URL.format(key=key, lat=lat, lon=lon)

        self.data = self._request()

    def _stamp_to_datetime(self, stamp):
        return pendulum.from_timestamp(stamp, tz=timezone("UTC"))

    @staticmethod
    def from_address(address, key):
        lat, lon = geolocate(address)
        return OWM(lat, lon, key)

    def _request(self):
        # TODO unis
        res = requests.get(self.url).json()
        pprint(res)
        w = {
            "time": res["dt"],
            "pressure": res["main"]["pressure"],
            "cloudCover": res["clouds"]["all"] / 100,
            "visibility": res["visibility"] / 1000,
            "humidity": res["main"]["humidity"] / 100,
            "temperature": res["main"]["temp"],
            "apparentTemperature": res["main"]["feels_like"],
            "temperatureMin": res["main"]["temp_min"],
            "temperatureMax": res["main"]["temp_max"],
            "windSpeed": res["wind"]["speed"],
            "windBearing": res["wind"]["deg"],
            "sunriseTime": res["sys"]["sunrise"],
            "sunsetTime": res["sys"]["sunset"],
            "summary": res["weather"][0]["description"],
            "icon": res["weather"][0]["main"].lower()
        }
        data = {
            "timezone": self.datetime.timezone_name,
            "latitude": res["coord"]["lat"],
            "longitude": res["coord"]["lon"],
            "currently": w,
            "daily": {"summary": w["summary"],
                      "icon": w["icon"],
                      "data": [w]},
            "hourly": {"summary": w["summary"],
                       "icon": w["icon"],
                       "data": [w]}
        }
        pprint(data)
        return data


if __name__ == "__main__":
    lat, lon = 38.7222563442538, -9.1393314973889
    # d = OWM.from_address("Lisbon Portugal", OWM_KEY)
    date = now()
    d = OWM(lat, lon, OWM_KEY)

    from pprint import pprint

    # pprint(d.data)

    while True:
        pass
    print("##### CURRENT WEATHER ######")
    d.print()

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    print("\n##### HOURLY FORECAST ######")
    d.print_hourly()
