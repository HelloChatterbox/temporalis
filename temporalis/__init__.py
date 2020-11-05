from temporalis.time import int_to_weekday
import pendulum
from pprint import pprint


class DataPoint:
    def __init__(self, name, value, units,
                 min_val=None, max_val=None,
                 low_val=None, high_val=None,
                 time=None, min_time=None, max_time=None,
                 low_time=None, high_time=None,
                 prob=None, prob_min=None, prob_max=None):
        self.name = name
        self.units = units
        self.value = value
        self.min_val = min_val or value
        self.max_val = max_val or value
        self.low_val = low_val or self.min_val
        self.high_val = high_val or self.max_val
        self.prob = prob  # probability of value
        self.prob_min = prob_min or prob  # probability of min_value
        self.prob_max = prob_max or prob  # probability of max_value
        self.time = time  # ts of prediction
        self.min_time = min_time or time  # predicted ts for min
        self.max_time = max_time or time  # predicted ts for max
        self.low_time = low_time or time
        self.high_time = high_time or time

    @staticmethod
    def _stamp_to_datetime(stamp, tz=None):
        tz = tz or "UTC"
        return pendulum.from_timestamp(stamp, tz=tz)

    def as_dict(self):
        data = self.__dict__
        for k in dict(data):
            if not data[k]:
                data.pop(k)
        return data

    @staticmethod
    def from_dict(data):
        if not isinstance(data, int) and not data:
            return None
        if isinstance(data, DataPoint):
            return data
        assert isinstance(data, dict)
        name = data["name"]
        units = data.get("units") or data.get("unit")
        tz = data.get("timezone")
        dt = None
        if data.get("time"):
            dt = data["time"]
            try:
                dt = DataPoint._stamp_to_datetime(data["time"], tz)
            except:
                pass
        if data.get("datetime"):
            dt = data["datetime"]
            try:
                dt = DataPoint._stamp_to_datetime(data["datetime"], tz)
            except:
                pass

        time = min_time = max_time = dt
        value = min_val = max_val = data.get("value")
        prob = prob_min = prob_max = data.get("prob")
        min_val = data.get("min_val") or data.get("min_value") or min_val
        max_val = data.get("max_val") or data.get("max_value") or max_val
        prob_min = data.get("min_prob") or data.get("prob_min") or prob_min
        prob_max = data.get("max_prob") or data.get("prob_max") or prob_max
        return DataPoint(name, value, units, min_val, max_val, time,
                         min_time, max_time, prob, prob_min, prob_max)

    def __repr__(self):
        return str(self.value) + " " + self.units


# timestamped weather data
class WeatherData:
    def __init__(self):
        self.datetime = None
        self.apparentTemperature = None
        self.cloudCover = None
        self.dewPoint = None
        self.humidity = None
        self.icon = None
        self.ozone = None
        self.precipitation = None
        self.pressure = None
        self.summary = None
        self.temperature = None
        self.uvIndex = None
        self.visibility = None
        self.windBearing = None
        self.windGust = None
        self.windSpeed = None
        self.snow = None

    def __repr__(self):
        return str(self.datetime) + ":" + self.summary

    def pprint(self):
        pprint(self.as_dict())

    def print(self):
        print(self.weekday, self.datetime.date(), self.datetime.time(),
              self.timezone, ":", self.summary)
        print("temperature:", self.temperature)
        print("humidity:", self.humidity)
        print("cloudCover:", self.cloudCover)
        print("windSpeed:", self.windSpeed)
        print("precipitation:", self.precipitation)
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

    def as_dict(self):
        data = self.__dict__
        for k in dict(data):
            try:
                data[k] = data[k].as_dict()
            except:
                pass
            if not data[k]:
                data.pop(k)
        return data

    def _stamp_to_datetime(self, stamp, tz=None):
        tz = tz or self.timezone
        return pendulum.from_timestamp(stamp, tz=tz)

    @staticmethod
    def from_dict(data):
        assert isinstance(data, dict)
        point = WeatherData()
        point.icon = data.get("icon")
        point.summary = data.get("summary")

        if data.get("datetime"):
            dt = data["datetime"]
            try:
                dt = point._stamp_to_datetime(data["datetime"])
            except:
                pass
            point.datetime = dt

        point.temperature = DataPoint.from_dict(data.get("temperature"))
        point.apparentTemperature = DataPoint.from_dict(
            data.get("apparentTemperature")) or point.temperature

        point.cloudCover = DataPoint.from_dict(data.get("cloudCover"))
        point.dewPoint = DataPoint.from_dict(data.get("dewPoint"))
        point.humidity = DataPoint.from_dict(data.get("humidity"))
        point.ozone = DataPoint.from_dict(data.get("ozone"))
        point.pressure = DataPoint.from_dict(data.get("pressure"))
        point.uvIndex = DataPoint.from_dict(data.get("uvIndex"))
        point.visibility = DataPoint.from_dict(data.get("visibility"))
        point.windBearing = DataPoint.from_dict(data.get("windBearing"))
        point.windGust = DataPoint.from_dict(data.get("windGust"))
        point.windSpeed = DataPoint.from_dict(data.get("windSpeed"))
        point.precipitation = DataPoint.from_dict(data.get("precipitation"))
        point.snow = DataPoint.from_dict(data.get("snow"))

        return point


# Collection of forecasts
class HourlyForecast:
    def __init__(self, date, hours, weather):
        self.datetime = date
        self.hours = hours
        self.weather = weather

    def __getitem__(self, item):
        return self.hours[item]

    def __iter__(self):
        for m in self.hours:
            yield m

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def print(self):
        print(self.datetime, ":", self.summary)

    def pprint(self):
        pprint(self.as_dict())

    def as_dict(self):
        return {"datetime": self.datetime,
                "hours": [m.as_dict() for m in self.hours],
                "weather": self.weather.as_dict()}


class DailyForecast:
    def __init__(self, date, days, weather):
        self.datetime = date
        self.days = days
        self.weather = weather

    def __getitem__(self, item):
        return self.days[item]

    def __iter__(self):
        for m in self.days:
            yield m

    def print(self):
        print(self.datetime, ":", self.summary)

    def pprint(self):
        pprint(self.as_dict())

    @property
    def summary(self):
        return self.weather.summary

    @property
    def icon(self):
        return self.weather.icon

    def as_dict(self):
        return {"datetime": self.datetime,
                "days": [m.as_dict() for m in self.days],
                "weather": self.weather.as_dict()}
