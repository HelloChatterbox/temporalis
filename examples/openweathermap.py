from pyweather.providers.owm import OWM
from pprint import pprint


lat, lon = 38.7222563442538, -9.1393314973889
forecast = OWM(lat, lon)
# or d = OWM.from_address("something to geolocate")

# pretty print basic forecast info
print("##### CURRENT WEATHER ######")
forecast.print()

print("\n##### DAILY FORECAST ######")
forecast.print_daily()

print("\n##### HOURLY FORECAST ######")
forecast.print_hourly()

# check sun data
print("Dusk", forecast.dusk)
print("Dawn", forecast.dawn)
print("Sunset", forecast.sunset)
print("Sunrise", forecast.sunrise)

# check moon data
print("Moon:", forecast.moon_symbol, forecast.moon_phase_name)
print("Moon phase", forecast.moon_phase)

# work with raw data
pprint(forecast.data)

# inspect current weather
pprint(forecast.hourly[0].as_dict())

# inspect tomorrow weather
pprint(forecast.daily[1].as_dict())


