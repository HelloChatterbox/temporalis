import pendulum
from astral import LocationInfo
from astral.sun import sun
from pyweather.location import get_timezone
from pyweather.time import now_utc


def get_dawn(lat, lon, date=None):
    date = date or now_utc()
    tz = get_timezone(lat, lon)
    city = LocationInfo("Some city", "Some location",
                        tz, lat, lon)
    s = sun(city.observer, date=date)
    dt = s["dawn"]
    tz = pendulum.timezone(tz)
    dt = tz.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return dt


def get_sunrise(lat, lon, date=None):
    date = date or now_utc()
    tz = get_timezone(lat, lon)
    city = LocationInfo("Some city", "Some location",
                        tz, lat, lon)
    s = sun(city.observer, date=date)
    dt = s["sunrise"]
    tz = pendulum.timezone(tz)
    dt = tz.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return dt


def get_noon(lat, lon, date=None):
    date = date or now_utc()
    tz = get_timezone(lat, lon)
    city = LocationInfo("Some city", "Some location",
                        tz, lat, lon)
    s = sun(city.observer, date=date)
    dt = s["noon"]
    tz = pendulum.timezone(tz)
    dt = tz.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return dt


def get_sunset(lat, lon, date=None):
    date = date or now_utc()
    tz = get_timezone(lat, lon)
    city = LocationInfo("Some city", "Some location",
                        tz, lat, lon)
    s = sun(city.observer, date=date)
    dt = s["sunset"]
    tz = pendulum.timezone(tz)
    dt = tz.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return dt


def get_dusk(lat, lon, date=None):
    date = date or now_utc()
    tz = get_timezone(lat, lon)
    city = LocationInfo("Some city", "Some location",
                        tz, lat, lon)
    s = sun(city.observer, date=date)
    dt = s["dusk"]
    tz = pendulum.timezone(tz)
    dt = tz.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
    return dt

