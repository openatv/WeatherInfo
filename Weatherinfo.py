#########################################################################################################
#                                                                                                       #
#  Weatherinfo for openATV is a multiplatform tool (runs on Enigma2 & Windows and probably many others) #
#  Coded by Mr.Servo @ openATV and jbleyel @ openATV (c) 2022                                           #
#  Learn more about the tool by running it in the shell: "python Weatherinfo.py -h"                     #
#  -----------------------------------------------------------------------------------------------------#
#  This plugin is licensed under the GNU version 3.0 <https://www.gnu.org/licenses/gpl-3.0.en.html>.    #
#  This plugin is NOT free software. It is open source, you are allowed to modify it (if you keep       #
#  the license), but it may not be commercially distributed. Advertise with this tool is not allowed.   #
#  For other uses, permission from the authors is necessary.                                            #
#                                                                                                       #
#########################################################################################################

from sys import exit, argv
from json import dump, loads
from datetime import datetime, timedelta, timezone
from requests import get, exceptions
from getopt import getopt, GetoptError
from random import choice
from twisted.internet.reactor import callInThread

MODULE_NAME = __name__.split(".")[-1]
SOURCES = ["msn", "omw", "owm"]  # supported sourcecodes (the order must not be changed)
DESTINATIONS = ["yahoo", "meteo"]  # supported iconcodes (the order must not be changed)


class Weatherinfo:
	def __init__(self, newmode="msn", apikey=None):

		self.msnCodes = {
						 "d000": ("32", "B"), "d100": ("34", "B"), "d200": ("30", "H"), "d210": ("12", "Q"),
						 "d211": ("5", "W"), "d212": ("14", "V"), "d220": ("11", "Q"), "d221": ("42", "V"),
						 "d222": ("16", "W"), "d240": ("4", "0"), "d300": ("28", "H"), "d310": ("11", "Q"),
						 "d311": ("5", "W"), "d312": ("14", "V"), "d320": ("39", "R"), "d321": ("5", "W"),
						 "d322": ("16", "W"), "d340": ("4", "0"), "d400": ("26", "Y"), "d410": ("9", "Q"),
						 "d411": ("5", "W"), "d412": ("14", "V"), "d420": ("9", "Q"), "d421": ("5", "W"),
						 "d422": ("16", "W"), "d430": ("12", "Q"), "d431": ("5", "W"), "d432": ("15", "W"),
						 "d440": ("4", "0"), "d500": ("28", "H"), "d600": ("20", "E"), "d603": ("10", "U"),
						 "d605": ("17", "X"), "d705": ("17", "X"), "d900": ("21", "M"), "d905": ("17", "X"),
						 "d907": ("21", "M"),
						 "n000": ("31", "C"), "n100": ("33", "C"), "n200": ("29", "I"), "n210": ("45", "Q"),
						 "n211": ("5", "W"), "n212": ("46", "W"), "n220": ("45", "Q"), "n221": ("5", "W"),
						 "n222": ("46", "W"), "n240": ("47", "Z"), "n300": ("27", "I"), "n310": ("45", "Q"),
						 "n311": ("11", "Q"), "n312": ("46", "W"), "n320": ("45", "R"), "n321": ("5", "W"),
						 "n322": ("46", "W"), "n340": ("47", "Z"), "n400": ("26", "Y"), "n410": ("9", "Q"),
						 "n411": ("5", "W"), "n412": ("14", "V"), "n420": ("9", "Q"), "n421": ("5", "W"),
						 "n422": ("14", "W"), "n430": ("12", "Q"), "n431": ("5", "W"), "n432": ("15", "W"),
						 "n440": ("4", "0"), "n500": ("29", "I"), "n600": ("20", "E"), "n603": ("10", "U"),
						 "n605": ("17", "X"), "n705": ("17", "X"), "n900": ("21", "M"), "n905": ("17", "X"),
						 "n907": ("21", "M")  # "xxxx1": "WindyV2"
						 }  # mapping: msn -> (yahoo, meteo)
		self.omwCodes = {
						 "0": ("32", "B"), "1": ("34", "B"), "2": ("30", "H"), "3": ("28", "N"), "45": ("20", "M"),
						 "48": ("21", "J"), "51": ("9", "Q"), "53": ("9", "Q"), "55": ("9", "R"), "56": ("8", "V"),
						 "57": ("10", "U"), "61": ("11", "Q"), "63": ("12", "R"), "65": ("12", "R"), "66": ("8", "R"),
						 "67": ("7", "W"), "71": ("42", "V"), "73": ("14", "U"), "75": ("41", "W"), "77": ("35", "X"),
						 "80": ("11", "Q"), "81": ("12", "R"), "82": ("12", "R"), "85": ("42", "V"), "86": ("43", "W"),
						 "95": ("38", "P"), "96": ("4", "O"), "99": ("4", "Z")
						}  # mapping: omw -> (yahoo, meteo)
		self.owmCodes = {
						 "200": ("37", "O"), "201": ("4", "O"), "202": ("3", "P"), "210": ("37", "O"), "211": ("4", "O"),
						 "212": ("3", "P"), "221": ("3", "O"), "230": ("37", "O"), "231": ("38", "O"), "232": ("38", "O"),
						 "300": ("9", "Q"), "301": ("9", "Q"), "302": ("9", "Q"), "310": ("9", "Q"), "311": ("9", "Q"),
						 "312": ("9", "R"), "313": ("11", "R"), "314": ("12", "R"), "321": ("11", "R"), "500": ("9", "Q"),
						 "501": ("11", "Q"), "502": ("11", "R"), "503": ("12", "R"), "504": ("12", "R"), "511": ("10", "W"),
						 "520": ("11", "Q"), "521": ("11", "R"), "522": ("12", "R"), "531": ("40", "Q"), "600": ("42", "U"),
						 "601": ("16", "V"), "602": ("15", "V"), "611": ("18", "X"), "612": ("10", "W"), "613": ("17", "X"),
						 "615": ("6", "W"), "616": ("5", "W"), "620": ("14", "U"), "621": ("42", "U"), "622": ("13", "V"),
						 "701": ("20", "M"), "711": ("22", "J"), "721": ("21", "E"), "731": ("19", "J"), "741": ("20", "E"),
						 "751": ("19", "J"), "761": ("19", "J"), "762": ("22", "J"), "771": ("23", "F"), "781": ("0", "F"),
						 "800": ("32", "B"), "801": ("34", "B"), "802": ("30", "H"), "803": ("26", "H"), "804": ("28", "N")
						 }  # mapping: owm -> (yahoo, meteo), OpenWeatherMap is DEPRECATED
		self.msnDescs = {
						 "d000": "SunnyDayV3", "d100": "MostlySunnyDay", "d200": "D200PartlySunnyV2", "d210": "D210LightRainShowersV2",
						 "d211": "D211LightRainSowShowersV2", "d212": "D212LightSnowShowersV2", "d220": "LightRainShowerDay",
						 "d221": "D221RainSnowShowersV2", "d222": "SnowShowersDayV2", "d240": "D240TstormsV2",
						 "d300": "MostlyCloudyDayV2", "d310": "D310LightRainShowersV2", "d311": "D311LightRainSnowShowersV2",
						 "d312": "LightSnowShowersDay", "d320": "RainShowersDayV2", "d321": "D321RainSnowShowersV2",
						 "d322": "SnowShowersDayV2", "d340": "D340TstormsV2", "d400": "CloudyV3", "d410": "LightRainV3",
						 "d411": "RainSnowV2", "d412": "LightSnowV2", "d420": "HeavyDrizzle", "d421": "RainSnowV2", "d422": "Snow",
						 "d430": "ModerateRainV2", "d431": "RainSnowV2", "d432": "HeavySnowV2", "d440": "ThunderstormsV2",
						 "d500": "MostlyCloudyDayV2", "d600": "FogV2", "d603": "FreezingRainV2", "d605": "IcePelletsV2",
						 "d705": "BlowingHailV2", "d900": "Haze", "d905": "BlowingHailV2", "d907": "Haze",
						 "n000": "ClearNightV3", "n100": "MostlyClearNight", "n200": "PartlyCloudyNightV2",
						 "n210": "N210LightRainShowersV2", "n211": "N211LightRainSnowShowersV2", "n212": "N212LightSnowShowersV2",
						 "n220": "LightRainShowerNight", "n221": "N221RainSnowShowersV2", "n222": "N222SnowShowersV2",
						 "n240": "N240TstormsV2", "n300": "MostlyCloudyNightV2", "n310": "N310LightRainShowersV2",
						 "n311": "N311LightRainSnowShowersV2", "n312": "LightSnowShowersNight", "n320": "RainShowersNightV2",
						 "n321": "N321RainSnowShowersV2", "n322": "N322SnowShowersV2", "n340": "N340TstormsV2", "n400": "CloudyV3",
						 "n410": "LightRainV3", "n411": "RainSnowV2", "n412": "LightSnowV2", "n420": "HeavyDrizzle",
						 "n421": "RainSnowShowersNightV2", "n422": "N422SnowV2", "n430": "ModerateRainV2",
						 "n431": "RainSnowV2", "n432": "HeavySnowV2", "n440": "ThunderstormsV2", "n500": "PartlyCloudyNightV2",
						 "n600": "FogV2", "n603": "FreezingRainV2", "n605": "BlowingHailV2", "n705": "BlowingHailV2",
						 "n905": "BlowingHailV2", "n907": "Haze", "n900": "Haze"  # "xxxx1": "WindyV2"
						 }  # cleartext description of msn-weathercodes
		self.omwDescs = {
						 "0": "clear sky", "1": "mainly clear", "2": "partly cloudy", "3": "overcast", "45": "fog", "48": "depositing rime fog", "51": "light drizzle",
						 "53": "moderate drizzle", "55": "dense intensity drizzle", "56": "light freezing drizzle", "57": "dense intensity freezing drizzle",
						 "61": "slight rain", "63": "moderate rain", "65": "heavy intensity rain", "66": "light freezing rain", "67": "heavy intensity freezing rain",
						 "71": "slight snow fall", "73": "moderate snow fall", "75": "heavy intensity snow fall", "77": "snow grains", "80": "slight rain showers",
						 "81": "moderate rain showers", "82": "violent rain showers", "85": "slight snow showers", "86": "heavy snow showers",
						 "95": "slight or moderate thunderstorm", "96": "thunderstorm with slight hail", "99": "thunderstorm with heavy hail"
						 }  # cleartext description of omw-weathercodes
		self.owmDescs = {
						 "200": "thunderstorm with light rain", "201": "thunderstorm with rain", "202": "thunderstorm with heavy rain",
						 "210": "light thunderstorm", "211": "thunderstorm", "212": "heavy thunderstorm", "221": "ragged thunderstorm",
						 "230": "thunderstorm with light drizzle", "231": "thunderstorm with drizzle", "232": "thunderstorm with heavy drizzle",
						 "300": "light intensity drizzle", "301": "drizzle", "302": "heavy intensity drizzle", "310": "light intensity drizzle rain",
						 "311": "drizzle rain", "312": "heavy intensity drizzle rain", "313": "shower rain and drizzle", "314": "heavy shower rain and drizzle",
						 "321": "shower drizzle", "500": "light rain", "501": "moderate rain", "502": "heavy intensity rain", "503": "very heavy rain",
						 "504": "extreme rain", "511": "freezing rain", "520": "light intensity shower rain", "521": "shower rain", "522": "heavy intensity shower rain",
						 "531": "ragged shower rain", "600": "light snow", "601": "Snow", "602": "Heavy snow", "611": "Sleet", "612": "Light shower sleet",
						 "613": "Shower sleet", "615": "Light rain and snow", "616": "Rain and snow", "620": "Light shower snow", "621": "Shower snow",
						 "622": "Heavy shower snow", "701": "mist", "711": "Smoke", "721": "Haze", "731": "sand/ dust whirls", "741": "fog", "751": "sand",
						 "761": "dust", "762": "volcanic ash", "771": "squalls", "781": "tornado", "800": "clear sky", "801": "few clouds: 11-25%",
						 "802": "scattered clouds: 25-50%", "803": "broken clouds: 51-84%", "804": "overcast clouds: 85-100%"
						 }  # cleartext description of owm-weathercodes, OpenWeatherMap is DEPRECATED
		self.yahooDescs = {
						 "0": "tornado", "1": "tropical storm", "2": "hurricane", "3": "severe thunderstorms", "4": "thunderstorms", "5": "mixed rain and snow",
						 "6": "mixed rain and sleet", "7": "mixed snow and sleet", "8": "freezing drizzle", "9": "drizzle", "10": "freezing rain",
						 "11": "showers (light)", "12": "showers (heavier)", "13": "snow flurries", "14": "light snow showers", "15": "blowing snow", "16": "snow",
						 "17": "hail", "18": "sleet", "19": "dust", "20": "foggy", "21": "haze", "22": "smoky", "23": "blustery", "24": "windy", "25": "cold",
						 "26": "cloudy", "27": "mostly cloudy (night)", "28": "mostly cloudy (day)", "29": "partly cloudy (night)", "30": "partly cloudy (day)",
						 "31": "clear (night)", "32": "sunny (day)", "33": "fair (night)", "34": "fair (day)", "35": "mixed rain and hail", "36": "hot",
						 "37": "isolated thunderstorms", "38": "scattered thunderstorms", "39": "capricious weather", "40": "scattered showers",
						 "41": "heavy snow", "42": "scattered snow showers", "43": "heavy snow", "44": "partly cloudy", "45": "rain showers (night)",
						 "46": "snow showers (night)", "47": "thundershowers (night)", "NA": "not available"
						 }  # cleartext description of modified yahoo-iconcodes
		self.meteoDescs = {
						 "!": "windy_rain_inv", "\"": "snow_inv", "#": "snow_heavy_inv", "$": "hail_inv", "%": "clouds_inv", "&": "clouds_flash_inv", "'": "temperature",
						 "(": "compass", ")": "na", "*": "celcius", "+": "fahrenheit", "0": "clouds_flash_alt", "1": "sun_inv", "2": "moon_inv", "3": "cloud_sun_inv",
						 "4": "cloud_moon_inv", "5": "cloud_inv", "6": "cloud_flash_inv", "7": "drizzle_inv", "8": "rain_inv", "9": "windy_inv", "A": "sunrise",
						 "B": "sun", "C": "moon", "D": "eclipse", "E": "mist", "F": "wind", "G": "snowflake", "H": "cloud_sun", "I": "cloud_moon", "J": "fog_sun",
						 "K": "fog_moon", "L": "fog_cloud", "M": "fog", "N": "cloud", "O": "cloud_flash", "P": "cloud_flash_alt", "Q": "drizzle", "R": "rain",
						 "S": "windy", "T": "windy_rain", "U": "snow", "V": "snow_alt", "W": "snow_heavy", "X": "hail", "Y": "clouds", "Z": "clouds_flash"
						 }  # cleartext description of modified meteo-iconcodes
		agents = [
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
				"Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Mobile/15E148 Safari/604.1",
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0",
				"Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36 Edg/87.0.664.75",
				"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363"
				]
		self.headers = {"User-Agent": choice(agents), 'Accept': 'application/json'}
		self.error = None
		self.info = None
		self.mode = None
		self.parser = None
		self.geodata = None
		self.units = None
		self.callback = None
		self.reduced = False
		self.dataReady = False
		self.setmode(newmode, apikey)

	def setmode(self, newmode="msn", apikey=None):
		self.error = None
		self.apikey = apikey
		newmode = newmode.lower()
		if newmode in SOURCES:
			if self.mode != newmode:
				self.mode = newmode
				if newmode == "msn":
					self.parser = self.msnparser
				elif newmode == "omw":
					self.parser = self.omwparser
				elif newmode == "owm":
					if apikey:
						self.parser = self.owmparser
					else:
						self.error = "[%s] ERROR in module 'setmode': API-Key for mode '%s' is missing!" % (MODULE_NAME, newmode)
						self.parser = None
						return self.error
		else:
			self.error = "[%s] ERROR in module 'setmode': unknown mode '%s'" % (MODULE_NAME, newmode)
			self.parser = None
			return self.error

	def directionsign(self, degree):
		return "." if degree < 0 else ["↓ N", "↙ NE", "← E", "↖ SE", "↑ S", "↗ SW", "→ W", "↘ NW"][int(round(degree % 360 / 45 % 7.5))]

	def convert2icon(self, src, code):
		self.error = None
		src = src.lower()
		if code is None:
			self.error = "[%s] ERROR in module 'convert2icon': input code value is 'None'" % MODULE_NAME
			print(self.error)
			return
		code = str(code).strip()
		selection = {"msn": self.msnCodes, "owm": self.owmCodes, "omw": self.omwCodes}
		if src and src in selection:
			common = selection[src]
		else:
			print("WARNING in module 'convert2icon': convert source '%s' is unknown. Valid is: %s" % (src, SOURCES))
			return
		result = dict()
		if src == "msn":
			code = code[:4]  # remove 'windy'-flag in MSN-code if present
		if code in common:
			result["yahooCode"] = common[code][0]
			result["meteoCode"] = common[code][1]
		else:
			result["yahooCode"] = "NA"
			result["meteoCode"] = "NA"
			print("WARNING in module 'convert2icon': key '%s' not found in converting dicts." % code)
			return
		return result

	def getCitylist(self, cityname=None, scheme="de-de", count=10):
		self.error = None
		if not cityname:
			self.error = "[%s] ERROR in module 'getCitylist': missing cityname." % MODULE_NAME
			return

		elif self.mode in ["msn", "omw"]:
			cityname, country = self.separateCityCountry(cityname)
			jsonData = None
			for city in [cityname, cityname.split(" ")[0]]:
				params = [("language", f"{scheme[:2]}"), ("count", f"{count}"), ("name", f"{city}{'' if country is None else ',%s' % country}")]
				jsonData = self.apiserver("https://geocoding-api.open-meteo.com/v1/search", params)
				if jsonData and "latitude" in jsonData.get("results", [""])[0]:
					break
			if jsonData is None or "results" not in jsonData:
				self.error = "[%s] ERROR in module 'getCitylist.owm': no city '%s' found on the server. Try another wording." % (MODULE_NAME, cityname)
				return
			count = 0
			citylist = []
			try:
				for hit in jsonData["results"]:
					count += 1
					if count > 9:
						break
					cityname = hit["name"] if "name" in hit else ""
					country = ", %s" % hit["country"].upper() if "country" in hit else ""
					admin1 = ", %s" % hit["admin1"] if "admin1" in hit else ""
					admin2 = ", %s" % hit["admin2"] if "admin2" in hit else ""
					admin3 = ", %s" % hit["admin3"] if "admin3" in hit else ""
					citylist.append(("%s%s%s%s%s" % (cityname, admin1, admin2, admin3, country), hit["longitude"], hit["latitude"]))
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitylist.owm': general error. %s" % (MODULE_NAME, str(err))
				return

		elif self.mode == "owm":
			special = {"br": "pt_br", "se": "sv, se", "es": "sp, es", "ua": "ua, uk", "cn": "zh_cn"}
			if scheme[:2] in special:
				scheme = special[scheme[:2]]
			cityname, country = self.separateCityCountry(cityname)
			jsonData = None
			for city in [cityname, cityname.split(" ")[0]]:
				link = "http://api.openweathermap.org/geo/1.0/direct?q=%s%s&lang=%s&limit=%s&appid=%s" % (city, "" if country is None else ",%s" % country, scheme[:2], count, self.apikey)
				jsonData = self.apiserver(link)
				if jsonData:
					break
			if not jsonData:
				self.error = "[%s] ERROR in module 'getCitylist.owm': no city '%s' found on the server. Try another wording." % (MODULE_NAME, cityname)
				return
			count = 0
			citylist = []
			try:
				for hit in jsonData:
					count += 1
					if count > 9:
						break
					cityname = hit["local_names"][scheme[:2]] if "local_names" in hit and scheme[:2] in hit["local_names"] else hit["name"]
					state = ", %s" % hit["state"] if "state" in hit else ""
					country = ", %s" % hit["country"].upper() if "country" in hit else ""
					citylist.append(("%s%s%s" % (cityname, state, country), hit["lon"], hit["lat"]))
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitylist.owm': general error. %s" % (MODULE_NAME, str(err))
				return

		else:
			self.error = "[%s] ERROR in module 'getCitylist': unknown mode." % MODULE_NAME
			return
		return citylist

	def separateCityCountry(self, cityname):
			country = None
			for special in [",", ";", "&", "|", "!"]:
				items = cityname.split(special)
				if len(items) > 1:
					cityname = "".join(items[:-1]).strip()
					country = "".join(items[-1:]).strip().upper()
					break
			return cityname, country

	def start(self, geodata=None, cityID=None, units="metric", scheme="de-de", reduced=False, callback=None):  # cityID was left only for compatibility reasons
		self.error = None
		self.geodata = ("", 0, 0) if geodata is None else geodata
		self.units = units.lower()
		self.scheme = scheme.lower()
		self.callback = callback
		self.reduced = reduced
		if not self.geodata[0]:
			self.error = "[%s] ERROR in module 'start': missing cityname for mode '%s'." % (MODULE_NAME, self.mode)
		elif not self.geodata[1] or not self.geodata[2]:
			self.error = "[%s] ERROR in module 'start': missing geodata for mode '%s'." % (MODULE_NAME, self.mode)
		elif self.mode not in SOURCES:
			self.error = "[%s] ERROR in module 'start': unknown mode '%s'." % (MODULE_NAME, self.mode)
		if callback:
			if self.error:
				callback(None, self.error)
			elif self.parser:
				callInThread(self.parser)
		else:
			if self.error:
				return
			elif self.parser:
				info = self.parser()
				return info

	def stop(self):
		self.error = None
		self.callback = None

	def apiserver(self, link, params=None):
		self.error = None
		jsonData = {}
		if link:
			try:
				response = get(link, headers=self.headers, params=params, timeout=(3.05, 6))
				response.raise_for_status()
				jsonData = loads(response.content)
			except exceptions.RequestException as err:
				self.error = "[%s] ERROR in module 'apiserver': '%s" % (MODULE_NAME, str(err))
		else:
			self.error = "[%s] ERROR in module 'apiserver': missing link." % MODULE_NAME
		return jsonData

	def msnparser(self):
		self.error = None
		self.info = None
		self.dataReady = False
		if self.geodata:
			tempunit = "F" if self.units == "imperial" else "C"
			link = "68747470733A2F2F6170692E6D736E2E636F6D2F7765617468657266616C636F6E2F776561746865722F6F766572766965773F266C6F6E3D2573266C61743D2573266C6F63616C653D257326756E6974733D25732661707049643D39653231333830632D666631392D346337382D623465612D313935353865393361356433266170694B65793D6A356934674471484C366E47597778357769356B5268586A74663263357167465839667A666B30544F6F266F6369643D73757065726170702D6D696E692D7765617468657226777261704F446174613D66616C736526696E636C7564656E6F7763617374696E673D7472756526666561747572653D6C696665646179266C696665446179733D363"
		else:
			self.error = "[%s] ERROR in module 'msnparser': missing geodata." % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		if self.callback:
			print("[%s] accessing MSN for weatherdata..." % MODULE_NAME)
		self.info = self.apiserver(bytes.fromhex(link[:-1]).decode('utf-8') % (float(self.geodata[1]), float(self.geodata[2]), self.scheme, tempunit))
		if self.callback:
			if self.error:
				self.callback(None, self.error)
			else:
				print("[%s] MSN successfully accessed..." % MODULE_NAME)
				self.dataReady = True
				self.callback(self.getreducedinfo() if self.reduced else self.info, None)
		if self.info and self.error is None:
			self.dataReady = True
			return self.getreducedinfo() if self.reduced else self.info

	def omwparser(self):
		self.error = None
		self.info = None
		self.dataReady = False
		if self.geodata:
			params = [("timezone", "auto"),
			 		("latitude", f"{round(float(self.geodata[2]), 4)}"),
					("longitude", f"{round(float(self.geodata[1]), 4)}"),
					("current", "pressure_msl"),
					("hourly", "temperature_2m,relativehumidity_2m,apparent_temperature,weathercode,windspeed_10m,wind_gusts_10m,winddirection_10m,precipitation_probability,uv_index,visibility,pressure_msl"),
					("daily", "sunrise,sunset,weathercode,precipitation_probability_max,temperature_2m_max,temperature_2m_min,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,uv_index_max,apparent_temperature_max,apparent_temperature_min"),
					("windspeed_unit", "mph" if self.units == "imperial" else "kmh"),
					("temperature_unit", "fahrenheit" if self.units == "imperial" else "celsius")
					]
		else:
			self.error = "[%s] ERROR in module 'omwparser': missing geodata." % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		if self.callback:
			print("[%s] accessing OMW for weatherdata..." % MODULE_NAME)
		self.info = self.apiserver("https://api.open-meteo.com/v1/forecast", params)
		if self.callback:
			if self.error:
				self.callback(None, self.error)
			else:
				print("[%s] OMW successfully accessed." % MODULE_NAME)
				self.dataReady = True
				self.callback(self.getreducedinfo() if self.reduced else self.info, self.error)
		if self.info and self.error is None:
			self.dataReady = True
			return self.getreducedinfo() if self.reduced else self.info

	def owmparser(self):
		self.error = None
		self.info = None
		self.dataReady = False
		if not self.apikey:
			self.error = "[%s] ERROR in module' owmparser': API-key is missing!" % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		if not self.geodata:
			self.error = "[%s] ERROR in module 'owmparser': missing geodata." % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		params = [("lat", f"{round(float(self.geodata[2]), 4)}"),
				("lon", f"{round(float(self.geodata[1]), 4)}"),
				("lang", self.scheme[:2]),
				("units", self.units),
				("appid", self.apikey)
				]
		if self.callback:
			print("[%s] accessing OWM for weatherdata..." % MODULE_NAME)
		self.info = self.apiserver("https://api.openweathermap.org/data/2.5/weather", params)  # current only
		self.info |= self.apiserver("https://api.openweathermap.org/data/2.5/forecast", params)  # forecasts only
		if self.callback:
			if self.error:
				self.callback(None, self.error)
			else:
				print("[%s] OWM successfully accessed..." % MODULE_NAME)
				self.dataReady = True
				self.callback(self.getreducedinfo() if self.reduced else self.info, self.error)
		if self.info and self.error is None:
			self.dataReady = True
			return self.getreducedinfo() if self.reduced else self.info

	def getreducedinfo(self):
		self.error = None
		daytextfmt = "%a, %d."
		datefmt = "%Y-%m-%d"
		reduced = dict()
		if self.info:
			if self.parser and self.mode == "msn":
				if self.geodata:
					try:
						source = self.info["responses"][0]["source"]
						current = self.info["responses"][0]["weather"][0]["current"]
						forecast = self.info["responses"][0]["weather"][0]["forecast"]["days"]
						reduced["source"] = "MSN Weather"
						location = self.geodata[0].split(", ")
						reduced["name"] = location[0].split(", ")[0]
						reduced["longitude"] = str(source["coordinates"]["lon"])
						reduced["latitude"] = str(source["coordinates"]["lat"])
						reduced["pressunit"] = self.info["units"]["pressure"]
						tempunit = self.info["units"]["temperature"].strip("\u200e")
						reduced["tempunit"] = tempunit
						reduced["windunit"] = self.info["units"]["speed"]
						reduced["precunit"] = "%"
						reduced["uvindexunit"] = ""
						reduced["visibiliyunit"] = self.info["units"]["distance"]
						reduced["current"] = dict()
						reduced["current"]["observationPoint"] = self.createFullname(location)
						currdate = datetime.fromisoformat(current["created"]).replace(tzinfo=None)
						reduced["current"]["observationTime"] = currdate.isoformat()
						sunrise = datetime.fromisoformat(forecast[0]["almanac"]["sunrise"]).replace(tzinfo=None)
						reduced["current"]["sunrise"] = sunrise.isoformat()
						sunset = datetime.fromisoformat(forecast[0]["almanac"]["sunset"]).replace(tzinfo=None)
						reduced["current"]["sunset"] = sunset.isoformat()
						moonrise = datetime.fromisoformat(forecast[0]["almanac"]["moonrise"]).replace(tzinfo=None)
						reduced["current"]["moonrise"] = moonrise.isoformat()
						moonset = datetime.fromisoformat(forecast[0]["almanac"]["moonset"]).replace(tzinfo=None)
						reduced["current"]["moonset"] = moonset.isoformat()
						now = datetime.now()
						reduced["current"]["isNight"] = now < sunrise or now > sunset
						pvdrCode = forecast[0]["hourly"][0]["symbol"] if forecast[0]["hourly"] else current["symbol"]
						reduced["current"]["ProviderCode"] = pvdrCode
						iconCode = self.convert2icon("MSN", pvdrCode)
						reduced["current"]["yahooCode"] = iconCode.get("yahooCode", "NA") if iconCode else "NA"
						reduced["current"]["meteoCode"] = iconCode.get("meteoCode", ")") if iconCode else ")"
						reduced["current"]["pressure"] = "%.0f" % current["baro"]
						reduced["current"]["temp"] = "%.0f" % current["temp"]
						reduced["current"]["feelsLike"] = "%.0f" % current["feels"]
						reduced["current"]["humidity"] = "%.0f" % current["rh"]
						reduced["current"]["windSpeed"] = "%.0f" % current["windSpd"]
						windDir = current["windDir"]
						reduced["current"]["windDir"] = str(windDir)
						reduced["current"]["windDirSign"] = self.directionsign(windDir)
						reduced["current"]["windGusts"] = "%.0f" % current["windGust"]
						reduced["current"]["uvIndex"] = "%.0f" % current["uv"]
						reduced["current"]["visibility"] = "%.0f" % current["vis"]
						reduced["current"]["maxTemp"] = "%.0f" % forecast[0]["daily"]["tempHi"]
						reduced["current"]["minTemp"] = "%.0f" % forecast[0]["daily"]["tempLo"]
						reduced["current"]["precipitation"] = "%.0f" % forecast[0]["daily"]["day"]["precip"]
						reduced["current"]["dayText"] = currdate.strftime(daytextfmt)
						reduced["current"]["day"] = currdate.strftime("%A")
						reduced["current"]["shortDay"] = currdate.strftime("%a")
						reduced["current"]["date"] = currdate.strftime(datefmt)
						reduced["current"]["text"] = forecast[0]["hourly"][0]["pvdrCap"] if forecast[0]["hourly"] else current["capAbbr"]
						reduced["current"]["raintext"] = self.info["responses"][0]["weather"][0]["nowcasting"]["summary"]
						reduced["forecast"] = dict()
						for idx in range(7):  # collect forecast of today and next 6 days
							reduced["forecast"][idx] = dict()
							pvdrCode = forecast[idx]["daily"]["symbol"]
							reduced["forecast"][idx]["ProviderCode"] = pvdrCode
							iconCodes = self.convert2icon("MSN", pvdrCode)
							reduced["forecast"][idx]["yahooCode"] = iconCodes.get("yahooCode", "NA") if iconCodes else "NA"
							reduced["forecast"][idx]["meteoCode"] = iconCodes.get("meteoCode", ")") if iconCodes else ")"
							reduced["forecast"][idx]["pressure"] = "%.0f" % forecast[idx]["daily"]["baro"]
							reduced["forecast"][idx]["minTemp"] = "%.0f" % forecast[idx]["daily"]["tempLo"]
							reduced["forecast"][idx]["maxTemp"] = "%.0f" % forecast[idx]["daily"]["tempHi"]
							reduced["forecast"][idx]["maxFeelsLike"] = "%.0f" % forecast[idx]["daily"]["feelsHi"]
							reduced["forecast"][idx]["minFeelsLike"] = "%.0f" % forecast[idx]["daily"]["feelsLo"]
							reduced["forecast"][idx]["maxWindSpeed"] = "%.0f" % forecast[idx]["daily"]["windMax"]
							windDir = forecast[idx]["daily"]["windMaxDir"]
							reduced["forecast"][idx]["domWindDir"] = "%.0f" % windDir
							reduced["forecast"][idx]["domWindDirSign"] = self.directionsign(windDir)
							reduced["forecast"][idx]["maxWindGusts"] = "%.0f" % forecast[idx]["daily"]["windTh"]
							reduced["forecast"][idx]["maxUvIndex"] = "%.0f" % forecast[idx]["daily"]["uv"]
							reduced["forecast"][idx]["maxVisibility"] = "%.0f" % forecast[idx]["daily"]["vis"]
							reduced["forecast"][idx]["precipitation"] = "%.0f" % forecast[idx]["daily"]["day"]["precip"]
							reduced["forecast"][idx]["dayText"] = currdate.strftime(daytextfmt)
							reduced["forecast"][idx]["day"] = currdate.strftime("%A")
							reduced["forecast"][idx]["shortDay"] = currdate.strftime("%a")
							reduced["forecast"][idx]["date"] = currdate.strftime(datefmt)
							reduced["forecast"][idx]["text"] = forecast[idx]["daily"]["pvdrCap"]
							reduced["forecast"][idx]["daySummary0"] = forecast[idx]["daily"]["day"]["summaries"][0]
							reduced["forecast"][idx]["daySummary1"] = forecast[idx]["daily"]["day"]["summaries"][1].replace("°.", " %s." % tempunit)
							reduced["forecast"][idx]["nightSummary0"] = forecast[idx]["daily"]["night"]["summaries"][0]
							reduced["forecast"][idx]["nightSummary1"] = forecast[idx]["daily"]["night"]["summaries"][1].replace("°.", " %s." % tempunit)
							umbrellaIndex = self.info["responses"][0]["weather"][0]["lifeDaily"]["days"][0]["umbrellaIndex"]
							reduced["forecast"][idx]["umbrellaIndex"] = umbrellaIndex["longSummary2"] if "longSummary2" in umbrellaIndex else umbrellaIndex["summary"]
							currdate = currdate + timedelta(1)
					except Exception as err:
						self.error = "[%s] ERROR in module 'getreducedinfo#msn': general error. %s" % (MODULE_NAME, str(err))
						return

			elif self.parser and self.mode == "omw":
				if self.geodata:
					try:
						hourly = self.info["hourly"]
						forecast = self.info["daily"]
						reduced["source"] = "Open-Meteo Weather"
						location = self.geodata[0].split(", ")
						reduced["name"] = location[0].split(", ")[0]
						reduced["longitude"] = str(self.info["longitude"])
						reduced["latitude"] = str(self.info["latitude"])
						reduced["pressunit"] = "mbar"
						reduced["tempunit"] = self.info["hourly_units"]["temperature_2m"]
						reduced["windunit"] = self.info["hourly_units"]["windspeed_10m"]
						reduced["precunit"] = self.info["hourly_units"]["precipitation_probability"]
						reduced["uvindexunit"] = self.info["hourly_units"]["uv_index"]
						reduced["visibiliyunit"] = "miles" if self.units == "imperial" else "km"
						isotime = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0).isoformat()[:16]
						reduced["current"] = dict()
						for idx, time in enumerate(hourly["time"]):  # collect current
							if isotime in time:
								reduced["current"]["observationPoint"] = self.createFullname(location)
								reduced["current"]["observationTime"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
								sunrise = datetime.fromisoformat(forecast["sunrise"][0])
								reduced["current"]["sunrise"] = sunrise.isoformat()
								sunset = datetime.fromisoformat(forecast["sunset"][0])
								reduced["current"]["sunset"] = sunset.isoformat()
								now = datetime.now()
								reduced["current"]["isNight"] = now < sunrise or now > sunset
								pvdrCode = hourly["weathercode"][idx]
								reduced["current"]["ProviderCode"] = str(pvdrCode)
								iconCode = self.convert2icon("OMW", pvdrCode)
								if iconCode:
									reduced["current"]["yahooCode"] = iconCode.get("yahooCode", "NA")
									reduced["current"]["meteoCode"] = iconCode.get("meteoCode", ")")
								reduced["current"]["pressure"] = "%.0f" % self.info["current"]["pressure_msl"]
								reduced["current"]["temp"] = "%.0f" % hourly["temperature_2m"][0]
								reduced["current"]["feelsLike"] = "%.0f" % hourly["apparent_temperature"][idx]
								reduced["current"]["humidity"] = "%.0f" % hourly["relativehumidity_2m"][idx]
								reduced["current"]["windSpeed"] = "%.0f" % hourly["windspeed_10m"][idx]
								windDir = hourly["winddirection_10m"][idx]
								reduced["current"]["windDir"] = str(windDir)
								reduced["current"]["windDirSign"] = self.directionsign(windDir)
								reduced["current"]["windGusts"] = "%.0f" % hourly["wind_gusts_10m"][idx]
								reduced["current"]["uvIndex"] = "%.0f" % hourly["uv_index"][idx]
								reduced["current"]["visibility"] = "%.0f" % round(hourly["visibility"][idx] / 1000)
								currdate = datetime.fromisoformat(time)
								reduced["current"]["dayText"] = currdate.strftime(daytextfmt)
								reduced["current"]["day"] = currdate.strftime("%A")
								reduced["current"]["shortDay"] = currdate.strftime("%a")
								reduced["current"]["date"] = currdate.strftime(datefmt)
								reduced["current"]["maxTemp"] = "%.0f" % forecast["temperature_2m_max"][0]
								reduced["current"]["minTemp"] = "%.0f" % forecast["temperature_2m_min"][0]
								reduced["current"]["precipitation"] = "%.0f" % hourly["precipitation_probability"][idx]
								break
						todaydate = hourly["time"][0][:10]
						hourpress, hourcount = 0, 0
						avpress = []
						hourlytime = hourly["time"]
						for idx, daydate in enumerate(hourlytime):  # collect all sealevel pressures and create averages per day
							if todaydate.startswith(daydate[:10]):
								hourpress += hourly["pressure_msl"][idx]
								hourcount += 1
							else:
								todaydate = daydate[:10]
								avpress.append(round(hourpress / hourcount))
								hourpress, hourcount = 0, 0
						avpress.append(round(hourpress / hourcount))
						reduced["forecast"] = dict()
						for idx in range(7):  # collect forecast of today and next 6 days
							reduced["forecast"][idx] = dict()
							pvdrCode = forecast["weathercode"][idx]
							reduced["forecast"][idx]["ProviderCode"] = str(pvdrCode)
							iconCode = self.convert2icon("OMW", pvdrCode)
							if iconCode:
								reduced["forecast"][idx]["yahooCode"] = iconCode.get("yahooCode", "NA")
								reduced["forecast"][idx]["meteoCode"] = iconCode.get("meteoCode", ")")
							reduced["forecast"][idx]["pressure"] = "%.0f" % avpress[idx]
							reduced["forecast"][idx]["minTemp"] = "%.0f" % forecast["temperature_2m_min"][idx]
							reduced["forecast"][idx]["maxTemp"] = "%.0f" % forecast["temperature_2m_max"][idx]
							reduced["forecast"][idx]["maxFeelsLike"] = "%.0f" % forecast["apparent_temperature_max"][idx]
							reduced["forecast"][idx]["minFeelsLike"] = "%.0f" % forecast["apparent_temperature_min"][idx]
							reduced["forecast"][idx]["maxWindSpeed"] = "%.0f" % forecast["wind_speed_10m_max"][idx]
							windDir = forecast["wind_direction_10m_dominant"][idx]
							reduced["forecast"][idx]["domWindDir"] = "%.0f" % windDir
							reduced["forecast"][idx]["domWindDirSign"] = self.directionsign(windDir)
							reduced["forecast"][idx]["maxWindGusts"] = "%.0f" % forecast["wind_gusts_10m_max"][idx]
							reduced["forecast"][idx]["maxUvIndex"] = "%.0f" % forecast["uv_index_max"][idx]
							reduced["forecast"][idx]["maxVisibility"] = "%.0f" % round(max(hourly.get("visibility", [] + [0])) / 1000)
							reduced["forecast"][idx]["precipitation"] = "%.0f" % forecast["precipitation_probability_max"][idx]
							currdate = datetime.fromisoformat(forecast["time"][idx])
							reduced["forecast"][idx]["dayText"] = currdate.strftime(daytextfmt)
							reduced["forecast"][idx]["day"] = currdate.strftime("%A")
							reduced["forecast"][idx]["shortDay"] = currdate.strftime("%a")
							reduced["forecast"][idx]["date"] = currdate.strftime(datefmt)
					except Exception as err:
						self.error = "[%s] ERROR in module 'getreducedinfo#omw': general error. %s" % (MODULE_NAME, str(err))
						return
				else:
					self.error = "[%s] ERROR in module 'getreducedinfo#omw': missing geodata." % MODULE_NAME

			elif self.parser and self.mode == "owm":   #  OpenWeatherMap is DEPRECATED
				if self.geodata:
					try:
						main = self.info["main"]
						reduced["source"] = "OpenWeatherMap"  # collect current weather data
						location = self.geodata[0].split(", ")
						reduced["name"] = location[0].split(", ")[0]
						reduced["longitude"] = str(self.info["city"]["coord"]["lon"])
						reduced["latitude"] = str(self.info["city"]["coord"]["lat"])
						reduced["pressunit"] = "mbar"
						reduced["tempunit"] = "°F" if self.units == "imperial" else "°C"
						reduced["windunit"] = "mph" if self.units == "imperial" else "km/h"
						reduced["precunit"] = "%"
						reduced["visibiliyunit"] = "miles" if self.units == "imperial" else "km"
						reduced["current"] = dict()
						now = datetime.now()
						isotime = datetime.now(timezone.utc).isoformat()
						reduced["current"]["observationPoint"] = self.createFullname(location)
						reduced["current"]["observationTime"] = "%s%s" % (isotime[: 19], isotime[26:])
						sunrise = datetime.fromtimestamp(self.info["city"]["sunrise"])
						sunset = datetime.fromtimestamp(self.info["city"]["sunset"])
						reduced["current"]["sunrise"] = sunrise.isoformat()
						reduced["current"]["sunset"] = sunset.isoformat()
						reduced["current"]["isNight"] = now < sunrise or now > sunset
						pvdrCode = self.info["weather"][0]["id"]
						reduced["current"]["ProviderCode"] = str(pvdrCode)
						iconCode = self.convert2icon("OWM", pvdrCode)
						if iconCode:
							reduced["current"]["yahooCode"] = iconCode.get("yahooCode", "NA")
							reduced["current"]["meteoCode"] = iconCode.get("meteoCode", ")")
						reduced["current"]["pressure"] = "%.0f" % main["pressure"]
						reduced["current"]["temp"] = "%.0f" % main["temp"]
						reduced["current"]["feelsLike"] = "%.0f" % main["feels_like"]
						reduced["current"]["humidity"] = "%.0f" % main["humidity"]
						reduced["current"]["windSpeed"] = "%.0f" % (self.info["wind"]["speed"] * 3.6)
						windDir = self.info["wind"]["deg"]
						reduced["current"]["windDir"] = str(windDir)
						reduced["current"]["windDirSign"] = self.directionsign(int(windDir))
						reduced["current"]["windGusts"] = "%.0f" % self.info["list"][0]["wind"]["gust"]
						reduced["current"]["visibility"] = "%.0f" % round(self.info["visibility"] / 1000)
						currdate = datetime.fromtimestamp(self.info["dt"])
						reduced["current"]["dayText"] = currdate.strftime(daytextfmt)
						reduced["current"]["day"] = currdate.strftime("%A")
						reduced["current"]["shortDay"] = currdate.strftime("%a")
						reduced["current"]["date"] = currdate.strftime(datefmt)
						reduced["current"]["text"] = self.info["weather"][0]["description"]
						# inits for today
						hourpress, hourcount = 0, 0
						tmin, tmax, fmin, fmax, wmax, gmax, vmax = 88, -88, 88, -88, -88, -88, -88
						yahoocode, meteocode, text = None, None, None
						prec, wdir = [], []
						idx = 0
						reduced["forecast"] = dict()
						for index, forecast in enumerate(self.info.get("list", [])):  # collect forecast of today and next 5 days
							main = forecast.get("main", {})
							if not index:
								reduced["current"]["pressure"] = f"{round(main.get("pressure", 0))}"  # catch the missing data for current weather
								reduced["current"]["minTemp"] = f"{round(main.get("temp_min", 0))}"
								reduced["current"]["maxTemp"] = f"{round(main.get("temp_max", 0))}"
								reduced["current"]["precipitation"] = f"{round(forecast.get("pop", 0) * 100)}"
							hourpress += main.get("pressure", 0)
							hourcount += 1
							tmin = min(tmin, main.get("temp_min", 0))
							tmax = max(tmax, main.get("temp_max", 0))
							fmin = min(fmin, main.get("feels_like", 0))
							fmax = max(fmax, main.get("feels_like", 0))
							wmax = max(wmax, main.get("speed", 0))
							gmax = max(gmax, main.get("gust", 0))
							vmax = max(vmax, forecast.get("visibility", 0) / 1000)
							wdir.append(forecast["wind"]["deg"])
							prec.append(forecast["pop"])
							dt_text = forecast["dt_txt"]
							if "15:00:00" in dt_text:  # get weather icon as a representative icon for current day
								pvdrCode = forecast.get("weather", [])[0].get("id", "NA")
								iconCode = self.convert2icon("OWM", pvdrCode)
								if iconCode:
									yahoocode = iconCode.get("yahooCode", "NA")
									meteocode = iconCode.get("meteoCode", ")")
								text = forecast["weather"][0]["description"]
							if "18:00:00" in dt_text and not yahoocode:  # in case we call the forecast late today: get current weather icon
								pvdrCode = forecast["weather"][0]["id"]
								iconCode = self.convert2icon("OWM", pvdrCode)
								if iconCode:
									yahoocode = iconCode.get("yahooCode", "NA")
									meteocode = iconCode.get("meteoCode", ")")
								text = text if text else forecast.get("weather", [])[0].get("description", "")
							if "21:00:00" in dt_text:  # last available data before daychange
								reduced["forecast"][idx] = dict()
								if not yahoocode:
									pvdrCode = forecast["weather"][0]["id"]
									reduced["forecast"][idx]["ProviderCode"] = str(pvdrCode)
									iconCode = self.convert2icon("OWM", pvdrCode)
									if iconCode:
										yahoocode = iconCode.get("yahooCode", "NA")
										meteocode = iconCode.get("meteoCode", ")")
								reduced["forecast"][idx]["yahooCode"] = yahoocode
								reduced["forecast"][idx]["meteoCode"] = meteocode
								reduced["forecast"][idx]["pressure"] = "%.0f" % round(hourpress / hourcount)
								reduced["forecast"][idx]["minTemp"] = "%.0f" % tmin
								reduced["forecast"][idx]["maxTemp"] = "%.0f" % tmax
								reduced["forecast"][idx]["maxFeelsLike"] = "%.0f" % fmin
								reduced["forecast"][idx]["minFeelsLike"] = "%.0f" % fmax
								reduced["forecast"][idx]["maxWindSpeed"] = "%.0f" % wmax
								wdom = round(sum(wdir) / len(wdir)) if wdir else 0
								reduced["forecast"][idx]["domWindDir"] = "%.0f" % wdom
								reduced["forecast"][idx]["domWindDirSign"] = self.directionsign(wdom)
								reduced["forecast"][idx]["maxWindGusts"] = "%.0f" % gmax
								reduced["forecast"][idx]["maxVisibility"] = "%.0f" % vmax
								reduced["forecast"][idx]["precipitation"] = "%.0f" % (sum(prec) / len(prec) * 100) if len(prec) > 0 else ""
								reduced["forecast"][idx]["dayText"] = currdate.strftime(daytextfmt)
								reduced["forecast"][idx]["day"] = currdate.strftime("%A")
								reduced["forecast"][idx]["shortDay"] = currdate.strftime("%a")
								reduced["forecast"][idx]["date"] = currdate.strftime(datefmt)
								reduced["forecast"][idx]["text"] = text
								# inits for next day
								hourpress, hourcount = 0, 0
								tmin, tmax, fmin, fmax, wmax, gmax, vmax = 88, -88, 88, -88, -88, -88, -88
								yahoocode, meteocode, text = None, None, None
								prec, wdir = [], []
								idx += 1
							if idx == 5 and "21:00:00" in forecast["dt_txt"]:  # in case day #5 is missing: create a copy of day 4 (=fake), in case day #5 is incomplete: use what we have
								reduced["forecast"][idx] = dict()
								pvdrCode = forecast["weather"][0]["id"]
								reduced["forecast"][idx]["ProviderCode"] = str(pvdrCode)
								reduced["forecast"][idx]["yahooCode"] = yahoocode if yahoocode else reduced["forecast"][idx - 1]["yahooCode"]
								reduced["forecast"][idx]["meteoCode"] = meteocode if meteocode else reduced["forecast"][idx - 1]["meteoCode"]
								reduced["forecast"][idx]["pressure"] = reduced["forecast"][idx - 1]["pressure"]
								reduced["forecast"][idx]["minTemp"] = "%.0f" % tmin if tmin != 88 else reduced["forecast"][idx - 1]["minTemp"]
								reduced["forecast"][idx]["maxTemp"] = "%.0f" % tmax if tmax != - 88 else reduced["forecast"][idx - 1]["maxTemp"]
								reduced["forecast"][idx]["maxFeelsLike"] = "%.0f" % fmin if fmin != 88 else reduced["forecast"][idx - 1]["minFeelsLike"]
								reduced["forecast"][idx]["minFeelsLike"] = "%.0f" % fmax if fmax != - 88 else reduced["forecast"][idx - 1]["maxFeelsLike"]
								reduced["forecast"][idx]["maxWindSpeed"] = "%.0f" % wmax if wmax != - 88 else reduced["forecast"][idx - 1]["maxWindSpeed"]
								wdom = round(sum(wdir) / len(wdir)) if wdir else 0
								reduced["forecast"][idx]["domWindDir"] = "%.0f" % wdom
								reduced["forecast"][idx]["domWindDirSign"] = self.directionsign(wdom)
								reduced["forecast"][idx]["maxWindGusts"] = "%.0f" % gmax if gmax != - 88 else reduced["forecast"][idx - 1]["maxWindGusts"]
								reduced["forecast"][idx]["maxVisibility"] = "%.0f" % vmax if vmax != - 88 else reduced["forecast"][idx - 1]["maxVisibility"]
								reduced["forecast"][idx]["precipitation"] = "%.0f" % (sum(prec) / len(prec) * 100) if len(prec) > 0 else ""
								nextdate = datetime.strptime(reduced["forecast"][idx - 1]["date"], datefmt) + timedelta(1)
								reduced["forecast"][idx]["dayText"] = currdate.strftime(daytextfmt)
								reduced["forecast"][idx]["day"] = nextdate.strftime("%A")
								reduced["forecast"][idx]["shortDay"] = nextdate.strftime("%a")
								reduced["forecast"][idx]["date"] = nextdate.strftime(datefmt)
								reduced["forecast"][idx]["text"] = text if text else reduced["forecast"][idx - 1]["text"]
					except Exception as err:
						self.error = "[%s] ERROR in module 'getreducedinfo#owm': general error. %s" % (MODULE_NAME, str(err))
						return
				else:
					self.error = "[%s] ERROR in module 'getreducedinfo#owm': missing geodata." % MODULE_NAME

			else:
				self.error = "[%s] ERROR in module 'getreducedinfo': unknown source." % MODULE_NAME
				return
		return reduced

	def writereducedjson(self, filename):
		self.error = None
		reduced = self.getreducedinfo()
		if self.error:
			return
		if reduced is None:
			self.error = "[%s] ERROR in module 'writereducedjson': no data found." % MODULE_NAME
			return
		with open(filename, "w") as f:
			dump(reduced, f)
		return filename

	def writejson(self, filename):
		self.error = None
		if self.info:
			try:
				with open(filename, "w") as f:
					dump(self.info, f)
			except Exception as err:
				self.error = "[%s] ERROR in module 'writejson': %s" % (MODULE_NAME, str(err))
		else:
			self.error = "[%s] ERROR in module 'writejson': no data found." % MODULE_NAME

	def getinfo(self):
		self.error = None
		if self.info is None:
			self.error = "[%s] ERROR in module 'getinfo': Parser not ready" % MODULE_NAME
			return
		return self.info

	def showDescription(self, src):
		self.error = None
		src = src.lower()
		selection = {"msn": self.msnDescs, "owm": self.owmDescs, "omw": self.omwDescs, "yahoo": self.yahooDescs, "meteo": self.meteoDescs}
		if src and src in selection:
			descs = selection[src]
		else:
			self.error = "[%s] ERROR in module 'showDescription': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, SOURCES)
			return self.error
		print("\n+%s+" % ("-" * 39))
		print("| {0:<5}{1:<32} |".format("CODE", "DESCRIPTION_%s (COMPLETE)" % src.upper()))
		print("+%s+" % ("-" * 39))
		for desc in descs:
			print("| {0:<5}{1:<32} |".format(desc, descs[desc]))
		print("+%s+" % ("-" * 39))

	def showConvertrules(self, src, dest):
		self.error = None
		src = src.lower()
		dest = dest.lower()
		if not src:
			self.error = "[%s] ERROR in module 'showConvertrules': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, SOURCES)
			return self.error
		selection = {"meteo": self.meteoDescs, "yahoo": self.yahooDescs}
		if dest in selection:
			ddescs = selection[dest]
			destidx = DESTINATIONS.index(dest)
		else:
			self.error = "[%s] ERROR in module 'showConvertrules': convert destination '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, DESTINATIONS)
			return self.error
		print("\n+%s+%s+" % ("-" * 39, "-" * 32))
		selection = {"msn": self.msnCodes, "omw": self.omwCodes, "owm": self.owmCodes}
		if src in selection:
			sCodes = selection[src]
			row = "| {0:<5}{1:<32} | {2:<5}{3:<25} |"
			print(row.format("CODE", "DESCRIPTION_%s (CONVERTER)" % src.upper(), "CODE", "DESCRIPTION_%s" % dest.upper()))
			print("+%s+%s+" % ("-" * 39, "-" * 32))
			if src == "msn":
				for scode in sCodes:
					dcode = sCodes[scode][destidx]
					print(row.format(scode, self.msnDescs[scode], dcode, ddescs[dcode]))
			elif src == "omw":
				for scode in self.omwCodes:
					dcode = self.omwCodes[scode][destidx]
					print(row.format(scode, self.omwDescs[scode], dcode, ddescs[dcode]))
			elif src == "owm":
				for scode in self.owmCodes:
					dcode = self.owmCodes[scode][destidx]
					print(row.format(scode, self.owmDescs[scode], dcode, ddescs[dcode]))
			print("+%s+%s+" % ("-" * 39, "-" * 32))
		else:
			self.error = "[%s] ERROR in module 'showConvertrules': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, SOURCES)
			return self.error

	def createFullname(self, location):
			components = list(dict.fromkeys(location))  # remove duplicates from list
			len_components = len(components)
			if len_components > 2:
				return (f"{components[0]}, {components[1]}, {components[-1]}")
			return (f"{components[0]}, {components[1]}") if len_components == 2 else (f"{components[0]}")

	def getDataReady(self):
		return self.dataReady


def main(argv):
	mainfmt = "[__main__]"
	cityname = ""
	units = "metric"
	scheme = "de-de"
	mode = "msn"
	apikey = None
	quiet = False
	json = None
	reduced = False
	specialopt = None
	control = False
	geodata = None
	info = None
	geodata = ("", 0, 0)
	helpstring = "Weatherinfo v2.8: try 'python Weatherinfo.py -h' for more information"
	opts = None
	args = None
	try:
		opts, args = getopt(argv, "hqm:a:j:r:x:s:u:i:c", ["quiet =", "mode=", "apikey=", "json =", "reduced =", "scheme =", "units =", "control ="])
	except GetoptError:
		print(helpstring)
		exit(2)
	for opt, arg in opts:
		opt = opt.lower().strip()
		arg = arg.lower().strip()
		if opt == "-h":
			print("Usage: python Weatherinfo.py [options...] <cityname>\n"
			"-m, --mode <data>\t\tValid modes: 'omw', 'owm' or 'msn' {'msn' is default}\n"
			"-a, --apikey <data>\t\tAPI-key required for 'owm' only\n"
			"-j, --json <filename>\t\tFile output formatted in JSON (all modes)\n"
			"-r, --reduced <filename>\tFile output formatted in JSON (minimum infos only)\n"
			"-s, --scheme <data>\t\tCountry scheme (not used by 'omw') {'de-de' is default}\n"
			"-u, --units <data>\t\tValid units: 'imperial' or 'metric' {'metric' is default}\n"
			"-c, --control\t\t\tShow iconcode-plaintexts and conversion rules\n"
			"-q, --quiet\t\t\tPerform without text output and select first found city")
			exit()
		elif opt in ("-u", "--units:"):
			if arg in ["metric", "imperial"]:
				units = arg
			else:
				print("ERROR: units '%s' is invalid. Valid parameters: 'metric' or 'imperial'" % arg)
				exit()
		elif opt in ("-j", "--json"):
			json = arg
		elif opt in ("-r", "--reduced"):
			reduced = arg
		elif opt in ("-s", "--scheme"):
			scheme = arg
		elif opt in ("-m", "--mode"):
			if arg in SOURCES:
				mode = arg
			else:
				print("ERROR: mode '%s' is invalid. Valid parameters: '%s'" % (arg, "', '".join(SOURCES)))
				exit()
		elif opt in ("-a", "--apikey"):
			apikey = arg
		elif opt in ("-c", "control"):
			control = True
			specialopt = True
		elif opt in ("-q", "--quiet"):
			quiet = True
			specialopt = True
	for part in args:
		cityname += "%s " % part
	cityname = cityname.strip()
	if len(cityname) < 3 and not specialopt:
		print("ERROR: Cityname is missing or too short, please use at least 3 letters!")
		exit()
	if len(args) == 0 and not specialopt:
		print(helpstring)
		exit()
	WI = Weatherinfo(mode, apikey)
	if control:
		for src in SOURCES + DESTINATIONS:
			if WI.showDescription(src) and WI.error:
				print(WI.error.replace(mainfmt, "").strip())
		for src in SOURCES:
			for dest in DESTINATIONS:
				WI.showConvertrules(src, dest)
	if WI.error:
		print(WI.error.replace(mainfmt, "").strip())
		exit()
	if cityname:
		citylist = WI.getCitylist(cityname, scheme)
		if WI.error:
			print(WI.error.replace(mainfmt, "").strip())
			exit()
		if len(citylist) == 0:
			print("No city '%s' found on the server. Try another wording." % cityname)
			exit()
		geodata = citylist[0]
		if citylist and len(citylist) > 1 and not quiet:
			print("Found the following cities/areas:")
			for idx, item in enumerate(citylist):
				lon = " [lon=%s" % item[1] if item[1] != 0 else ""
				lat = ", lat=%s]" % item[2] if item[2] != 0 else ""
				print("%s = %s%s%s" % (idx + 1, item[0], lon, lat))
			choice = input("Select (1-%s)? : " % len(citylist))[: 1]
			index = ord(choice) - 48 if len(choice) > 0 else -1
			if index > 0 and index < len(citylist) + 1:
				geodata = citylist[index - 1]
			else:
				print("Choice '%s' is not allowable (only numbers 1 to %s are valid).\nPlease try again." % (choice, len(citylist)))
				exit()
	if not specialopt:
		if geodata:
			info = WI.start(geodata=geodata, units=units, scheme=scheme)  # INTERACTIVE CALL (unthreaded)
		else:
			print("ERROR: missing cityname or geodata.")
			exit()
	if WI.error:
		print(WI.error.replace(mainfmt, "").strip())
		exit()

	if info and not control:
		if not quiet:
			print("Using city/area: %s [lon=%s, lat=%s]" % (geodata[0], geodata[1], geodata[2]))
		successtext = "File '%s' was successfully created."
		if json:
			WI.writejson(json)
			if not quiet and not WI.error:
				print(successtext % json)
		if reduced:
			WI.writereducedjson(reduced)
			if not quiet:
				print(successtext % reduced)
	if WI.error:
			print(WI.error.replace(mainfmt, "").strip())


if __name__ == "__main__":
	main(argv[1:])
