#########################################################################################################
#                                                                                                       #
#  Weatherinfo for openTV is a multiplatform tool (runs on Enigma2 & Windows and probably many others)  #
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
from re import search, findall
from urllib.request import quote
from datetime import datetime, timedelta, timezone
from requests import get, exceptions
from getopt import getopt, GetoptError
from twisted.internet.reactor import callInThread
from xml.etree.ElementTree import Element, tostring

MODULE_NAME = __name__.split(".")[-1]


class Weatherinfo:
	def __init__(self, newmode="msn", apikey=None):
		self.SOURCES = ["msn", "owm", "omw"]  # supported sourcecodes (the order must not be changed)
		self.DESTINATIONS = ["yahoo", "meteo"]  # supported iconcodes (the order must not be changed)

		self.msnPvdr = {"1": "1", "2": "1", "3": "1", "4": "4", "5": "4", "6": "6", "7": "7", "8": "8", "9": "9", "10": "8",
						"11": "8", "12": "9", "13": "8", "14": "8", "15": "7", "16": "7", "17": "8", "18": "9", "19": "8",
						"20": "7", "21": "9", "22": "8", "23": "8", "24": "7", "25": "7", "26": "7", "27": "27", "28": "1",
						"29": "1", "30": "4", "31": "4", "32": "4", "33": "6", "34": "7", "35": "8", "36": "9", "37": "8",
						"38": "8", "39": "9", "40": "8", "41": "8", "42": "7", "43": "7", "44": "8", "45": "9", "46": "8",
						"47": "7", "48": "9", "49": "8", "50": "8", "51": "8", "52": "7", "53": "7", "54": "27", "57": "7",
						"58": "7", "59": "7", "60": "7", "61": "6", "62": "6", "63": "9", "64": "9", "65": "9", "66": "9",
						"67": "27", "68": "27", "69": "8", "70": "8", "71": "8", "72": "8", "73": "9", "74": "9", "75": "8",
						"76": "8", "77": "8", "78": "8", "79": "8", "80": "8", "81": "7", "82": "7", "83": "8", "84": "8",
						"85": "8", "86": "8", "87": "6", "88": "6", "89": "9", "90": "9", "91": "6", "92": "6", "93": "6",
						"94": "6", "95": "9", "96": "9", "101": "1", "102": "1", "na": "na"
						}  # mapping: provider-external -> msn-internal
		self.msnCodes = {
						"1": ("32", "B"), "2": ("34", "B"), "3": ("30", "H"), "4": ("28", "H"), "5": ("26", "N"),
						"6": ("15", "X"), "7": ("15", "U"), "8": ("9", "Q"), "9": ("20", "M"), "10": ("10", "X"),
						"12": ("22", "J"), "14": ("11", "Q"), "15": ("41", "V"), "16": ("17", "X"), "17": ("9", "Q"),
						"19": ("9", "Q"), "20": ("14", "U"), "23": ("12", "R"), "26": ("46", "U"), "27": ("4", "P"),
						"28": ("31", "C"), "29": ("33", "C"), "30": ("29", "I"), "31": ("27", "I"), "39": ("22", "K"),
						"43": ("17", "X"), "44": ("9", "Q"), "50": ("12", "R"), "77": ("5", "W"), "78": ("5", "W"),
						"82": ("46", "U"), "91": ("24", "S"), "na": ("NA", ")")
						}  # mapping: msn-internal -> (yahoo, meteo)
		self.owmCodes = {
						"200": ("4", "O"), "201": ("4", "O"), "202": ("4", "P"), "210": ("39", "O"), "211": ("4", "O"),
						"212": ("3", "P"), "221": ("38", "O"), "230": ("4", "O"), "231": ("4", "O"), "232": ("4", "O"),
						"300": ("9", "Q"), "301": ("9", "Q"), "302": ("9", "Q"), "310": ("9", "Q"), "311": ("9", "Q"),
						"312": ("9", "R"), "313": ("11", "R"), "314": ("12", "R"), "321": ("11", "R"), "500": ("9", "Q"),
						"501": ("11", "Q"), "502": ("12", "R"), "503": ("45", "R"), "504": ("45", "R"), "511": ("10", "W"),
						"520": ("40", "Q"), "521": ("11", "R"), "522": ("45", "R"), "531": ("40", "Q"), "600": ("13", "U"),
						"601": ("16", "V"), "602": ("41", "V"), "611": ("18", "X"), "612": ("10", "W"), "613": ("17", "X"),
						"615": ("5", "W"), "616": ("5", "W"), "620": ("14", "U"), "621": ("42", "U"), "622": ("46", "V"),
						"701": ("20", "M"), "711": ("22", "J"), "721": ("21", "E"), "731": ("19", "J"), "741": ("20", "E"),
						"751": ("19", "J"), "761": ("19", "J"), "762": ("22", "J"), "771": ("23", "F"), "781": ("0", "F"),
						"800": ("32", "B"), "801": ("34", "B"), "802": ("30", "H"), "803": ("26", "H"), "804": ("28", "N"),
						"na": ("NA", ")")
						}  # mapping: owm -> (yahoo, meteo)
		self.omwCodes = {"0": ("32", "B"), "1": ("34", "B"), "2": ("30", "H"), "3": ("28", "N"), "45": ("20", "M"), "48": ("21", "J"),
						"51": ("9", "Q"), "53": ("9", "Q"), "55": ("9", "R"), "56": ("8", "V"), "57": ("10", "U"),
						"61": ("11", "Q"), "63": ("12", "R"), "65": ("4", "T"), "66": ("6", "R"), "67": ("7", "W"),
						"71": ("42", "V"), "73": ("46", "U"), "75": ("41", "W"), "77": ("35", "X"), "80": ("40", "Q"),
						"81": ("47", "Q"), "82": ("45", "T"), "85": ("5", "V"), "86": ("43", "W"), "95": ("35", "P"),
						"96": ("35", "O"), "99": ("4", "Z")
						}  # mapping: omw -> (yahoo, meteo)
		self.msnDescs = {
						"1": "SunnyDayV3", "2": "MostlySunnyDay", "3": "PartlyCloudyDayV3", "4": "MostlyCloudyDayV2",
						"5": "CloudyV3", "6": "BlowingHailV2", "7": "BlowingSnowV2", "8": "LightRainV2", "9": "FogV2",
						"10": "FreezingRainV2", "12": "HazySmokeV2", "14": "ModerateRainV2", "15": "HeavySnowV2",
						"16": "HailDayV2", "19": "LightRainV3", "17": "LightRainShowerDay", "20": "LightSnowV2",
						"22": "ModerateRainV2", "23": "RainShowersDayV2", "24": "RainSnowV2", "26": "SnowShowersDayV2",
						"27": "ThunderstormsV2", "28": "ClearNightV3", "29": "MostlyClearNight", "30": "PartlyCloudyNightV2",
						"31": "MostlyCloudyNightV2", "32": "ClouddyHazeSmokeNightV2_106", "39": "HazeSmokeNightV2_106",
						"43": "HailNightV2", "44": "LightRainShowerNight", "50": "RainShowersNightV2", "67": "ThunderstormsV2",
						"77": "RainSnowV2", "78": "RainSnowShowersNightV2", "82": "SnowShowersNightV2", "91": "WindyV2", "na": "NA"
			   			}
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
						"802": "scattered clouds: 25-50%", "803": "broken clouds: 51-84%", "804": "overcast clouds: 85-100%", "na": "not available"
						}
		self.omwDescs = {
						"0": "clear sky", "1": "mainly clear", "2": "partly cloudy", "3": "overcast", "45": "fog", "48": "depositing rime fog", "51": "light drizzle",
						"53": "moderate drizzle", "55": "dense intensity drizzle", "56": "light freezing drizzle", "57": "dense intensity freezing drizzle",
						"61": "slight rain", "63": "moderate rain", "65": "heavy intensity rain", "66": "light freezing rain", "67": "heavy intensity freezing rain",
						"71": "slight snow fall", "73": "moderate snow fall", "75": "heavy intensity snow fall", "77": "snow grains", "80": "slight rain showers",
						"81": "moderate rain showers", "82": "violent rain showers", "85": "slight snow showers", "86": "heavy snow showers",
						"95": "slight or moderate thunderstorm", "96": "thunderstorm with slight hail", "99": "thunderstorm with heavy hail"
						}
		self.yahooDescs = {
						"0": "tornado", "1": "tropical storm", "2": "hurricane", "3": "severe thunderstorms", "4": "thunderstorms", "5": "mixed rain and snow",
						"6": "mixed rain and sleet", "7": "mixed snow and sleet", "8": "freezing drizzle", "9": "drizzle", "10": "freezing rain",
						"11": "showers", "12": "showers", "13": "snow flurries", "14": "light snow showers", "15": "blowing snow", "16": "snow",
						"17": "hail", "18": "sleet", "19": "dust", "20": "foggy", "21": "haze", "22": "smoky", "23": "blustery", "24": "windy", "25": "cold",
						"26": "cloudy", "27": "mostly cloudy (night)", "28": "mostly cloudy (day)", "29": "partly cloudy (night)", "30": "partly cloudy (day)",
						"31": "clear (night)", "32": "sunny (day)", "33": "fair (night)", "34": "fair (day)", "35": "mixed rain and hail", "36": "hot",
						"37": "isolated thunderstorms", "38": "scattered thunderstorms", "39": "scattered thunderstorms", "40": "scattered showers",
						"41": "heavy snow", "42": "scattered snow showers", "43": "heavy snow", "44": "partly cloudy", "45": "thundershowers",
						"46": "snow showers", "47": "isolated thundershowers", "3200": "not available", "NA": "not available"
						}
		self.meteoDescs = {
						"!": "windy_rain_inv", "\"": "snow_inv", "#": "snow_heavy_inv", "$": "hail_inv", "%": "clouds_inv", "&": "clouds_flash_inv", "'": "temperature",
						"(": "compass", ")": "na", "*": "celcius", "+": "fahrenheit", "0": "clouds_flash_alt", "1": "sun_inv", "2": "moon_inv", "3": "cloud_sun_inv",
						"4": "cloud_moon_inv", "5": "cloud_inv", "6": "cloud_flash_inv", "7": "drizzle_inv", "8": "rain_inv", "9": "windy_inv", "A": "sunrise",
						"B": "sun", "C": "moon", "D": "eclipse", "E": "mist", "F": "wind", "G": "snowflake", "H": "cloud_sun", "I": "cloud_moon", "J": "fog_sun",
						"K": "fog_moon", "L": "fog_cloud", "M": "fog", "N": "cloud", "O": "cloud_flash", "P": "cloud_flash_alt", "Q": "drizzle", "R": "rain",
						"S": "windy", "T": "windy_rain", "U": "snow", "V": "snow_alt", "W": "snow_heavy", "X": "hail", "Y": "clouds", "Z": "clouds_flash"
						}
		self.error = None
		self.info = None
		self.mode = None
		self.parser = None
		self.geodata = None
		self.units = None
		self.callback = None
		self.reduced = False
		self.setmode(newmode, apikey)

	def setmode(self, newmode="msn", apikey=None):
		self.error = None
		newmode = newmode.lower()
		if newmode in self.SOURCES:
			if self.mode != newmode:
				self.mode = newmode
				if newmode == "msn":
					self.apikey = apikey
					self.parser = self.msnparser
				elif newmode == "owm":
					if not apikey:
						self.parser = None
						self.error = "[%s] ERROR in module 'setmode': API-Key for mode '%s' is missing!" % (MODULE_NAME, newmode)
						return self.error
					else:
						self.apikey = apikey
						self.parser = self.owmparser
				elif newmode == "omw":
					self.apikey = apikey
					self.parser = self.omwparser
			return
		else:
			self.parser = None
			self.error = "[%s] ERROR in module 'setmode': unknown mode '%s'" % (MODULE_NAME, newmode)
			return self.error

	def directionsign(self, degree):
		return "." if degree < 0 else ["↓ N", "↙ NE", "← E", "↖ SE", "↑ S", "↗ SW", "→ W", "↘ NW"][round(degree % 360 / 45 % 7.5)]

	def convert2icon(self, src, code):
		self.error = None
		if code is None:
			self.error = "[%s] ERROR in module 'convert2icon': input code value is 'None'" % MODULE_NAME
			return
		code = str(code).strip()
		if src is not None and src.lower() == "msn":
			common = self.msnCodes
		elif src is not None and src.lower() == "owm":
			common = self.owmCodes
		elif src is not None and src.lower() == "omw":
			common = self.omwCodes
		else:
			self.error = "[%s] ERROR in module 'convert2icon': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, self.SOURCES)
			return
		result = dict()
		if code in common:
			result["yahooCode"] = common[code][0]
			result["meteoCode"] = common[code][1]
		else:
			result["yahooCode"] = "NA"
			result["meteoCode"] = "NA"
			self.error = "[%s] ERROR in module 'convert2icon': key '%s' not found in converting dicts." % (MODULE_NAME, code)
			return
		return result

	def getCitylist(self, cityname=None, scheme="de-de"):
		self.error = None
		if not cityname:
			self.error = "[%s] ERROR in module 'getCitylist': missing cityname." % MODULE_NAME
			return

		if self.mode == "msn":
			apicode = "454445433343423734434631393042424245323644463739333846334439363145393235463539333"
			apikey = bytes.fromhex(apicode[:-1]).decode('utf-8')
			linkcode = "68747470733a2f2f7777772e62696e672e636f6d2f6170692f76362f506c616365732f4175746f537567676573743f61707069643d257326636f756e743d313526713d2573267365746d6b743d2573267365746c616e673d25737"
			link = bytes.fromhex(linkcode[:-1]).decode('utf-8') % (apikey, cityname, scheme, scheme)
			jsonData = self.apiserver(link)
			if not jsonData:
				self.error = "[%s] ERROR in module 'getCitylist': city '%s' not found on server, continue with '%s'." % (MODULE_NAME, cityname)
				return [cityname]
			citylist = []
			count = 0
			try:
				for hit in jsonData["value"]:
					if hit["_type"] in ["Place", "LocalBusiness"]:
						count += 1
						if count > 9:
							break
						cityname = hit["name"] if "name" in hit else hit["address"]["text"]
						state = ""
						country = ""
						citylist.append((cityname + state + country, 0, 0))
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitylist': general error. %s" % (MODULE_NAME, str(err))

		elif self.mode == "owm":
			special = {"br": "pt_br", "se": "sv, se", "es": "sp, es", "ua": "ua, uk", "cn": "zh_cn"}
			if scheme[:2] in special:
				scheme = special[scheme[:2]]
			items = cityname.split(",")
			cityname = "".join(items[:-1]).strip() if len(items) > 1 else items[0]
			country = "".join(items[-1:]).strip().upper() if len(items) > 1 else None
			link = "http://api.openweathermap.org/geo/1.0/direct?q=%s,%s&lang=%s&limit=15&appid=%s" % (cityname, country, scheme[:2], self.apikey)
			jsonData = self.apiserver(link)
			if not jsonData:
				self.error = "[%s] ERROR in module 'getCitylist': no city '%s' found." % (MODULE_NAME, cityname)
				return
			count = 0
			citylist = []
			try:
				for hit in jsonData:
					count += 1
					if count > 9:
						break
					cityname = hit["local_names"][scheme[:2]] if "local_names" in hit and scheme[:2] in hit["local_names"] else hit["name"]
					state = ", " + hit["state"] if "state" in hit else ""
					country = ", " + hit["country"].upper() if "country" in hit else ""
					citylist.append(("%s%s%s" % (cityname, state, country), hit["lon"], hit["lat"]))
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitylist': general error. %s" % (MODULE_NAME, str(err))
				return

		elif self.mode == "omw":
			items = cityname.split(",")
			cityname = "".join(items[:-1]).strip() if len(items) > 1 else items[0]
			country = "".join(items[-1:]).strip().upper() if len(items) > 1 else None
			link = "https://nominatim.openstreetmap.org/search?format=json&limit=10&city=%s" % cityname
			jsonData = self.apiserver(link)
			if not jsonData:
				self.error = "[%s] ERROR in module 'getCitylist': no city '%s' found." % (MODULE_NAME, cityname)
				return
			count = 0
			citylist = []
			try:
				for hit in jsonData:
					count += 1
					if count > 9:
						break
					items = hit["display_name"].split(", ")
					cityname = "%s, %s" % (items[0], items[1]) if len(items) > 1 else "%s" % items[0]
					if len(items) > 2:
						cityname = "%s, %s" % (cityname, items[-1])
					citylist.append(("%s" % cityname, hit["lon"], hit["lat"]))
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitylist': general error. %s" % (MODULE_NAME, str(err))
				return

		else:
			self.error = "[%s] ERROR in module 'start': unknown mode." % MODULE_NAME
			return
		return citylist

	def start(self, geodata=None, cityID=None, units="metric", scheme="de-de", callback=None, reduced=False):
		self.error = None
		self.geodata = ("", 0, 0) if geodata is None else geodata
		self.cityID = cityID
		self.units = units.lower()
		self.scheme = scheme.lower()
		self.callback = callback
		self.reduced = reduced
		if self.mode == "msn" and not self.geodata[0]:
			self.error = "[%s] ERROR in module 'start': missing cityname for mode 'msn'." % MODULE_NAME
		elif self.mode == "owm" and (not self.geodata[1] or not self.geodata[2]) and cityID is None:
			self.error = "[%s] ERROR in module 'start': missing geodata for mode 'owm'." % MODULE_NAME
		else:
			if self.mode not in self.SOURCES:
				self.error = "[%s] ERROR in module 'start': unknown mode '%s'." % (MODULE_NAME, self.mode)
		if callback:
			if self.error:
				callback(None, self.error)
			else:
				callInThread(self.parser)
		else:
			if self.error:
				return
			info = self.parser()
			return None if self.error else info

	def stop(self):
		self.error = None
		self.callback = None

	def msnparser(self):
		self.error = None
		self.info = None
		# some pre-defined localized URLs
		localisation = {"de-de": "de-de/wetter/vorhersage/", "it-it": "it-it/meteo/previsioni/", "cs-cz": "cs-cz/pocasi/predpoved/",
						"pl-pl": "pl-pl/pogoda/prognoza/", "pt-pt": "pt-pt/meteorologia/previsao/", "es-es": "es-es/eltiempo/prevision/",
						"fr-fr": "fr-fr/meteo/previsions/", "da-dk": "da-dk/vejr/vejrudsigt/", "sv-se": "sv-se/vader/prognos/",
						"fi-fi": "fi-fi/saa/ennuste/", "nb-no": "nb-no/weather/vaermelding/", "tr-tr": "tr-tr/havaduroldumu/havadurumutahmini/",
						"el-gr": "el-gr/weather/forecast/", "ru-xl": "ru-xl/weather/forecast/", "ar-sa": "ar-sa/weather/forecast/",
						"ja-jp": "ja-jp/weather/forecast/", "ko-kr": "ko-kr/weather/forecast/", "th-th": "th-th/weather/forecast/",
						"vi-vn": "vi-vn/weather/forecast/"
						}
		link = "http://www.msn.com/%s" % localisation.get(self.scheme, "en-us/weather/forecast/")  # fallback to general localized url
		degunit = "F" if self.units == "imperial" else "C"
		if self.callback is not None:
			print("[%s] accessing MSN for weatherdata..." % MODULE_NAME)
		link += "in-%s?weadegreetype=%s" % (quote(self.geodata[0]), degunit)
		try:
			response = get(link)
			response.raise_for_status()
		except exceptions.RequestException as err:
			self.error = "[%s] ERROR in module 'apiserver': '%s" % (MODULE_NAME, str(err))
			if self.callback:
				self.callback(None, self.error)
			return
		if self.callback:
			print("[%s] accessing MSN successful." % MODULE_NAME)
		try:
			output = response.content.decode("utf-8")
			startpos = output.find('</style>')
			endpos = output.find('</script></div>')
			bereich = output[startpos:endpos]
			todayData = search('<div class="iconTempPartContainer-E1_1"><img class="iconTempPartIcon-E1_1" src="(.*?)" title="(.*?)"/></div>', bereich)
			svgsrc = todayData.group(1) if todayData else "N/A"
			svgdesc = todayData.group(2) if todayData else "N/A"
			svgdata = findall('<img class="iconTempPartIcon-E1_1" src="(.*?)" title="(.*?)"/></div>', bereich)
			# Create DICT "jsonData" from JSON-string and add some useful infos
			start = '<script id="redux-data" type="application/json">'
			startpos = output.find(start)
			endpos = output.find("</script>", startpos)
			output = output[startpos + len(start):endpos].split("; ")
			if len(output):
				jsonData = None
				try:
					output = loads(output[0])
					jsonData = output["WeatherData"]["_@STATE@_"]
				except Exception as jsonerr:
					self.error = "[%s] ERROR in module 'msnparser': found invalid json-string. %s" % (MODULE_NAME, str(jsonerr))
				if jsonData:
					currdate = datetime.fromisoformat(jsonData["lastUpdated"])
					jsonData["currentCondition"]["deepLink"] = link  # replace by minimized link
					jsonData["currentCondition"]["date"] = currdate.strftime("%Y-%m-%d")  # add some missing info
					jsonData["currentCondition"]["image"]["svgsrc"] = svgsrc
					jsonData["currentCondition"]["image"]["svgdesc"] = svgdesc
					iconCode = self.convert2icon("MSN", self.msnPvdr[jsonData["currentCondition"]["pvdrIcon"]])
					if iconCode:
						jsonData["currentCondition"]["yahooCode"] = iconCode.get("yahooCode", "NA")
						jsonData["currentCondition"]["meteoCode"] = iconCode.get("meteoCode", ")")
						jsonData["currentCondition"]["day"] = currdate.strftime("%A")
						jsonData["currentCondition"]["shortDay"] = currdate.strftime("%a")
					for idx, forecast in enumerate(jsonData["forecast"][:-2]):  # last two entries are not usable
						forecast["deepLink"] = link + "&day=%s" % (idx + 1)  # replaced by minimized link
						forecast["date"] = (currdate + timedelta(days=idx)).strftime("%Y-%m-%d")
						if idx < len(svgdata):
							forecast["image"]["svgsrc"] = svgdata[idx][0]
							forecast["image"]["svgdesc"] = svgdata[idx][1]
						else:
							forecast["image"]["svgsrc"] = "N/A"
							forecast["image"]["svgdesc"] = "N/A"
						iconCodes = self.convert2icon("MSN", self.msnPvdr[forecast["pvdrIcon"]])
						if iconCodes:
							forecast["yahooCode"] = iconCodes.get("yahooCode", "NA")
							forecast["meteoCode"] = iconCodes.get("meteoCode", ")")
							forecast["day"] = (currdate + timedelta(days=idx)).strftime("%A")
							forecast["shortDay"] = (currdate + timedelta(days=idx)).strftime("%a")
					self.info = jsonData
				else:
					if self.callback:
						self.callback(None, self.error)
						return
			else:
				self.error = "[%s] ERROR in module 'msnparser': expected parsing data not found." % MODULE_NAME
		except Exception as err:
			self.error = "[%s] ERROR in module 'msnparser': general error. %s" % (MODULE_NAME, str(err))
		if self.callback:
			if self.error:
				self.callback(None, self.error)
			else:
				self.callback(self.getreducedinfo() if self.reduced else self.info, None)
		else:
			return self.info

	def writejson(self, filename):
		self.error = None
		if self.info:
			try:
				with open(filename, "w") as f:
					dump(self.info, f)
			except Exception as err:
				self.error = "[%s] ERROR in module 'msnparser': %s" % (MODULE_NAME, str(err))
		else:
			self.error = "[%s] ERROR in module 'writejson': no data found." % MODULE_NAME

	def getmsnxml(self):  # only MSN supported
		self.error = None
		try:
			root = Element("weatherdata")
			root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
			root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
			w = Element("weather")
			w.set("weatherlocationname", self.info["currentLocation"]["displayName"])
			w.set("url", self.info["currentCondition"]["deepLink"])
			w.set("degreetype", self.info["currentCondition"]["degreeSetting"][1:])
			w.set("long", self.info["currentLocation"]["longitude"])
			w.set("lat", self.info["currentLocation"]["latitude"])
			w.set("timezone", str(int(self.info["source"]["location"]["TimezoneOffset"][: 2])))
			w.set("alert", self.info["currentCondition"]["alertSignificance"])
			w.set("encodedlocationname", self.info["currentLocation"]["locality"].encode("ascii", "xmlcharrefreplace").decode().replace(" ", "%20").replace("\n", ""))
			root.append(w)
			c = Element("current")
			c.set("temperature", self.info["currentCondition"]["currentTemperature"])
			c.set("skycode", self.info["currentCondition"]["normalizedSkyCode"])
			c.set("skytext", self.info["currentCondition"]["skycode"]["children"])
			c.set("date", self.info["currentCondition"]["date"])
			c.set("svglink", self.info["currentCondition"]["image"]["svgsrc"])
			c.set("svgdesc", self.info["currentCondition"]["image"]["svgdesc"])
			c.set("yahoocode", self.info["currentCondition"]["yahooCode"])
			c.set("meteocode", self.info["currentCondition"]["meteoCode"])
			c.set("observationtime", self.info["lastUpdated"][11:19])
			c.set("observationpoint", self.info["currentLocation"]["locality"])
			c.set("feelslike", self.info["currentCondition"]["feels"].replace("°", ""))
			c.set("humidity", self.info["currentCondition"]["humidity"].replace("%", ""))
			c.set("winddisplay", "%s %s" % (self.info["currentCondition"]["windSpeed"], self.directionsign(self.info["currentCondition"]["windDir"])))
			c.set("day", self.info["forecast"][0]["dayTextLocaleString"])
			c.set("shortday", self.info["currentCondition"]["shortDay"])
			c.set("windspeed", self.info["currentCondition"]["windSpeed"])
			w.append(c)
			for forecast in self.info["forecast"][:-2]:  # last two entries are not usable
				f = Element("forecast")
				f.set("low", str(forecast["lowTemp"]))
				f.set("high", str(forecast["highTemp"]))
				f.set("skytextday", forecast["cap"])
				f.set("date", forecast["date"])
				f.set("svglink", forecast["image"]["svgsrc"])
				f.set("svgdesc", forecast["image"]["svgdesc"])
				f.set("yahoocode", forecast["yahooCode"])
				f.set("meteocode", forecast["meteoCode"])
				f.set("day", forecast["day"])
				f.set("shortday", forecast["shortDay"])
				f.set("precip", forecast["precipitation"])
				w.append(f)
			return root
		except Exception as err:
			self.error = "[%s] ERROR in module 'getmsnxml': general error. %s" % (MODULE_NAME, str(err))

	def writemsnxml(self, filename):  # only MSN supported
		self.error = None
		xmlData = self.getmsnxml()
		if xmlData:
			xmlstring = tostring(xmlData, encoding="utf-8", method="html")
			try:
				with open(filename, "wb") as f:
					f.write(xmlstring)
			except OSError as err:
				self.error = "[%s] ERROR in module 'msnparser': %s" % (MODULE_NAME, str(err))
		else:
			self.error = "[%s] ERROR in module 'writemsnxml': no xmldata found." % MODULE_NAME

	def apiserver(self, link):
		self.error = None
		if link:
			try:
				response = get(link)
				response.raise_for_status()
			except exceptions.RequestException as err:
				self.error = "[%s] ERROR in module 'apiserver': '%s" % (MODULE_NAME, str(err))
				return
			try:
				jsonData = loads(response.content)
				if jsonData:
					return jsonData
				self.error = "[%s] ERROR in module 'apiserver': owm-server access failed." % MODULE_NAME
			except Exception as err:
				self.error = "[%s] ERROR in module 'apiserver': invalid json data from OWM-server. %s" % (MODULE_NAME, str(err))
		else:
			self.error = "[%s] ERROR in module 'apiserver': missing link." % MODULE_NAME
		return

	def owmparser(self):
		self.error = None
		self.info = None
		if not self.apikey:
			self.error = "[%s] ERROR in module' owmparser': API-key is missing!" % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		if self.cityID:
			link = "http://api.openweathermap.org/data/2.5/forecast?id=%s&units=%s&lang=%s&appid=%s" % (self.cityID, self.units, self.scheme[:2], self.apikey)
		elif self.geodata:
			link = "https://api.openweathermap.org/data/2.5/forecast?&lon=%s&lat=%s&units=%s&lang=%s&appid=%s" % (self.geodata[1], self.geodata[2], self.units, self.scheme[:2], self.apikey)
		else:
			self.error = "[%s] ERROR in module 'owmparser': missing geodata or cityID." % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		if self.callback:
			print("[%s] accessing OWM for weatherdata..." % MODULE_NAME)
		jsonData = self.apiserver(link)
		if jsonData and self.error is None:
			if self.callback:
				print("[%s] accessing OWM successful." % MODULE_NAME)
			try:
				if self.cityID:
					jsonData["requested"] = dict()  # add some missing info
					jsonData["requested"]["cityName"] = jsonData["city"]["name"]
					jsonData["requested"]["lon"] = jsonData["city"]["coord"]["lon"]
					jsonData["requested"]["lat"] = jsonData["city"]["coord"]["lat"]
				else:
					jsonData["requested"] = dict()  # add some missing info
					jsonData["requested"]["cityName"] = self.geodata[0]
					jsonData["requested"]["lon"] = self.geodata[1]
					jsonData["requested"]["lat"] = self.geodata[2]
				for period in jsonData["list"]:
					timestamp = period["dt"]
					period["day"] = datetime.fromtimestamp(timestamp).strftime("%A")
					period["shortDay"] = datetime.fromtimestamp(timestamp).strftime("%a")
					iconCode = self.convert2icon("OWM", period["weather"][0]["id"])
					if iconCode:
						period["weather"][0]["yahooCode"] = iconCode.get("yahooCode", "NA")
						period["weather"][0]["meteoCode"] = iconCode.get("meteoCode", ")")
			except Exception as err:
				self.error = "[%s] ERROR in module 'owmparser': general error. %s" % (MODULE_NAME, str(err))
				jsonData = None
			self.info = jsonData
		if self.callback:
			if self.error:
				self.callback(None, self.error)
			else:
				self.callback(self.getreducedinfo() if self.reduced else self.info, self.error)
		else:
			return self.getreducedinfo() if self.reduced else self.info

	def omwparser(self):
		self.error = None
		self.info = None
		windunit = "mph" if self.units == "imperial" else "kmh"
		tempunit = "fahrenheit" if self.units == "imperial" else "celsius"
		timezones = {"-06": "America/Anchorage", "-05": "America/Los_Angeles", "-04": "America/Denver", "-03": "America/Chicago", "-02": "America/New_York",
	  				"-01": "America/Sao_Paulo", "+00": "Europe/London", "+01": "Europe/Berlin", "+02": "Europe/Moscow", "+03": "Africa/Cairo",
		  			"+04": "Asia/Bangkok", "+05": "Asia/Singapore", "+06": "Asia/Tokyo", "+07": "Australia/Sydney", "+08": "Pacific/Auckland"}
		currzone = timezones.get(datetime.now(timezone.utc).astimezone().isoformat()[26:29], "Europe/Berlin")
		if self.geodata:
			link = "https://api.open-meteo.com/v1/forecast?longitude=%s&latitude=%s&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,weathercode,windspeed_10m,winddirection_10m&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=%s&windspeed_unit=%s&temperature_unit=%s" % (float(self.geodata[1]), float(self.geodata[2]), currzone, windunit, tempunit)
		else:
			self.error = "[%s] ERROR in module 'omwparser': missing geodata." % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		if self.callback:
			print("[%s] accessing OMW for weatherdata..." % MODULE_NAME)
		jsonData = self.apiserver(link)
		if jsonData and self.error is None:
			if self.callback:
				print("[%s] accessing OMW successful." % MODULE_NAME)
			try:
				jsonData["requested"] = dict()  # add some missing info
				jsonData["requested"]["cityName"] = self.geodata[0]
				jsonData["requested"]["lon"] = self.geodata[1]
				jsonData["requested"]["lat"] = self.geodata[2]
				jsonData["hourly"]["yahooCode"] = dict()
				jsonData["hourly"]["meteoCode"] = dict()
				for idx in range(len(jsonData["hourly"]["time"])):
					iconCode = self.convert2icon("OMW", jsonData["hourly"]["weathercode"][idx])
					if iconCode:
						jsonData["hourly"]["yahooCode"][idx] = iconCode.get("yahooCode", "NA")
						jsonData["hourly"]["meteoCode"][idx] = iconCode.get("meteoCode", ")")
				jsonData["daily"]["day"] = dict()
				jsonData["daily"]["shortDay"] = dict()
				jsonData["daily"]["yahooCode"] = dict()
				jsonData["daily"]["meteoCode"] = dict()
				for idx, forecast in enumerate(jsonData["daily"]["time"]):
					currdate = datetime.fromisoformat(forecast)
					jsonData["daily"]["day"][idx] = currdate.strftime("%A")
					jsonData["daily"]["shortDay"][idx] = currdate.strftime("%a")
					iconCode = self.convert2icon("OMW", jsonData["daily"]["weathercode"][idx])
					if iconCode:
						jsonData["daily"]["yahooCode"][idx] = iconCode.get("yahooCode", "NA")
						jsonData["daily"]["meteoCode"][idx] = iconCode.get("meteoCode", ")")
			except Exception as err:
				self.error = "[%s] ERROR in module 'omwparser': general error. %s" % (MODULE_NAME, str(err))
				jsonData = None
			self.info = jsonData
		if self.callback:
			if self.error:
				self.callback(None, self.error)
			else:
				self.callback(self.getreducedinfo() if self.reduced else self.info, self.error)
		else:
			return self.getreducedinfo() if self.reduced else self.info

	def getCitybyID(self, cityID=None):
		self.error = None
		if self.mode != "owm":
			self.error = "[%s] ERROR in module 'getCitybyID': unsupported mode '%s', only mode 'owm' is supported" % (MODULE_NAME, self.mode)
			return
		if not cityID:
			self.error = "[%s] ERROR in module 'getCitybyID': missing cityID" % MODULE_NAME
			return
		link = "http://api.openweathermap.org/data/2.5/forecast?id=%s&cnt=1&appid=%s" % (cityID, self.apikey)
		if self.callback:
			print("[%s] accessing OWM for cityID..." % MODULE_NAME)
		jsonData = self.apiserver(link)
		if jsonData:
			if self.callback:
				print("[%s] accessing OWM successful." % MODULE_NAME)
			try:
				cityData = jsonData.get("city", {})
				cityname = cityData.get("name", "N/A")
				lon = cityData.get("coord", {}).get("lon", "N/A")
				lat = cityData.get("coord", {}).get("lat", "N/A")
				return (cityname, lon, lat)
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitybyID': general error. %s" % (MODULE_NAME, str(err))
				return
		else:
			self.error = "[%s] ERROR in module 'getCitybyID': no city found" % MODULE_NAME

	def getCitylistbyGeocode(self, geocode=None, scheme="de-de"):
		self.error = None
		if geocode:
			lon = geocode.split(",")[0].strip()
			lat = geocode.split(",")[1].strip()
		else:
			lon = None
			lat = None
		if not self.mode.startswith("owm"):
			self.error = "[%s] ERROR in module 'getCitylistbyGeocode': unsupported mode '%s', only mode 'owm' is supported" % (MODULE_NAME, self.mode)
			return
		if not lon or not lat:
			self.error = "[%s] ERROR in module 'getCitylistbyGeocode': incomplete or missing coordinates" % MODULE_NAME
			return
		link = "http://api.openweathermap.org/geo/1.0/reverse?lon=%s&lat=%s&limit=15&appid=%s" % (lon, lat, self.apikey)
		if self.callback:
			print("[%s] accessing OWM for coordinates..." % MODULE_NAME)
		jsonData = self.apiserver(link)
		if jsonData:
			if self.callback:
				print("[%s] accessing OWM successful." % MODULE_NAME)
			try:
				citylist = []
				for hit in jsonData:
					cityname = hit["local_names"][scheme[:2]] if "local_names" in hit and scheme[:2] in hit["local_names"] else hit["name"]
					state = ", %s" % hit["state"] if "state" in hit else ""
					country = ", %s" % hit["country"].upper() if "country" in hit else ""
					citylist.append((cityname + state + country, hit.get("lon", "N/A"), hit.get("lat", "N/A")))
				return citylist
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitylistbyCoords': general error. %s" % (MODULE_NAME, str(err))
				return
		else:
			self.error = "[%s] ERROR in module 'getCitylistbyCoords': no data." % MODULE_NAME

	def getreducedinfo(self):
		self.error = None
		reduced = dict()
		if self.info:
			if self.parser is not None and self.mode == "msn":
				try:
					current = self.info["currentCondition"]  # current weather
					reduced["source"] = "MSN Weather"
					reduced["name"] = self.info["currentLocation"]["displayName"]
					reduced["longitude"] = self.info["currentLocation"]["longitude"]
					reduced["latitude"] = self.info["currentLocation"]["latitude"]
					reduced["current"] = dict()
					reduced["current"]["observationTime"] = self.info["lastUpdated"]
					reduced["current"]["yahooCode"] = current["yahooCode"]
					reduced["current"]["meteoCode"] = current["meteoCode"]
					reduced["current"]["temp"] = current["currentTemperature"]
					reduced["current"]["feelsLike"] = current["feels"].replace("°", "").strip()
					reduced["current"]["humidity"] = current["humidity"].replace("%", "").strip()
					reduced["current"]["windSpeed"] = current["windSpeed"].replace("km/h", "").replace("mph", "").strip()
					windDir = current["windDir"]
					reduced["current"]["windDir"] = str(windDir)
					reduced["current"]["windDirSign"] = self.directionsign(windDir)
					date = current["date"]
					reduced["current"]["day"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%A")
					reduced["current"]["shortDay"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%a")
					reduced["current"]["date"] = date
					reduced["current"]["text"] = current["shortCap"]
					reduced["current"]["minTemp"] = str(self.info["forecast"][0]["lowTemp"])
					reduced["current"]["maxTemp"] = str(self.info["forecast"][0]["highTemp"])
					forecast = self.info["forecast"]
					reduced["forecast"] = dict()
					for idx in range(6):  # forecast of today and next 5 days
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = forecast[idx]["yahooCode"]
						reduced["forecast"][idx]["meteoCode"] = forecast[idx]["meteoCode"]
						reduced["forecast"][idx]["minTemp"] = str(forecast[idx]["lowTemp"])
						reduced["forecast"][idx]["maxTemp"] = str(forecast[idx]["highTemp"])
						date = forecast[idx]["date"]
						reduced["forecast"][idx]["day"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%A")
						reduced["forecast"][idx]["shortDay"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%a")
						reduced["forecast"][idx]["date"] = forecast[idx]["date"]
						reduced["forecast"][idx]["text"] = forecast[idx]["cap"]
				except Exception as err:
					self.error = "[%s] ERROR in module 'getreducedinfo': general error. %s" % (MODULE_NAME, str(err))
					return

			elif self.parser is not None and self.mode == "owm":
				try:
					current = self.info["list"][0]  # collect current weather data
					reduced["source"] = "OWM Weather"
					reduced["name"] = self.info["requested"]["cityName"]
					reduced["longitude"] = str(self.info["requested"]["lon"])
					reduced["latitude"] = str(self.info["requested"]["lat"])
					reduced["current"] = dict()
					isotime = datetime.now(timezone.utc).astimezone().isoformat()
					reduced["current"]["observationTime"] = "%s%s" % (isotime[:19], isotime[26:])
					reduced["current"]["yahooCode"] = current["weather"][0]["yahooCode"]
					reduced["current"]["meteoCode"] = current["weather"][0]["meteoCode"]
					reduced["current"]["temp"] = str(round(current["main"]["temp"]))
					reduced["current"]["feelsLike"] = str(round(current["main"]["feels_like"]))
					reduced["current"]["humidity"] = str(round(current["main"]["humidity"]))
					reduced["current"]["windSpeed"] = str(round(current["wind"]["speed"]))
					windDir = current["wind"]["deg"]
					reduced["current"]["windDir"] = str(windDir)
					reduced["current"]["windDirSign"] = self.directionsign(int(windDir))
					reduced["current"]["day"] = current["day"]
					reduced["current"]["shortDay"] = current["shortDay"]
					reduced["current"]["date"] = datetime.fromtimestamp(current["dt"]).strftime("%Y-%m-%d")
					reduced["current"]["text"] = current["weather"][0]["description"]
					tmin = 88  # init for today
					tmax = -88
					yahoocode = None
					meteocode = None
					text = None
					idx = 0
					reduced["forecast"] = dict()
					for forecast in self.info["list"]:
						tmin = min(tmin, forecast["main"]["temp_min"])
						tmax = max(tmax, forecast["main"]["temp_max"])
						if "15:00:00" in forecast["dt_txt"]:  # get weather icon as a representative icon for current day
							yahoocode = forecast["weather"][0]["yahooCode"]
							meteocode = forecast["weather"][0]["meteoCode"]
							text = forecast["weather"][0]["description"]
						if "18:00:00" in forecast["dt_txt"]:  # in case we call the forecast late today: get current weather icon
							yahoocode = yahoocode if yahoocode else forecast["weather"][0]["yahooCode"]
							meteocode = meteocode if meteocode else forecast["weather"][0]["meteoCode"]
							text = text if text else forecast["weather"][0]["description"]
						if "21:00:00" in forecast["dt_txt"]:  # last available data before daychange
							reduced["forecast"][idx] = dict()
							reduced["forecast"][idx]["yahooCode"] = yahoocode if yahoocode else forecast["weather"][0]["yahooCode"]
							reduced["forecast"][idx]["meteoCode"] = meteocode if meteocode else forecast["weather"][0]["meteoCode"]
							reduced["forecast"][idx]["minTemp"] = str(round(tmin))
							reduced["forecast"][idx]["maxTemp"] = str(round(tmax))
							reduced["forecast"][idx]["day"] = forecast["day"]
							reduced["forecast"][idx]["shortDay"] = forecast["shortDay"]
							reduced["forecast"][idx]["date"] = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
							reduced["forecast"][idx]["text"] = forecast["weather"][0]["description"]
							tmin = 88  # inits for next day
							tmax = -88
							yahoocode = None
							meteocode = None
							text = None
							idx += 1
					if idx == 5 and "21:00:00" in forecast["dt_txt"]:  # in case day #5 is missing: create a copy of day 4 (=fake)
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = yahoocode if yahoocode else reduced["forecast"][idx - 1]["yahooCode"]
						reduced["forecast"][idx]["meteoCode"] = meteocode if meteocode else reduced["forecast"][idx - 1]["meteoCode"]
						reduced["forecast"][idx]["minTemp"] = str(round(tmin)) if tmin != 88 else reduced["forecast"][idx - 1]["minTemp"]
						reduced["forecast"][idx]["maxTemp"] = str(round(tmax)) if tmax != - 88 else reduced["forecast"][idx - 1]["maxTemp"]
						nextdate = datetime.strptime(reduced["forecast"][idx - 1]["date"], "%Y-%m-%d") + timedelta(1)
						reduced["forecast"][idx]["day"] = nextdate.strftime("%A")
						reduced["forecast"][idx]["shortDay"] = nextdate.strftime("%a")
						reduced["forecast"][idx]["date"] = nextdate.strftime("%Y-%m-%d")
						reduced["forecast"][idx]["text"] = text if text else reduced["forecast"][idx - 1]["text"]
					elif idx == 5:  # in case day #5 is incomplete: use what we have
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = yahoocode if yahoocode else forecast["weather"][0]["yahooCode"]
						reduced["forecast"][idx]["meteoCode"] = meteocode if meteocode else forecast["weather"][0]["meteoCode"]
						reduced["forecast"][idx]["minTemp"] = str(round(tmin)) if tmin != 88 else reduced["forecast"][idx - 1]["minTemp"]
						reduced["forecast"][idx]["maxTemp"] = str(round(tmax)) if tmax != - 88 else reduced["forecast"][idx - 1]["maxTemp"]
						reduced["forecast"][idx]["day"] = forecast["day"]
						reduced["forecast"][idx]["shortDay"] = forecast["shortDay"]
						reduced["forecast"][idx]["date"] = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
						reduced["forecast"][idx]["text"] = text if text else reduced["forecast"][idx - 1]["text"]
					reduced["current"]["minTemp"] = reduced["forecast"][0]["minTemp"]  # missing data for today are added
					reduced["current"]["maxTemp"] = reduced["forecast"][0]["maxTemp"]
				except Exception as err:
					self.error = "[%s] ERROR in module 'getreducedinfo': general error. %s" % (MODULE_NAME, str(err))
					return

			elif self.parser is not None and self.mode == "omw":
				try:
					reduced["source"] = "O-M Weather"
					reduced["name"] = self.info["requested"]["cityName"]
					reduced["longitude"] = str(self.info["longitude"])
					reduced["latitude"] = str(self.info["latitude"])
					isotime = "%s%s" % (datetime.now(timezone.utc).astimezone().isoformat()[:14], "00")
					reduced["current"] = dict()
					for idx, current in enumerate(self.info["hourly"]["time"]):
						if isotime in current:
							isotime = datetime.now(timezone.utc).astimezone().isoformat()
							reduced["current"]["observationTime"] = "%s%s" % (isotime[:19], isotime[26:])
							reduced["current"]["yahooCode"] = self.info["hourly"]["yahooCode"][idx]
							reduced["current"]["meteoCode"] = self.info["hourly"]["meteoCode"][idx]
							reduced["current"]["temp"] = str(round(self.info["hourly"]["temperature_2m"][idx]))
							reduced["current"]["feelsLike"] = str(round(self.info["hourly"]["apparent_temperature"][idx]))
							reduced["current"]["humidity"] = str(round(self.info["hourly"]["relativehumidity_2m"][idx]))
							reduced["current"]["windSpeed"] = str(round(self.info["hourly"]["windspeed_10m"][idx]))
							windDir = self.info["hourly"]["winddirection_10m"][idx]
							reduced["current"]["windDir"] = str(windDir)
							reduced["current"]["windDirSign"] = self.directionsign(windDir)
							reduced["current"]["day"] = datetime(int(current[:4]), int(current[5:7]), int(current[8:10])).strftime("%A")
							reduced["current"]["shortDay"] = datetime(int(current[:4]), int(current[5:7]), int(current[8:10])).strftime("%a")
							reduced["current"]["date"] = current[:10]
							reduced["current"]["text"] = "N/A"
							reduced["current"]["minTemp"] = str(round(self.info["daily"]["temperature_2m_min"][0]))
							reduced["current"]["maxTemp"] = str(round(self.info["daily"]["temperature_2m_max"][0]))
							break
					reduced["forecast"] = dict()
					for idx in range(6):  # forecast of today and next 5 days
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = self.info["daily"]["yahooCode"][idx]
						reduced["forecast"][idx]["meteoCode"] = self.info["daily"]["meteoCode"][idx]
						reduced["forecast"][idx]["maxTemp"] = str(round(self.info["daily"]["temperature_2m_max"][idx]))
						reduced["forecast"][idx]["minTemp"] = str(round(self.info["daily"]["temperature_2m_min"][idx]))
						date = self.info["daily"]["time"][idx]
						reduced["forecast"][idx]["day"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%A")
						reduced["forecast"][idx]["shortDay"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%a")
						reduced["forecast"][idx]["date"] = date
						reduced["forecast"][idx]["text"] = "N/A"
				except Exception as err:
					self.error = "[%s] ERROR in module 'getreducedinfo': general error. %s" % (MODULE_NAME, str(err))
					return

			else:
				self.error = "[%s] ERROR in module 'getreducedinfo': unknown source." % MODULE_NAME
				return
		return reduced

	def writereducedjson(self, filename):
		self.error = None
		reduced = self.getreducedinfo()
		if self.error is not None:
			return
		if reduced is None:
			self.error = "[%s] ERROR in module 'writereducedjson': no data found." % MODULE_NAME
			return
		with open(filename, "w") as f:
			dump(reduced, f)
		return filename

	def getinfo(self):
		self.error = None
		if self.ready is None:
			self.error = "[%s] ERROR in module 'getinfo': Parser not ready" % MODULE_NAME
			return
		return self.info

	def showDescription(self, src):
		self.error = None
		if src is not None and src.lower() == "msn":
			descs = self.msnDescs
		elif src is not None and src.lower() == "owm":
			descs = self.owmDescs
		elif src is not None and src.lower() == "omw":
			descs = self.omwDescs
		elif src is not None and src.lower() == "yahoo":
			descs = self.yahooDescs
		elif src is not None and src.lower() == "meteo":
			descs = self.meteoDescs
		else:
			self.error = "[%s] ERROR in module 'showDescription': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, self.SOURCES)
			return self.error
		print("+%s+" % ("-" * 38))
		print("| {0:<5}{1:<31} |".format("CODE", "DESCRIPTION_%s (COMPLETE)" % src.upper()))
		print("+%s+" % ("-" * 38))
		for desc in descs:
			print("| {0:<5}{1:<31} |".format(desc, descs[desc]))
		print("+%s+\n" % ("-" * 38))
		return

	def showConvertrules(self, src, dest):
		self.error = None
		if not src:
			self.error = "[%s] ERROR in module 'showConvertrules': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, self.SOURCES)
			return self.error
		if dest is not None and dest.lower() == "meteo":
			ddescs = self.meteoDescs
		elif dest is not None and dest.lower() == "yahoo":
			ddescs = self.yahooDescs
		else:
			self.error = "[%s] ERROR in module 'showConvertrules': convert destination '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, self.DESTINATIONS)
			return self.error
		destidx = self.DESTINATIONS.index(dest)
		print("+%s+%s+" % ("-" * 40, "-" * 32))
		if src.lower() == "msn":
			print("| {0:<3} -> {1:<4}{2:<27} | {3:<5}{4:<25} |".format("PVD", "MSN", "DESCRIPTION_%s (CONVERTER)" % src.upper(), "CODE", "DESCRIPTION_%s" % dest.upper()))
			print("+%s+%s+" % ("-" * 40, "-" * 32))
			for scode in self.msnPvdr:
				dcode = self.msnCodes[self.msnPvdr[scode]][destidx]
				print("| {0:<3} -> {1:<4}{2:<27} | {3:<5}{4:<25} |".format(scode, self.msnPvdr[scode], self.msnDescs[self.msnPvdr[scode]], dcode, ddescs[dcode]))
		elif src.lower() == "owm":
			print("| {0:<5}{1:<33} | {2:<5}{3:<25} |".format("CODE", "DESCRIPTION_%s (CONVERTER)" % src.upper(), "CODE", "DESCRIPTION_%s" % dest.upper()))
			print("+%s+%s+" % ("-" * 40, "-" * 32))
			for scode in self.owmCodes:
				dcode = self.owmCodes[scode][destidx]
				print("| {0:<5}{1:<33} | {2:<5}{3:<25} |".format(scode, self.owmDescs[scode], dcode, ddescs[dcode]))
		elif src.lower() == "omw":
			print("| {0:<5}{1:<33} | {2:<5}{3:<25} |".format("CODE", "DESCRIPTION_%s (CONVERTER)" % src.upper(), "CODE", "DESCRIPTION_%s" % dest.upper()))
			print("+%s+%s+" % ("-" * 40, "-" * 32))
			for scode in self.omwCodes:
				dcode = self.omwCodes[scode][destidx]
				print("| {0:<5}{1:<33} | {2:<5}{3:<25} |".format(scode, self.omwDescs[scode], dcode, ddescs[dcode]))
		else:
			self.error = "[%s] ERROR in module 'showConvertrules': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, self.SOURCES)
			return self.error
		print("+%s+%s+\n" % ("-" * 40, "-" * 32))
		return


def main(argv):
	cityname = ""
	units = "metric"
	scheme = "de-de"
	mode = "msn"
	apikey = None
	quiet = False
	json = None
	reduced = False
	xml = None
	specialopt = None
	control = False
	cityID = None
	geocode = None
	geodata = None
	helpstring = "Weatherinfo v1.3: try 'Weatherinfo -h' for more information"
	try:
		opts, args = getopt(argv, "hqm:a:j:r:x:s:u:i:g:c", ["quiet =", "mode=", "apikey=", "json =", "reduced =", "xml =", "scheme =", "units =", "id =", "geocode =", "control ="])
	except GetoptError:
		print(helpstring)
		exit(2)
	for opt, arg in opts:
		opt = opt.lower().strip()
		arg = arg.lower().strip()
		if opt == "-h":
			print("Usage: Weatherinfo [options...] <cityname>\n"
			"-m, --mode <data>\t\tValid modes: 'omw', 'owm' or 'msn' {'msn' is default}\n"
			"-a, --apikey <data>\t\tAPI-key required for 'owm' only\n"
			"-j, --json <filename>\t\tFile output formatted in JSON (all modes)\n"
			"-r, --reduced <filename>\tFile output formatted in JSON (minimum infos only)\n"
			"-x, --xml <filename>\t\tFile output formatted in XML (mode 'msn' only)\n"
			"-s, --scheme <data>\t\tCountry scheme (not used by 'omw') {'de-de' is default}\n"
			"-u, --units <data>\t\tValid units: 'imperial' or 'metric' {'metric' is default}\n"
			"-i, --id <cityID>\t\tGet cityname by owm's DEPRECATED cityID ('owm' only)\n"
			"-g, --geocode <lon/lat>\t\tGet cityname by 'longitude,latitude' ('owm' only)\n"
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
		elif opt in ("-x", "--xml"):
			xml = arg
		elif opt in ("-s", "--scheme"):
			scheme = arg
		elif opt in ("-m", "--mode"):
			if arg in ["msn", "owm", "omw"]:
				mode = arg
			else:
				print("ERROR: mode '%s' is invalid. Valid parameters: 'msn', 'omw' or 'owm'" % arg)
				exit()
		elif opt in ("-a", "--apikey"):
			apikey = arg
		elif opt in ("-i", "--id"):
			cityID = arg
			specialopt = True
		elif opt in ("-g", "--geocode"):
			geocode = arg.split(",")
			geodata = ("", geocode[0], geocode[1])
			specialopt = True
		elif opt in ("-c", "control"):
			control = True
			specialopt = True
		elif opt in ("-q", "--quiet"):
			quiet = True
			specialopt = True
	if len(args) == 0 and not specialopt:
		print(helpstring)
		exit()
	for part in args:
		cityname += part + " "
	cityname = cityname.strip()
	if len(cityname) < 3 and not specialopt:
		print("ERROR: Cityname too short, please use at least 3 letters!")
		exit()
	WI = Weatherinfo(mode, apikey)
	if control:
		for src in WI.SOURCES + WI.DESTINATIONS:
			if WI.showDescription(src):
				print(WI.error.replace("[__main__]", "").strip())
		for src in WI.SOURCES:
			for dest in WI.DESTINATIONS:
				if WI.showConvertrules(src, dest):
					print(WI.error.replace("[__main__]", "").strip())
		exit()
	if WI.error:
		print(WI.error.replace("[__main__]", "").strip())
		exit()
	if cityname and not geocode:
		citylist = WI.getCitylist(cityname, scheme)
		if WI.error:
			print(WI.error.replace("[__main__]", "").strip())
			exit()
		if len(citylist) == 0:
			print("No cites found. Try another wording.")
			exit()
		geodata = citylist[0]
		if citylist and len(citylist) > 1 and not quiet:
			print("Found the following cities/areas:")
			for idx, item in enumerate(citylist):
				lon = " [lon=%s" % item[1] if item[1] != 0.0 else ""
				lat = ", lat=%s]" % item[2] if item[2] != 0.0 else ""
				print("%s = %s%s%s" % (idx + 1, item[0], lon, lat))
			choice = input("Select (1-%s)? : " % len(citylist))[:1]
			index = ord(choice) - 48 if len(choice) > 0 else -1
			if index > 0 and index < len(citylist) + 1:
				geodata = citylist[index - 1]
			else:
				print("Choice '%s' is not allowable (only numbers 1 to %s are valid).\nPlease try again." % (choice, len(citylist)))
				exit()
	if geodata:
		info = WI.start(geodata=geodata, units=units, scheme=scheme)  # INTERACTIVE CALL (unthreaded)
	elif cityID:
		info = WI.start(cityID=cityID, units=units, scheme=scheme)  # INTERACTIVE CALL (unthreaded)
	else:
		print("ERROR: missing cityname or geodata or cityid.")
		exit()
	if WI.error:
		print(WI.error.replace("[__main__]", "").strip())
		exit()

	if info is not None and not control:
		if not quiet:
			if mode == "msn":
				print("Using city/area: %s" % info["currentLocation"]["displayName"])
			elif mode in ["owm", "omw"]:
				print("Using city/area: %s [lon=%s, lat=%s]" % (info["requested"]["cityName"], info["requested"]["lon"], info["requested"]["lat"]))
		successtext = "File '%s' was successfully created."
		if json:
			WI.writejson(json)
			if not quiet and not WI.error:
				print(successtext % json)
		if reduced:
			WI.writereducedjson(reduced)
			if not quiet:
				print(successtext % reduced)
		if xml:
			if mode == "msn":
				WI.writemsnxml(xml)
				if not quiet and not WI.error:
					print(successtext % xml)
			else:
				print("ERROR: XML is only supported in mode 'msn'.\nFile '%s' was not created..." % xml)
	if WI.error:
			print(WI.error.replace("[__main__]", "").strip())


if __name__ == "__main__":
	main(argv[1:])
