from pyweather.location import geolocate
from pyweather import WeatherData
from pyweather.providers import WeatherProvider
from pendulum import now
from datetime import datetime


class WeatherUnlocked(WeatherProvider):
    default_app_id = "102297f7"
    default_key = "dcddedb2b86edf121cc5de355494ca6e"

    def __init__(self, lat, lon, key=None, app_id=None,
                 date=None, units="metric", lang="en"):
        if units in ["english", "imperial", "us"]:
            units = "f"
        elif units != "metric":
            units = "s"
        else:
            units = "m"
        super().__init__(lat, lon, date, units, lang)
        self.key = key or self.default_key
        self.app_id = app_id or self.default_app_id
        self._request()

    @staticmethod
    def from_address(address, key=None, app_id=None):
        key = key or WeatherUnlocked.default_key
        app_id = app_id or WeatherUnlocked.default_app_id
        lat, lon = geolocate(address)
        return WeatherUnlocked(lat, lon, key, app_id)

    def _request_current(self):
        current_url = "http://api.weatherunlocked.com/api/current/{lat},{lon}"
        params = {
            "app_key": self.key,
            "app_id": self.app_id
        }
        current_url = current_url.format(lat=self.latitude,
                                         lon=self.longitude)
        entry = self.session.get(current_url, params=params).json()

        if self.units == "f":
            temperature = entry.get("temp_f")
            visibility = entry.get("vis_mi")
            ap_temperature = entry.get("feelslike_f") or temperature
            wind_speed = entry.get("windspd_mph")
        else:
            temperature = entry.get("temp_c")
            visibility = entry.get("vis_km")
            ap_temperature = entry.get("feelslike_c") or temperature
            wind_speed = entry.get("windspd_kmh")

        wind_bearing = entry.get("winddir_deg")
        cloudCover = entry.get("cloudtotal_pct")
        humidity = entry.get("humid_pct")
        summary = entry.get("wx_desc")
        icon = entry.get("wx_icon")
        #
        # # {'alt_ft': 16.4,
        # #  'alt_m': 5.0,
        #  'cloudtotal_pct': 50.0,
        # #  'dewpoint_c': 11.98,
        # #  'dewpoint_f': 53.57,
        #  'feelslike_c': 15.7,
        #  'feelslike_f': 60.26,
        #  'humid_pct': 77.0,
        # #  'lat': 51.5,
        # #  'lon': 0.05,
        # #  'slp_in': 29.93,
        # #  'slp_mb': 1010.8,
        #  'temp_c': 16.0,
        #  'temp_f': 60.8,
        # #  'vis_desc': None,
        #  'vis_km': 10.0,
        #  'vis_mi': 6.21,
        # #  'winddir_compass': 'S',
        #  'winddir_deg': 180.0,
        # #  'windspd_kmh': 11.0,
        # #  'windspd_kts': 5.94,
        # #  'windspd_mph': 6.84,
        # #  'windspd_ms': 3.06,
        #  'wx_code': 1,
        #  'wx_desc': 'Partly cloudy',
        # #  'wx_icon': 'PartlyCloudyNight.gif'}

        temperature_min = temperature
        temperature_max = temperature

        # timezone = entry["location"]["timezone_id"]
        timezone = "UTC"
        ts = now(timezone).timestamp()
        lat = entry["lat"] or self.latitude
        lon = entry["lon"] or self.longitude

        w = {
            "time": ts,
            "timezone": timezone,
            "cloudCover": cloudCover,
            "visibility": visibility,
            "humidity": humidity,
            "temperature": temperature,
            "apparentTemperature": ap_temperature,
            "temperatureMin": temperature_min,
            "temperatureMax": temperature_max,
            "windSpeed": wind_speed,
            "windBearing": wind_bearing,
            "summary": summary,
            "icon": icon
        }

        hour = w
        hour["time"] = now(timezone).replace(minute=0, microsecond=0,
                                    second=0).timestamp()
        self.data["timezone"] = timezone
        self.data["latitude"] = lat
        self.data["longitude"] = lon
        self.data["currently"] = w
        self.data["daily"] = {"summary": w["summary"],
                              "icon": w["icon"],
                              "data": [w]}
        self.data["hourly"] = {"summary": w["summary"],
                               "icon": w["icon"],
                               "data": [hour]}

    def _request_forecast(self):

        forecast_url = "http://api.weatherunlocked.com/api/forecast/{lat},{lon}"
        params = {
            "app_key": self.key,
            "app_id": self.app_id
        }
        forecast_url = forecast_url.format(lat=self.latitude,
                                           lon=self.longitude)
        res = self.session.get(forecast_url, params=params).json()

        # daily readings
        hours = []
        _days = {}
        lat = self.latitude
        lon = self.longitude
        timezone = "UTC"

        for entry in res["Days"]:

            extra = entry.pop('Timeframes')[0]
            entry.update(extra)
            """
            {'cloud_high_pct': 0.0,
             'cloud_low_pct': 3.0,
             'cloud_mid_pct': 0.0,
                'cloudtotal_pct': 3.0,
                'date': '18/06/2020',
                 'dewpoint_c': 12.6,
                 'dewpoint_f': 54.7,
                 'feelslike_c': 15.6,
                 'feelslike_f': 60.0,
             'humid_max_pct': 81.0,
             'humid_min_pct': 54.0,
                 'humid_pct': 79.0,
                 'moonrise_time': '04:19',
                 'moonset_time': '18:30',
                 'precip_in': 0.0,
                'precip_mm': 0.0,
             'precip_total_in': 0.0,
             'precip_total_mm': 0.0,
             'prob_precip_pct': '<1',
             'rain_in': 0.0,
             'rain_mm': 0.0,
             'rain_total_in': 0.0,
             'rain_total_mm': 0.0,
             'slp_in': 30.15,
             'slp_max_in': 30.18,
             'slp_max_mb': 1019.1,
             'slp_mb': 1018.0,
             'slp_min_in': 30.09,
             'slp_min_mb': 1016.2,
             'snow_accum_cm': 0.0,
             'snow_accum_in': 0.0,
             'snow_in': 0.0,
             'snow_mm': 0.0,
             'snow_total_in': 0.0,
             'snow_total_mm': 0.0,
                 'sunrise_time': '06:11',
                 'sunset_time': '21:04',
                 'temp_c': 16.3,
                 'temp_f': 61.4,
                 'temp_max_c': 22.9,
                 'temp_max_f': 73.2,
                 'temp_min_c': 14.5,
                 'temp_min_f': 58.0,
                 'time': 0,
                 'utcdate': '18/06/2020',
                 'utctime': 0,
                 'vis_km': 10.0,
                 'vis_mi': 6.2,
             'winddir_compass': 'NNW',
                'winddir_deg': 339.0,
                 'windgst_kmh': 23.0,
                 'windgst_kts': 12.0,
             'windgst_max_kmh': 38.0,
             'windgst_max_kts': 21.0,
             'windgst_max_mph': 24.0,
             'windgst_max_ms': 10.6,
                 'windgst_mph': 14.0,
                 'windgst_ms': 6.4,
                 'windspd_kmh': 17.0,
                 'windspd_kts': 9.0,
             'windspd_max_kmh': 28.0,
             'windspd_max_kts': 15.0,
             'windspd_max_mph': 17.0,
             'windspd_max_ms': 7.8,
                 'windspd_mph': 11.0,
                 'windspd_ms': 4.7,
             'wx_code': 0,
                'wx_desc': 'Clear skies',
                'wx_icon': 'Clear.gif'}
             """
            summary =  entry.get("wx_desc")
            icon = entry.get("wx_icon")
            sunriseTime = entry.get("sunrise_time")
            sunsetTime = entry.get("sunset_time")
            moonriseTime = entry.get("moonrise_time")
            moonsetTime = entry.get("moonset_time")

            if self.units == "f":
                temperature_min = entry.get("temp_min_f")
                temperature_max = entry.get("temp_max_f")
                temperature = entry.get("temp_f")
                ap_temperature = entry.get("feelslike_f")
                wind_speed = entry.get("windspd_mph")
                wind_gust = entry.get("windgst_mph")
                visibility = entry.get("vis_mi")
                precipIntensity = entry.get("precip_in")
                dew = entry.get("dewpoint_f")
            else:
                temperature_min = entry.get("temp_min_c")
                temperature_max = entry.get("temp_max_c")
                temperature = entry.get("temp_c")
                wind_speed = entry.get("windspd_kmh")
                wind_gust = entry.get("windgst_kmh")
                visibility = entry.get("vis_km")
                ap_temperature = entry.get("feelslike_c")
                precipIntensity = entry.get("precip_mm")
                dew = entry.get("dewpoint_c")

            precipProbability = entry.get("prob_precip_pct")
            wind_bearing = entry.get("winddir_deg")
            humidity = entry.get("humid_pct")
            cloudCover = entry.get("cloudtotal_pct")

            date = datetime.strptime(entry["utcdate"], "%d/%m/%Y")
            ts = date.timestamp()
            w = {
                "time": ts,
                "SunriseTime": sunriseTime,
                "SunsetTime": sunsetTime,
                'precipProbability': precipProbability,
                "timezone": timezone,
                "dewPoint": dew,
               # "pressure": pressure,
                "cloudCover": cloudCover,
                "visibility": visibility,
                "humidity": humidity,
                "temperature": temperature,
                "apparentTemperature": ap_temperature,
                "temperatureMin": temperature_min,
                "temperatureMax": temperature_max,
                "windSpeed": wind_speed,
                "windGust": wind_gust,
                "windBearing": wind_bearing,
                "summary": summary,
                "icon": icon,
                "precipIntensity": precipIntensity
            }
            hours.append(w)
            w = WeatherData().from_dict(w)

            if w.datetime.day not in _days:
                _days[w.datetime.day] = []
            _days[w.datetime.day] += [w]

        # TODO
        hourly_summary, hourly_icon = self._calc_hourly_summary(hours)
        self.data["timezone"] = timezone
        self.data["latitude"] = lat
        self.data["longitude"] = lon

        self.data["hourly"] = {"summary": hourly_summary,
                               "icon": hourly_icon,
                               "data": hours}
        days = []
        for d in _days:
            day = self._calc_day_average(_days[d])
            day = day.as_dict()
            days += [day]

        daily_summary, daily_icon = self._calc_daily_summary(days)
        self.data["daily"] = {"summary": daily_summary,
                              "icon": daily_icon,
                              "data": days}

    def _request(self):
        self._request_current()
        self._request_forecast()



if __name__ == "__main__":
    from pprint import pprint
    date = now()
    print(date)

    #d = WeatherUnlocked.from_address("Lisbon")
    lat, lon = 38.7222563442538, -9.1393314973889
    d = WeatherUnlocked(lat, lon)

    print("##### CURRENT WEATHER ######")
    d.print()

    print("\n##### DAILY FORECAST ######")
    d.print_daily()

    for forecast in d.daily:
        data = forecast.as_dict()
        data.pop("hours")
        pprint(data)
        exit()