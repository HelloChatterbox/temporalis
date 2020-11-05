from temporalis.location import geolocate, get_timezone
from temporalis.sun import get_dawn, get_dusk, get_sunrise, get_sunset, get_noon
from temporalis import WeatherData, DailyForecast, HourlyForecast
from temporalis.time import now_utc
from temporalis.moon import get_moon_phase, moon_code_to_symbol, \
    moon_code_to_name
from pendulum import timezone
import pendulum
from requests_cache import CachedSession
from datetime import timedelta


class WeatherProvider:
    expire_after = timedelta(hours=1)
    session = CachedSession(backend='memory', expire_after=expire_after)

    def __init__(self, lat, lon, date=None, units="metric", lang="en"):
        self.lang = lang
        self.datetime = date or now_utc()
        if units in ["english", "imperial", "us"]:
            units = "us"

        # units=[units] optional
        #
        # Return weather conditions in the requested units.
        # [units] should be one of the following:
        #
        #     auto: automatically select units based on geographic location
        #     ca: same as si, except that windSpeed and windGust are in kilometers per hour
        #     uk2: same as si, except that nearestStormDistance and visibility are in miles, and windSpeed and windGust in miles per hour
        #     us: Imperial units (the default)
        #     si: SI units

        # SI units are as follows:
        #
        #     summary: Any summaries containing temperature or snow accumulation units will have their values in degrees Celsius or in centimeters (respectively).
        #     nearestStormDistance: Kilometers.
        #     precipitation: Millimeters per hour.
        #     precipitation.max_val: Millimeters per hour.
        #     precipAccumulation: Centimeters.
        #     temperature: Degrees Celsius.
        #     temperature.min_val: Degrees Celsius.
        #     temperature.max_val: Degrees Celsius.
        #     apparentTemperature: Degrees Celsius.
        #     dewPoint: Degrees Celsius.
        #     windSpeed: Meters per second.
        #     windGust: Meters per second.
        #     pressure: Hectopascals.
        #     visibility: Kilometers.
        self._units = units

        self.data = {"latitude": lat,
                     "longitude": lon,
                     "timezone": self.datetime.timezone_name,
                     "units": self._units,
                     "currently": {},
                     "daily": {},
                     "hourly": {}}

    # sun
    @property
    def dawn(self):
        return get_dawn(self.latitude, self.longitude, self.datetime)

    @property
    def sunrise(self):
        return get_sunrise(self.latitude, self.longitude, self.datetime)

    @property
    def noon(self):
        return get_noon(self.latitude, self.longitude, self.datetime)

    @property
    def sunset(self):
        return get_sunset(self.latitude, self.longitude, self.datetime)

    @property
    def dusk(self):
        return get_dusk(self.latitude, self.longitude, self.datetime)

    # moon
    @property
    def moon_phase(self):
        return get_moon_phase(self.datetime)[0]

    @property
    def moon_code(self):
        return get_moon_phase(self.datetime)[1]

    @property
    def moon_symbol(self):
        return moon_code_to_symbol(self.moon_code)

    @property
    def moon_phase_name(self):
        return moon_code_to_name(self.moon_code, self.lang)

    # localization
    @property
    def units(self):
        return self._units

    @property
    def latitude(self):
        return self.data["latitude"]

    @property
    def longitude(self):
        return self.data["longitude"]

    @staticmethod
    def from_address(address, key=None):
        lat, lon = geolocate(address)
        return WeatherProvider(lat, lon)

    @property
    def timezone(self):
        return get_timezone(latitude=self.latitude, longitude=self.longitude)

    # weather forecasts
    @property
    def weather(self):
        return WeatherData().from_dict(self.data["currently"])

    @property
    def weather_tomorrow(self):
        return self.weather_in_n_days(1)

    def weather_in_n_days(self, n):
        if n >= len(self.days):
            raise OverflowError
        return self.days[n].weather

    @property
    def hourly(self):
        daily = self.data["hourly"]

        hourly_weather = WeatherData()
        hourly_weather.icon = daily["icon"]
        hourly_weather.summary = daily["summary"]
        hourly_weather.datetime = self.datetime

        hours = []
        for hour in daily["data"]:
            if isinstance(hour, dict):
                weather = WeatherData().from_dict(hour)
            else:
                weather = hour
            hours.append(weather)

        return HourlyForecast(self.datetime, hours, hourly_weather)

    @property
    def hours(self):
        return self.hourly.hours

    @property
    def daily(self):
        daily = self.data["daily"]

        daily_weather = WeatherData()
        if daily.get("icon"):
            daily_weather.icon = daily["icon"]
            daily_weather.summary = daily["summary"]
        else:
            daily_weather.icon = daily["data"][0].icon
            daily_weather.summary = daily["data"][0].summary
        daily_weather.datetime = self.datetime
        return DailyForecast(self.datetime, daily["data"], daily_weather)

    @property
    def days(self):
        return self.daily.days

    # pretty print
    def print(self):
        self.weather.print()

    def print_daily(self):
        # self.daily.print()
        for day in self.days:
            print(day.weekday, ":", day.datetime.date(), ":", day.summary)

    def print_hourly(self):
        # self.hourly.print()
        for hour in self.hours:
            print(hour.weekday, ":", hour.datetime.time(), ":", hour.summary)

    # internals
    def _stamp_to_datetime(self, stamp, tz_name=None):
        if tz_name:
            return pendulum.from_timestamp(stamp, tz=timezone(tz_name))
        return pendulum.from_timestamp(stamp, tz=self.timezone)

    @staticmethod
    def _calc_day_average(hours):
        data = hours[0].as_dict()

        for idx, d in enumerate(hours):
            new_data = d.as_dict()
            for k in new_data:
                try:
                    if new_data[k]["min_val"] < data[k]["min_val"]:
                        data[k]["min_val"] = new_data[k]["min_val"]
                        data[k]["min_time"] = new_data[k]["time"]
                    if new_data[k]["max_val"] > data[k]["max_val"]:
                        data[k]["max_val"] = new_data[k]["max_val"]
                        data[k]["max_time"] = new_data[k]["time"]
                    offset = new_data[k]["max_val"] - new_data[k]["min_val"]
                    new_data[k]["val"] = new_data[k]["min_val"] + offset / 2
                except:
                    pass
                try:
                    if new_data[k]["prob_min"] < data[k]["prob_min"]:
                        data[k]["prob_min"] = new_data[k]["prob_min"]
                    if new_data[k]["prob_max"] > data[k]["prob_max"]:
                        data[k]["prob_max"] = new_data[k]["prob_max"]
                    offset = new_data[k]["prob_max"] - new_data[k]["prob_min"]
                    new_data[k]["prob"] = new_data[k]["prob_min"] + offset / 2
                except:
                    pass

        return data

    @staticmethod
    def _calc_hourly_summary(hours):
        hourly_summary = hours[0].summary
        hourly_icon = hours[0].icon
        return hourly_summary, hourly_icon

    @staticmethod
    def _calc_daily_summary(days):
        hourly_summary = days[0].summary
        hourly_icon = days[0].icon
        return hourly_summary, hourly_icon
