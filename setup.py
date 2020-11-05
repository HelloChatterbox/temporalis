from setuptools import setup

setup(
    name='pyweather',
    version='0.1',
    packages=['pyweather', 'pyweather.providers'],
    url='https://github.com/HelloChatterbox/pyweather',
    license='Apache2',
    author='jarbasAi',
    install_requires=["requests",
                      "timezonefinder",
                      "geopy",
                      "geocoder",
                      "pendulum",
                      "python-dateutil",
                      "pytz",
                      "requests-cache",
                      "astral"],
    author_email='jarbasai@mailfence.com',
    description='unified weather service apis'
)
