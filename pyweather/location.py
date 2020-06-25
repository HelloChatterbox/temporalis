from geopy.geocoders import Yandex, Nominatim
import geocoder
from timezonefinder import TimezoneFinder
from datetime import timedelta
import pytz
from astral.geocoder import database, lookup


def geolocate(address, try_all=True):
    try:
        # see https://astral.readthedocs.io/en/latest/#cities
        a = lookup(address, database())
        return a.latitude, a.longitude
    except:
        pass  # use online geocoder

    location_data = geocoder.geonames(address, method='details', key='jarbas')
    if not location_data.ok:
        location_data = geocoder.geocodefarm(address)
    if not location_data.ok:
        location_data = geocoder.osm(address)
    if try_all:
        # more are just making it slow
        if not location_data.ok:
            location_data = geocoder.google(address)
        if not location_data.ok:
            location_data = geocoder.arcgis(address)
        if not location_data.ok:
            location_data = geocoder.bing(address)
        if not location_data.ok:
            location_data = geocoder.canadapost(address)
        if not location_data.ok:
            location_data = geocoder.yandex(address)
        if not location_data.ok:
            location_data = geocoder.tgos(address)

    if location_data.ok:
        location_data = location_data.json
        lat = location_data.get("lat")
        lon = location_data.get("lng")

        return lat, lon
    raise ValueError


def reverse_geolocate(lat, lon):
    geolocator = Nominatim()
    location = geolocator.reverse(str(lat) + ", " + str(lon), timeout=10)
    if location is None:
        geolocator = Yandex(lang='en_US')
        location = geolocator.reverse(str(lat) + ", " + str(lon), timeout=10)
        if location is None or not len(location):
            return {}
        location = location[0]

    return location.__dict__


def get_timezone(latitude, longitude):
    return TimezoneFinder().timezone_at(lng=longitude, lat=latitude)


def possible_timezones(tz_offset, common_only=True):
    # pick one of the timezone collections
    timezones = pytz.common_timezones if common_only else pytz.all_timezones

    # convert the float hours offset to a timedelta
    offset_days, offset_seconds = 0, int(tz_offset * 3600)
    if offset_seconds < 0:
        offset_days = -1
        offset_seconds += 24 * 3600
    desired_delta = timedelta(offset_days, offset_seconds)

    # Loop through the timezones and find any with matching offsets
    null_delta = timedelta(0, 0)
    results = []
    for tz_name in timezones:
        tz = pytz.timezone(tz_name)
        non_dst_offset = getattr(tz, '_transition_info', [[null_delta]])[-1]
        if desired_delta == non_dst_offset[0]:
            results.append(tz_name)

    return results

