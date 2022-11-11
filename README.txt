Weatherinfo for openTV is a multiplatform tool (runs on Enigma2 & Windows and probably many others)
Coded by Mr.Servo @ openATV and jbleyel @ openATV (c) 2022
Purpose: get weather forecasts from msnWeather (MSN), Open-Meteo Weather (OMW) and OpenWeatherMap (OWM)
Output : DICT (MSN, OMW & OWM), JSON-file (MSN, OMW & OWM), XML-string (MSN only), XML-file (MSN only)
---------------------------------------------------------------------------------------------------------
This plugin is licensed under the GNU version 3.0 <https://www.gnu.org/licenses/gpl-3.0.en.html>.
This plugin is NOT free software. It is open source, you are allowed to modify it (if you keep
the license), but it may not be commercially distributed. Advertise with this tool is not allowed.
For other uses, permission from the authors is necessary.
---------------------------------------------------------------------------------------------------------
Learn more about the tool by running it in the shell: "python Weatherinfo.py -h"
Usage: Weatherinfo [options...] <cityname>
-m, --mode <data>               Valid modes: 'omw', 'owm' or 'msn' {'msn' is default}
-a, --apikey <data>             API-key required for 'owm' only
-j, --json <filename>           File output formatted in JSON (all modes)
-r, --reduced <filename>        File output formatted in JSON (minimum infos only)
-x, --xml <filename>            File output formatted in XML (mode 'msn' only)
-s, --scheme <data>             Country scheme (not used by 'omw') {'de-de' is default}
-u, --units <data>              Valid units: 'imperial' or 'metric' {'metric' is default}
-i, --id <cityID>               Get cityname by owm's DEPRECATED cityID ('owm' only)
-g, --geocode <lon/lat>         Get cityname by 'longitude,latitude' ('owm' only)
-c, --control                   Show iconcode-plaintexts and conversion rules
-q, --quiet                     Perform without text output and select first found city
---------------------------------------------------------------------------------------------------------
definitions with example:
mode = "omw"                                # string: operation mode ("msn" is default)
units = "imperial"                          # string: units "metric" or "imperial" ("metric" is default)
scheme = "en-us"                            # string: language scheme (not for "omw", default is "de-de")
reduced = True                              # reduced dataset for a simple forecast (e.g. Metrix-Weather)
cityID = 2950159 or "2950159"               # integer or string: owm's DEPRECATED cityID (2950159=Berlin)
cityname = "Berlin{, DE}"                   # string: realname of city (with optional country code)
geocode = "13.4105,52.5244"                 # string: consisting of "longitude,latitude"
geodata = ("Berlin, DE", 13.4105,52.5244)   # tuple: consisting of cityname and its "geocode"
geolist = ["city1",lon,lat),("city2",...)]  # list: of tuples "geodata" (e.g. search results)
---------------------------------------------------------------------------------------------------------
usage for MSN only:
WI = WeatherInfo(mode="msn")                # initialization for "msn" (no API-key required)
msnxmlData = WI.getmsnxml()                 # get XML-string (similar to old msnWeather API-server)
msnxmlData = WI.writemsnxml()               # get XML-string & write as file
---------------------------------------------------------------------------------------------------------
usage for OMW only:
WI = WeatherInfo(mode="omw")                           # initialization for "omw" (no API-key required)
WI.start(geodata=geodata, cityID=None, units, scheme, reduced=True, callback=MyCallback)    # by geodata
---------------------------------------------------------------------------------------------------------
usage for OWM only:
WI = WeatherInfo(mode="owm", apikey="my_apikey")       # initialization for "owm" (API-key required)
geodata = WI.getCitybyID(2950159)                      # get geodata from owm's DEPRECATED cityID
WI.start(geodata=None, cityID=cityID, units, scheme, reduced=True, callback=MyCallback)     # by cityID
---------------------------------------------------------------------------------------------------------
common usage for all:
geolist = WI.getCitylist(cityname, scheme)             # get search results (max. 10) from cityname
WI.setmode(newmode, apikey)         # change mode if desired (is already part of the initialization)
WI.stop()                           # remove callback and let thread run out
DICT = WI.getinfo()                 # alternatively: DICT = WI.info
WI.writejson(filename)              # writes full DICT as full JSON-string as file
DICT = WI.getreducedinfo()          # get reduced DICT
WI.writereducedjson(filename)       # get reduced DICT & write reduced JSON-string as file
WI.error                            # returns None when everything is OK otherwise a detailed error msg
WI.SOURCES = ["msn", "owm", "omw"]  # supported sourcecodes (the order must not be changed)
WI.DESTINATIONS = ["yahoo", "meteo"]  # supported iconcodes (the order must not be changed)
---------------------------------------------------------------------------------------------------------
Interactive call is also possible by setting WI.start(..., callback=None) # example: see "def main(argv)"
