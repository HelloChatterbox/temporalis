# [Temporalis](https://en.wiktionary.org/wiki/temporalis#Adjective)

"there's a lot of weather"

## install

```bash
pip install temporalis
```

## Usage

```python
from temporalis.providers.owm import OWM

lat, lon = 38.7222563442538, -9.1393314973889
forecast = OWM(lat, lon)
# forecast = OWM.from_address("something to geolocate")

# pretty print basic forecast info
print("##### CURRENT WEATHER ######")
forecast.print()

print("\n##### DAILY FORECAST ######")
forecast.print_daily()

print("\n##### HOURLY FORECAST ######")
forecast.print_hourly()

# check sun data
print("\n##### ABOUT THE SUN ######")
print("Dusk", forecast.dusk)
print("Dawn", forecast.dawn)
print("Sunset", forecast.sunset)
print("Sunrise", forecast.sunrise)

# check moon data
print("\n##### ABOUT THE MOON ######")
print("Moon:", forecast.moon_symbol, forecast.moon_phase_name)
print("Moon phase", forecast.moon_phase)

# work with raw data
print("\n##### RAW DATA ######")
pprint(forecast.data)

```