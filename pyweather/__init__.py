from datetime import timedelta
from pyweather.time import int_to_weekday
import pendulum
from datetime import datetime


class WeatherDataPoint:
    def __init__(self):
        self.datetime = None
        self.apparentTemperature = None
        self.apparentTemperatureMin = None
        self.apparentTemperatureMax = None
        self.apparentTemperatureMinTime = None
        self.apparentTemperatureMaxTime = None
        self.apparentTemperatureLow = None
        self.apparentTemperatureHigh = None
        self.apparentTemperatureLowTime = None
        self.apparentTemperatureHighTime = None

        self.cloudCover = None
        self.dewPoint = None
        self.humidity = None
        self.icon = None
        self.ozone = None
        self.precipIntensity = None
        self.precipIntensityMin = 0

        self.precipIntensityMax = 1
        self.precipIntensityMaxTime = None
        self.precipProbability = None
        self.pressure = None
        self.summary = None

        self.temperature = None
        self.temperatureMin = None
        self.temperatureMax = None
        self.temperatureMinTime = None
        self.temperatureMaxTime = None
        self.temperatureLow = None
        self.temperatureHigh = None
        self.temperatureLowTime = None
        self.temperatureHighTime = None

        self.uvIndex = None
        self.visibility = None
        self.windBearing = None
        self.windGust = None
        self.windSpeed = None

    def print(self):
        print(self.weekday, self.datetime.date(), self.datetime.time(),
              self.timezone, ":", self.summary)
        print("temperature:", self.temperature)
        print("temperature min:", self.temperatureMin)
        print("temperature max:", self.temperatureMax)
        print("humidity:", self.humidity)
        print("cloudCover:", self.cloudCover)
        print("windSpeed:", self.windSpeed)
        print("precipIntensity:", self.precipIntensity)
        print("precipProbability:", self.precipProbability)
        print("visibility:", self.visibility)

    @property
    def timezone(self):
        if not self.datetime:
            return pendulum.timezone("UTC")
        return self.datetime.timezone_name

    @property
    def weekday(self):
        if self.datetime is None:
            return -1
        return int_to_weekday(self.datetime.weekday())

    def as_json(self):
        data = self.__dict__
        for k in data:
            if isinstance(data[k], datetime):
                data[k] = data[k].timestamp()
        return data

    def _stamp_to_datetime(self, stamp, tz=None):
        tz = tz or self.timezone
        return pendulum.from_timestamp(stamp, tz=tz)

    def from_json(self, data):

        tz = data.get("timezone")
        if data.get("time"):
            self.datetime = self._stamp_to_datetime(data["time"], tz)
        if data.get("datetime"):
            self.datetime = self._stamp_to_datetime(data["datetime"], tz)

        self.temperature = data.get("temperature")
        self.temperatureMin = data.get("temperatureMin") or self.temperature
        self.temperatureMax = data.get("temperatureMax") or self.temperature
        self.temperatureLow = data.get("temperatureLow") or self.temperature
        self.temperatureHigh = data.get("temperatureHigh") or self.temperature

        dt = data.get("temperatureMinTime")
        self.temperatureMinTime = self._stamp_to_datetime(dt) if dt else \
            self.datetime
        dt = data.get("temperatureMaxTime")
        self.temperatureMaxTime = self._stamp_to_datetime(dt) if dt else \
            self.datetime
        dt = data.get("temperatureLowTime")
        self.temperatureLowTime = self._stamp_to_datetime(dt) if dt else \
            self.datetime
        dt = data.get("temperatureHighTime")
        self.temperatureHighTime = self._stamp_to_datetime(dt) if dt else \
            self.datetime
        dt = data.get("apparentTemperatureMinTime ")
        self.apparentTemperatureMinTime = self._stamp_to_datetime(dt) if dt \
            else self.datetime
        dt = data.get("apparentTemperatureMaxTime")
        self.apparentTemperatureMaxTime = self._stamp_to_datetime(dt) if dt \
            else self.datetime
        dt = data.get("apparentTemperatureLowTime")
        self.apparentTemperatureLowTime = self._stamp_to_datetime(dt) if dt \
            else self.datetime
        dt = data.get("apparentTemperatureHighTime ")
        self.apparentTemperatureHighTime = self._stamp_to_datetime(dt) if dt \
            else self.datetime

        self.apparentTemperature = data.get("apparentTemperature") or \
                                   self.temperature
        self.apparentTemperatureMin = data.get("apparentTemperatureMin") or \
                                      self.apparentTemperature
        self.apparentTemperatureMax = data.get("apparentTemperatureMax") or \
                                      self.apparentTemperature
        self.apparentTemperatureLow = data.get("apparentTemperature") or \
                                      self.apparentTemperatureMin
        self.apparentTemperatureHigh = data.get("apparentTemperature") or \
                                       self.apparentTemperatureMax

        self.cloudCover = data.get("cloudCover")
        self.dewPoint = data.get("dewPoint")
        self.humidity = data.get("humidity")
        self.icon = data.get("icon")
        self.ozone = data.get("ozone")
        self.pressure = data.get("pressure")
        self.summary = data.get("summary")
        self.uvIndex = data.get("uvIndex")
        self.visibility = data.get("visibility")
        self.windBearing = data.get("windBearing")
        self.windGust = data.get("windGust")
        self.windSpeed = data.get("windSpeed")

        self.precipIntensity = data.get("precipIntensity")
        self.precipProbability = data.get("precipProbability")
        self.precipIntensityMin = data.get("precipIntensityMin") or 0
        self.precipIntensityMax = data.get("precipIntensityMax") or 1
        dt = data.get("precipIntensityMaxTime")
        self.precipIntensityMaxTime = self._stamp_to_datetime(dt) if dt else None

        return self


class MinuteWeather:
    def __init__(self, date, weather):
        self.datetime = date.replace(second=0,
                                     microsecond=0)
        self.weather = weather

    def print(self):
        self.weather.print()

    def as_json(self):
        return {"datetime": self.datetime,
                "weather": self.weather.as_json()}

    @property
    def weekday(self):
        if self.datetime is None:
            return -1
        return int_to_weekday(self.datetime.weekday())

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def __repr__(self):
        return str(self.datetime) + ":" + self.weather.summary


class HourWeather:
    def __init__(self, date, weather):
        self.datetime = date.replace(minute=0, second=0,
                                     microsecond=0)
        self.weather = weather
        self.minutes = []
        for i in range(60):
            minute = self.datetime + timedelta(minutes=i)
            self.minutes.append(MinuteWeather(minute, weather))

    def print(self):
        self.weather.print()

    def as_json(self):
        return {"datetime": self.datetime,
                "minutes": [m.as_json() for m in self.minutes],
                "weather": self.weather.as_json()}

    @property
    def weekday(self):
        if self.datetime is None:
            return -1
        return int_to_weekday(self.datetime.weekday())

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def __repr__(self):
        return str(self.datetime) + ":" + self.weather.summary


class DayWeather:
    def __init__(self, date, weather):
        self.datetime = date.replace(hour=0, minute=0, second=0,
                                     microsecond=0)
        self.weather = weather
        self.hours = []
        for i in range(24):
            hour = self.datetime + timedelta(hours=i)
            self.hours.append(HourWeather(hour, weather))

        self.sunriseTime = None
        self.sunsetTime = None
        self.moonPhase = None

    def as_json(self):
        return {"datetime": self.datetime,
                "sunsetTime": self.sunsetTime,
                "sunriseTime": self.sunriseTime,
                "moonPhase": self.moonPhase,
                "hours": [m.as_json() for m in self.hours],
                "weather": self.weather.as_json()}

    def print(self):
        self.weather.print()

    @property
    def weekday(self):
        if self.datetime is None:
            return -1
        return int_to_weekday(self.datetime.weekday())

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def __repr__(self):
        return str(self.datetime) + ":" + self.weather.summary


class MinutelyForecast:
    def __init__(self, date, minutes, weather):
        self.datetime = date
        self.minutes = minutes
        self.weather = weather

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def print(self):
        print(self.datetime, ":", self.summary)

    def as_json(self):
        return {"datetime": self.datetime,
                "minutes": [m.as_json() for m in self.minutes],
                "weather": self.weather.as_json()}


class HourlyForecast:
    def __init__(self, date, hours, weather):
        self.datetime = date
        self.hours = hours
        self.weather = weather

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def print(self):
        print(self.datetime, ":", self.summary)

    def as_json(self):
        return {"datetime": self.datetime,
                "hours": [m.as_json() for m in self.hours],
                "weather": self.weather.as_json()}


class DailyForecast:
    def __init__(self, date, days, weather):
        self.datetime = date
        self.days = days
        self.weather = weather

    def print(self):
        print(self.datetime, ":", self.summary)

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def as_json(self):
        return {"datetime": self.datetime,
                "days": [m.as_json() for m in self.days],
                "weather": self.weather.as_json()}
