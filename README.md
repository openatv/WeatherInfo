###############################################################################################################
#                                                                                                             #
#  Weatherinfo for openTV is a multiplatform tool (runs on Enigma2 & Windows and probably many others)        #
#  Coded by Mr.Servo @ openATV and jbleyel @ openATV (c) 2022                                                 #
#  Purpose: get weather forecasts from msnWeather (MSN) and/or OpenWeatherMap (OWM)                           #
#  Output : DICT (MSN & OWM), JSON-file (MSN & OWM), XML-string (MSN only), XML-file (MSN only)               #
#  Learn more about the tool by running it in the shell: "python Weatherinfo.py -h"                           #
#  ---------------------------------------------------------------------------------------------------------  #
#  This plugin is licensed under the GNU version 3.0 <https://www.gnu.org/licenses/gpl-3.0.en.html>.          #
#  This plugin is NOT free software. It is open source, you are allowed to modify it (if you keep             #
#  the license), but it may not be commercially distributed. Advertise with this tool is not allowed.         #
#  For other uses, permission from the authors is necessary.                                                  #
#  ---------------------------------------------------------------------------------------------------------  #
#  definitions with example:                                                                                  #
#  mode = "owm"                                # string: operation mode "msn" or "owm" ("msn" is default)     #
#  units = "imperial"                          # string: units ("metric" or "imperial" ("metric is defualt)   #
#  scheme = "en-us"                            # string: local language scheme (default is "de-de")           #
#  reduced = True                              # reduced dataset for a simple forecast (e.g. Metrix-Weather)  #
#  cityID = 2950159 or "2950159"               # integer or string: owm's DEPRECATED cityID (2950159=Berlin)  #
#  cityname = "Berlin{, DE}"                   # string: realname of city (with optional country code)        #
#  geocode = "13.4105,52.5244"                 # string: consisting of "longitude,latitude"                   #
#  geodata = ("Berlin, DE", 13.4105,52.5244)   # tuple: consisting of cityname and its "geocode"              #
#  geolist = ["city1",lon,lat),("city2",...)]  # list: of tuples "geodata" (e.g. search results)              #
#  ---------------------------------------------------------------------------------------------------------  #
#  usage for MSN only:                                                                                        #
#  WI = WeatherInfo(mode="msn")                # initialization for "msn" (no API-key required)               #
#  msnxmlData = WI.getmsnxml()                 # get XML-string (similar to old msnWeather API-server)        #
#  msnxmlData = WI.writemsnxml()               # get XML-string & write as file                               #
#  ---------------------------------------------------------------------------------------------------------  #
#  usage for OWM only:                                                                                        #
#  WI = WeatherInfo(mode="owm", apikey="my_apikey")       # initialization for "owm" (API-key required)       #
#  geolist = WI.getCitylistbyGeocode(geocode, scheme)     # get search results (max. 5) from geocode          #
#  geodata = WI.getCitybyID(2950159)                      # get geodata from owm's cityID (2950159=Berlin)    #
#  WI.start(geodata=None, cityID=cityID, units, scheme, reduced=True, callback=MyCallback)     # by cityID    #
#  ---------------------------------------------------------------------------------------------------------  #
#  common usage for MSN and OWM:                                                                              #
#  geolist = WI.getCitylist(cityname, scheme)             # get search results (max. 9) from cityname         #
#  WI.start(geodata=geodata, cityID=None, units, scheme, reduced=True, callback=MyCallback)    # by geodata   #
#  WI.setmode(newmode, apikey)         # change mode if desired (is already part of the initialization)       #
#  DICT = WI.getinfo()                 # alternatively: DICT = WI.info                                        #
#  WI.writejson(filename)              # writes full DICT as full JSON-string as file                         #
#  DICT = WI.getreducedinfo()          # get reduced DICT                                                     #
#  WI.writereducedjson(filename)       # get reduced DICT & write reduced JSON-string as file                 #
#  WI.error                            # returns None when everything is OK otherwise a detailed error msg    #
#  ---------------------------------------------------------------------------------------------------------  #
#  Interactive call is also possible by setting WI.start(..., callback=None) # example: see 'def main(argv)'  #
#                                                                                                             #
###############################################################################################################
