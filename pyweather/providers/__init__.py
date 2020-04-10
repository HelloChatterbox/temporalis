from pyweather.location import geolocate
from pyweather import WeatherDataPoint, DailyForecast, HourlyForecast, \
    MinutelyForecast, DayWeather, HourWeather, MinuteWeather
from pendulum import now, timezone
import pendulum
from pprint import pprint


class WeatherProvider:
    def __init__(self, lat, lon, date=None, units="metric"):

        self.datetime = date or now()
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
        #     precipIntensity: Millimeters per hour.
        #     precipIntensityMax: Millimeters per hour.
        #     precipAccumulation: Centimeters.
        #     temperature: Degrees Celsius.
        #     temperatureMin: Degrees Celsius.
        #     temperatureMax: Degrees Celsius.
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
    def from_address(address, key):
        lat, lon = geolocate(address)
        return WeatherProvider(lat, lon, key)

    @property
    def timezone(self):
        tz = self.data["timezone"]
        return timezone(tz)

    def _stamp_to_datetime(self, stamp, tz_name=None):
        if tz_name:
            return pendulum.from_timestamp(stamp, tz=timezone(tz_name))
        return pendulum.from_timestamp(stamp, tz=self.timezone)

    @property
    def weather(self):
        return WeatherDataPoint().from_json(self.data["currently"])

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

        hourly_weather = WeatherDataPoint()
        hourly_weather.icon = daily["icon"]
        hourly_weather.summary = daily["summary"]
        hourly_weather.datetime = self.datetime

        hours = []
        for hour in daily["data"]:
            weather = WeatherDataPoint().from_json(hour)
            date = hour.get("time") or hour.get("datetime") or self.datetime
            time = self._stamp_to_datetime(date)
            hours.append(HourWeather(time, weather))

        return HourlyForecast(self.datetime, hours, hourly_weather)

    @property
    def hours(self):
        return self.hourly.hours

    @property
    def daily(self):
        daily = self.data["daily"]

        daily_weather = WeatherDataPoint()
        if daily.get("icon"):
            daily_weather.icon = daily["icon"]
            daily_weather.summary = daily["summary"]
        else:
            daily_weather.icon = daily["data"][0]["icon"]
            daily_weather.summary = daily["data"][0]["summary"]
        daily_weather.datetime = self.datetime

        days = []
        for day in daily["data"]:
            date = day.get("time") or day.get("datetime") or self.datetime
            time = self._stamp_to_datetime(date)
            weather = WeatherDataPoint().from_json(day)

            dayw = DayWeather(time, weather)
            if day.get("sunriseTime"):
                dayw.sunriseTime = self._stamp_to_datetime(
                    day["sunriseTime"], day.get("timezone"))
            if day.get("sunsetTime"):
                dayw.sunsetTime = self._stamp_to_datetime(
                    day["sunsetTime"], day.get("timezone"))

            dayw.moonPhase = day.get("moonPhase")

            for hour in self.hours:
                if hour.datetime.day == time.day:
                    dayw.hours[hour.datetime.hour] = hour

            days.append(dayw)

        return DailyForecast(self.datetime, days, daily_weather)

    @property
    def days(self):
        return self.daily.days

    def print(self):
        self.weather.print()

    def print_daily(self):
        #self.daily.print()
        for day in self.days:
            print(day.weekday, ":", day.datetime.date(), ":", day.summary)

    def print_hourly(self):
        #self.hourly.print()
        for hour in self.hours:
            print(hour.weekday, ":", hour.datetime.time(), ":", hour.summary)

    @staticmethod
    def _calc_day_average(hours):
        day = hours[0]
        day.precipIntensityMax = 0
        day.precipIntensityMin = day.precipIntensity
        for idx, d in enumerate(hours):
            if d.temperatureMin < day.temperatureMin:
                day.temperatureMin = d.temperatureMin
                day.temperatureMinTime = d.datetime
            if d.temperatureMax > day.temperatureMax:
                day.temperatureMax = d.temperatureMax
                day.temperatureMaxTime = d.datetime
            if d.temperatureLow < day.temperatureLow:
                day.temperatureLow = d.temperatureLow
                day.temperatureLowTime = d.datetime
            if d.temperatureHigh > day.temperatureHigh:
                day.temperatureHigh = d.temperatureHigh
                day.temperatureHighTime = d.datetime

            if d.precipIntensity and d.precipIntensity > \
                    day.precipIntensityMax:
                day.precipIntensityMax = d.precipIntensity
                day.precipIntensityMaxTime = d.datetime

            if not day.precipIntensityMin or d.precipIntensity and \
                    d.precipIntensity < day.precipIntensityMin:
                day.precipIntensityMin = d.precipIntensity

        # average hourly predictions
        day.temperature = day.temperatureMin + \
                          (day.temperatureMax - day.temperatureMin) / 2
        return day


    @staticmethod
    def _calc_hourly_summary(hours):
        hourly_summary = hours[0]["summary"]
        hourly_icon = hours[0]["icon"]
        return hourly_summary, hourly_icon

    @staticmethod
    def _calc_daily_summary(days):
        hourly_summary = days[0]["summary"]
        hourly_icon = days[0]["icon"]
        return hourly_summary, hourly_icon