import pendulum
from astral import LocationInfo
from astral.sun import sun
from temporalis.location import get_timezone
from temporalis.time import now_utc


def get_sun_times(lat, lon, date=None):
    date = date or now_utc()
    tz = get_timezone(lat, lon)
    city = LocationInfo("Some city", "Some location",
                        tz, lat, lon)
    s = sun(city.observer, date=date)
    # inject timezone data
    tz = pendulum.timezone(tz)
    for k in s:
        s[k] = tz.datetime(s[k].year, s[k].month, s[k].day,
                           s[k].hour, s[k].minute, s[k].second)
    return s


def get_dawn(lat, lon, date=None):
    return get_sun_times(lat, lon, date)["dawn"]


def get_sunrise(lat, lon, date=None):
    return get_sun_times(lat, lon, date)["sunrise"]


def get_noon(lat, lon, date=None):
    return get_sun_times(lat, lon, date)["noon"]


def get_sunset(lat, lon, date=None):
    return get_sun_times(lat, lon, date)["sunset"]


def get_dusk(lat, lon, date=None):
    return get_sun_times(lat, lon, date)["dusk"]
