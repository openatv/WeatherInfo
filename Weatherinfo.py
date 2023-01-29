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
SOURCES = ["msn", "omw", "owm"]  # supported sourcecodes (the order must not be changed)
DESTINATIONS = ["yahoo", "meteo"]  # supported iconcodes (the order must not be changed)


class Weatherinfo:
	def __init__(self, newmode="msn", apikey=None):

		self.msnCodes = {"SunnyDayV3": ("32", "B"), "MostlySunnyDay": ("34", "B"), "PartlyCloudyDayV3": ("30", "H"),
						"MostlyCloudyDayV2": ("28", "H"), "CloudyV3": ("26", "Y"), "BlowingHailV2": ("17", "X"),
						"HeavyDrizzle": ("9", "Q"), "BlowingSnowV2": ("13", "W"), "LightRainV2": ("12", "Q"), "FogV2": ("20", "E"),
						"FreezingRainV2": ("10", "X"), "HazySmokeV2": ("21", "J"), "ModerateRainV2": ("12", "Q"),
						"HeavySnowV2": ("15", "W"), "HailDayV2": ("17", "X"), "LightRainV3": ("9", "Q"),
						"LightRainShowerDay": ("11", "Q"), "LightSnowV2": ("14", "V"), "RainShowersDayV2": ("39", "R"),
						"RainSnowV2": ("5", "W"), "SnowShowersDayV2": ("16", "W"), "ThunderstormsV2": ("4", "0"),
						"ClearNightV3": ("31", "C"), "MostlyClearNight": ("33", "C"), "PartlyCloudyNightV2": ("29", "I"),
						"MostlyCloudyNightV2": ("27", "I"), "HazeSmokeNightV2_106": ("21", "K"), "HailNightV2": ("17", "X"),
						"LightRainShowerNight": ("45", "Q"), "RainShowersNightV2": ("45", "R"), "N422Snow": ("14", "W"),
						"RainSnowShowersNightV2": ("5", "W"), "SnowShowersNightV2": ("46", "W"), "na": ("NA", ")")
						}  # mapping: msn -> (yahoo, meteo)
		self.omwCodes = {"0": ("32", "B"), "1": ("34", "B"), "2": ("30", "H"), "3": ("28", "N"), "45": ("20", "M"), "48": ("21", "J"),
						"51": ("9", "Q"), "53": ("9", "Q"), "55": ("9", "R"), "56": ("8", "V"), "57": ("10", "U"),
						"61": ("9", "Q"), "63": ("11", "R"), "65": ("12", "T"), "66": ("8", "R"), "67": ("7", "W"),
						"71": ("42", "V"), "73": ("14", "U"), "75": ("41", "W"), "77": ("35", "X"), "80": ("9", "Q"),
						"81": ("11", "Q"), "82": ("12", "T"), "85": ("42", "V"), "86": ("43", "W"), "95": ("38", "P"),
						"96": ("4", "O"), "99": ("4", "Z")
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
						"800": ("32", "B"), "801": ("34", "B"), "802": ("30", "H"), "803": ("26", "H"), "804": ("28", "N"),
						"na": ("NA", ")")
						}  # mapping: owm -> (yahoo, meteo)
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
						"802": "scattered clouds: 25-50%", "803": "broken clouds: 51-84%", "804": "overcast clouds: 85-100%", "na": "not available"
						}  # cleartext description of owm-weathercodes
		self.yahooDescs = {
						"0": "tornado", "1": "tropical storm", "2": "hurricane", "3": "severe thunderstorms", "4": "thunderstorms", "5": "mixed rain and snow",
						"6": "mixed rain and sleet", "7": "mixed snow and sleet", "8": "freezing drizzle", "9": "drizzle", "10": "freezing rain",
						"11": "showers", "12": "showers", "13": "snow flurries", "14": "light snow showers", "15": "blowing snow", "16": "snow",
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
		if newmode in SOURCES:
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
		else:
			self.parser = None
			self.error = "[%s] ERROR in module 'setmode': unknown mode '%s'" % (MODULE_NAME, newmode)
			return self.error

	def directionsign(self, degree):
		return "." if degree < 0 else ["↓ N", "↙ NE", "← E", "↖ SE", "↑ S", "↗ SW", "→ W", "↘ NW"][round(degree % 360 / 45 % 7.5)]

	def convert2icon(self, src, code):
		self.error = None
		src = src.lower()
		if code is None:
			self.error = "[%s] ERROR in module 'convert2icon': input code value is 'None'" % MODULE_NAME
			print(self.error)
			return
		code = str(code).strip()
		selection = {"msn": self.msnCodes, "owm": self.owmCodes, "omw": self.omwCodes}
		if src is not None and src in selection:
			common = selection[src]
		else:
			self.error = "[%s] WARNING in module 'convert2icon': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, SOURCES)
			print(self.error)
			return
		result = dict()
		if code in common:
			result["yahooCode"] = common[code][0]
			result["meteoCode"] = common[code][1]
		else:
			result["yahooCode"] = "NA"
			result["meteoCode"] = "NA"
			self.error = "[%s] WARNING in module 'convert2icon': key '%s' not found in converting dicts." % (MODULE_NAME, code)
			print(self.error)
			return
		return result

	def getCitylist(self, cityname=None, scheme="de-de"):
		self.error = None
		if not cityname:
			self.error = "[%s] ERROR in module 'getCitylist': missing cityname." % MODULE_NAME
			return

		if self.mode == "msn":
			for special in [",", ";", "&", "|", "!", "(", "[", "{"]:
				items = cityname.split(special)
				cityname = "".join(items[:-1]).strip() if len(items) > 1 else items[0]
			apicode = "454445433343423734434631393042424245323644463739333846334439363145393235463539333"
			apikey = bytes.fromhex(apicode[:-1]).decode('utf-8')
			linkcode = "68747470733a2f2f7777772e62696e672e636f6d2f6170692f76362f506c616365732f4175746f537567676573743f61707069643d257326636f756e743d313526713d2573267365746d6b743d2573267365746c616e673d25737"
			link = bytes.fromhex(linkcode[:-1]).decode('utf-8') % (apikey, cityname, scheme, scheme)
			jsonData = self.apiserver(link)
			if not jsonData:
				self.error = "[%s] ERROR in module 'getCitylist.msn': city '%s' not found on the server, continue with '%s'." % (MODULE_NAME, cityname)
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
						citylist.append((cityname, 0, 0))
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitylist.msn': general error. %s" % (MODULE_NAME, str(err))
				return
		elif self.mode == "owm":
			special = {"br": "pt_br", "se": "sv, se", "es": "sp, es", "ua": "ua, uk", "cn": "zh_cn"}
			if scheme[:2] in special:
				scheme = special[scheme[:2]]
			for special in [",", ";", "&", "|", "!", "(", "[", "{"]:
				items = cityname.split(special)
				cityname = "".join(items[:-1]).strip() if len(items) > 1 else items[0]
			country = "".join(items[-1:]).strip().upper() if len(items) > 1 else None
			link = "http://api.openweathermap.org/geo/1.0/direct?q=%s,%s&lang=%s&limit=15&appid=%s" % (cityname, country, scheme[:2], self.apikey)
			jsonData = self.apiserver(link)
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

		elif self.mode == "omw":
			for special in [",", ";", "&", "|", "!", "(", "[", "{"]:
				items = cityname.split(special)
				cityname = "".join(items[:-1]).strip() if len(items) > 1 else items[0]
			country = "".join(items[-1:]).strip().upper() if len(items) > 1 else None
			link = "https://geocoding-api.open-meteo.com/v1/search?language=%s&count=10&name=%s" % (scheme[:2], cityname)
			jsonData = self.apiserver(link)
			if not jsonData or "results" not in jsonData:
				self.error = "[%s] ERROR in module 'getCitylist.omw': no city '%s' found on the server. Try another wording." % (MODULE_NAME, cityname)
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
				self.error = "[%s] ERROR in module 'getCitylist.omw': general error. %s" % (MODULE_NAME, str(err))
				return
		else:
			self.error = "[%s] ERROR in module 'start': unknown mode." % MODULE_NAME
			return
		return citylist

	def start(self, geodata=None, cityID=None, units="metric", scheme="de-de", reduced=False, callback=None):
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
			if self.mode not in SOURCES:
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
			output = response.content.decode("utf-8", "ignore")
			startpos = output.find('</style>')
			endpos = output.find('</script></div>')
			bereich = output[startpos:endpos]
			svgdata = findall('<img class="iconTempPartIcon-E1_1" src="(.*?)" title="(.*?)"/></div>', bereich)
			todayData = search('class="summaryLineGroupCompact-E1_1">(.*?)" title="(.*?)<a data-t=', bereich)
			svgsrc = "N/A" if todayData is None else search('src="(.*?)"/><a data-t=', todayData.group(0)).group(1)
			svgname = "na" if todayData is None else svgsrc[svgsrc.rfind("/") + 1:svgsrc.rfind(".")]
			svgdesc = "N/A" if todayData is None else search('title="(.*?)" src=', todayData.group(1))
			# Create DICT "jsonData" from JSON-string and add some useful infos
			start = '<script id="redux-data" type="application/json">'
			startpos = output.find(start)
			endpos = output.find("</script>", startpos)
			output = output[startpos + len(start):endpos]
			if len(output):
				jsonData = None
				try:
					output = loads(output)
					jsonData = output["WeatherData"]["_@STATE@_"]
				except Exception as jsonerr:
					self.error = "[%s] ERROR in module 'msnparser': found invalid json-string. %s" % (MODULE_NAME, str(jsonerr))
				if jsonData:
					currdate = datetime.fromisoformat(jsonData["lastUpdated"])
					jsonData["currentCondition"]["deepLink"] = link  # replace by minimized link
					jsonData["currentCondition"]["date"] = currdate.strftime("%Y-%m-%d")  # add some missing info
					jsonData["currentCondition"]["image"]["svgsrc"] = svgsrc
					jsonData["currentCondition"]["image"]["svgname"] = svgname
					jsonData["currentCondition"]["image"]["svgdesc"] = svgdesc
					iconCode = self.convert2icon("MSN", svgname)
					if iconCode:
						jsonData["currentCondition"]["yahooCode"] = iconCode.get("yahooCode", "NA")
						jsonData["currentCondition"]["meteoCode"] = iconCode.get("meteoCode", ")")
						jsonData["currentCondition"]["day"] = currdate.strftime("%A")
						jsonData["currentCondition"]["shortDay"] = currdate.strftime("%a")
					for idx, forecast in enumerate(jsonData["forecast"][: -2]):  # last two entries are not usable
						forecast["deepLink"] = "%s&day=%s" % (link, idx + 1)  # replaced by minimized link
						forecast["date"] = (currdate + timedelta(days=idx)).strftime("%Y-%m-%d")
						if idx < len(svgdata):
							svgsrc = svgdata[idx][0]
							svgname = svgsrc[svgsrc.rfind("/") + 1:svgsrc.rfind(".")]
							forecast["image"]["svgsrc"] = svgsrc
							forecast["image"]["svgname"] = svgname
							forecast["image"]["svgdesc"] = svgdata[idx][1]
						else:
							forecast["image"]["svgsrc"] = "N/A"
							forecast["image"]["svgdesc"] = "N/A"
						iconCodes = self.convert2icon("MSN", svgname)
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
			current = self.info["currentCondition"]
			root = Element("weatherdata")
			root.set("xmlns:xsd", "http://www.w3.org/2001/XMLSchema")
			root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
			w = Element("weather")
			w.set("weatherlocationname", self.info["currentLocation"]["displayName"])
			w.set("url", current["deepLink"])
			w.set("degreetype", current["degreeSetting"][1:])
			w.set("long", self.info["currentLocation"]["longitude"])
			w.set("lat", self.info["currentLocation"]["latitude"])
			w.set("timezone", "%s" % int(self.info["source"]["location"]["TimezoneOffset"][: 2]))
			w.set("alert", current["alertSignificance"])
			w.set("encodedlocationname", self.info["currentLocation"]["locality"].encode("ascii", "xmlcharrefreplace").decode().replace(" ", "%20").replace("\n", "").strip())
			root.append(w)
			c = Element("current")
			c.set("temperature", current["currentTemperature"])
			c.set("skycode", current["normalizedSkyCode"])
			c.set("skytext", current["skycode"]["children"])
			c.set("date", current["date"])
			c.set("svglink", current["image"]["svgsrc"])
			c.set("svgdesc", current["image"]["svgname"])
			c.set("yahoocode", current["yahooCode"])
			c.set("meteocode", current["meteoCode"])
			c.set("observationtime", self.info["lastUpdated"][11: 19])
			c.set("observationpoint", self.info["currentLocation"]["locality"])
			c.set("feelslike", current["feels"].replace("°", "")).strip()
			c.set("humidity", current["humidity"].replace("%", "")).strip()
			c.set("winddisplay", "%s %s" % (current["windSpeed"], self.directionsign(current["windDir"])))
			c.set("day", self.info["forecast"][0]["dayTextLocaleString"])
			c.set("shortday", current["shortDay"])
			c.set("windspeed", current["windSpeed"])
			w.append(c)
			for forecast in self.info["forecast"][: -2]:  # last two entries are not usable
				f = Element("forecast")
				f.set("low", "%s" % forecast["lowTemp"])
				f.set("high", "%s" % forecast["highTemp"])
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
			xmlString = tostring(xmlData, encoding="utf-8", method="html")
			try:
				with open(filename, "wb") as f:
					f.write(xmlString)
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
			link = "https://api.open-meteo.com/v1/forecast?longitude=%s&latitude=%s&hourly=temperature_2m,relativehumidity_2m,apparent_temperature,weathercode,windspeed_10m,winddirection_10m&daily=sunrise,sunset,weathercode,precipitation_sum,temperature_2m_max,temperature_2m_min&timezone=%s&windspeed_unit=%s&temperature_unit=%s" % (float(self.geodata[1]), float(self.geodata[2]), currzone, windunit, tempunit)
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
				now = datetime.now()
				sunrise = datetime.fromisoformat(jsonData["daily"]["sunrise"][0])
				sunset = datetime.fromisoformat(jsonData["daily"]["sunset"][0])
				jsonData["isNight"] = now < sunrise or now > sunset
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

	def owmparser(self):
		self.error = None
		self.info = None
		if not self.apikey:
			self.error = "[%s] ERROR in module' owmparser': API-key is missing!" % MODULE_NAME
			if self.callback:
				self.callback(None, self.error)
			return
		if self.cityID:
			link = "http://api.openweathermap.org/data/2.5/forecast?id=%s&units=%s&lang=%s&appid=%s" % (self.cityID, self.units, self.scheme[: 2], self.apikey)
		elif self.geodata:
			link = "https://api.openweathermap.org/data/2.5/forecast?&lon=%s&lat=%s&units=%s&lang=%s&appid=%s" % (self.geodata[1], self.geodata[2], self.units, self.scheme[: 2], self.apikey)
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
					jsonData["requested"] = dict()
					jsonData["requested"]["cityName"] = self.geodata[0]
					jsonData["requested"]["lon"] = self.geodata[1]
					jsonData["requested"]["lat"] = self.geodata[2]
				now = datetime.now()
				sunrise = datetime.fromtimestamp(jsonData["city"]["sunrise"])
				sunset = datetime.fromtimestamp(jsonData["city"]["sunset"])
				jsonData["isNight"] = now < sunrise or now > sunset
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
				citydata = jsonData.get("city", {})
				cityname = citydata.get("name", "N/A")
				lon = citydata.get("coord", {}).get("lon", "N/A")
				lat = citydata.get("coord", {}).get("lat", "N/A")
				return (cityname, lon, lat)
			except Exception as err:
				self.error = "[%s] ERROR in module 'getCitybyID': general error. %s" % (MODULE_NAME, str(err))
				return
		else:
			self.error = "[%s] ERROR in module 'getCitybyID': no city '%s' found on the server. Try another wording." % (MODULE_NAME, cityname)

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
					citylist.append(("%s%s%s" % (cityname, state, country), hit.get("lon", "N/A"), hit.get("lat", "N/A")))
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
					current = self.info["currentCondition"]  # collect current weather data
					reduced["source"] = "MSN Weather"
					reduced["name"] = self.info["currentLocation"]["displayName"]
					reduced["longitude"] = self.info["currentLocation"]["longitude"]
					reduced["latitude"] = self.info["currentLocation"]["latitude"]
					reduced["tempunit"] = "°F" if self.units == "imperial" else "°C"
					reduced["windunit"] = "mph" if self.units == "imperial" else "km/h"
					reduced["precunit"] = "%"
					reduced["current"] = dict()
					reduced["current"]["observationTime"] = self.info["lastUpdated"]
					reduced["current"]["sunrise"] = self.info["forecast"][0]["almanac"]["sunrise"]
					reduced["current"]["sunset"] = self.info["forecast"][0]["almanac"]["sunset"]
					reduced["current"]["isNight"] = self.info["currentCondition"]["isNight"]
					reduced["current"]["yahooCode"] = current["yahooCode"]
					reduced["current"]["meteoCode"] = current["meteoCode"]
					reduced["current"]["temp"] = current["currentTemperature"]
					reduced["current"]["feelsLike"] = current["feels"].replace("°", "").strip()
					reduced["current"]["humidity"] = current["humidity"].replace("%", "").strip()
					reduced["current"]["windSpeed"] = current["windSpeed"].replace("km/h", "").replace("mph", "").strip()
					windDir = current["windDir"]
					reduced["current"]["windDir"] = "%s" % windDir
					reduced["current"]["windDirSign"] = self.directionsign(windDir)
					date = current["date"]
					reduced["current"]["day"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%A")
					reduced["current"]["shortDay"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%a")
					reduced["current"]["date"] = date
					reduced["current"]["text"] = current["shortCap"]
					reduced["current"]["minTemp"] = "%s" % self.info["forecast"][0]["lowTemp"]
					reduced["current"]["maxTemp"] = "%s" % self.info["forecast"][0]["highTemp"]
					reduced["current"]["precipitation"] = current["precipitation"]["children"].replace("%", "").strip()
					forecast = self.info["forecast"]
					reduced["forecast"] = dict()
					for idx in range(6):  # collect forecast of today and next 5 days
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = forecast[idx]["yahooCode"]
						reduced["forecast"][idx]["meteoCode"] = forecast[idx]["meteoCode"]
						reduced["forecast"][idx]["minTemp"] = "%s" % forecast[idx]["lowTemp"]
						reduced["forecast"][idx]["maxTemp"] = "%s" % forecast[idx]["highTemp"]
						reduced["forecast"][idx]["precipitation"] = "%s" % forecast[idx]["precipitation"].replace("%", "").strip()
						date = forecast[idx]["date"]
						reduced["forecast"][idx]["day"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%A")
						reduced["forecast"][idx]["shortDay"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%a")
						reduced["forecast"][idx]["date"] = forecast[idx]["date"]
						reduced["forecast"][idx]["text"] = forecast[idx]["cap"]
				except Exception as err:
					self.error = "[%s] ERROR in module 'getreducedinfo.msn': general error. %s" % (MODULE_NAME, str(err))
					return

			elif self.parser is not None and self.mode == "omw":
				try:
					daily = self.info["daily"]
					reduced["source"] = "O-M Weather"
					reduced["name"] = self.info["requested"]["cityName"]
					reduced["longitude"] = "%s" % self.info["longitude"]
					reduced["latitude"] = "%s" % self.info["latitude"]
					reduced["tempunit"] = "°F" if self.units == "imperial" else "°C"
					reduced["windunit"] = "mph" if self.units == "imperial" else "km/h"
					reduced["precunit"] = self.info["daily_units"]["precipitation_sum"]
					isotime = "%s%s" % (datetime.now(timezone.utc).astimezone().isoformat()[:14], "00")
					reduced["current"] = dict()
					for idx, current in enumerate(self.info["hourly"]["time"]):
						if isotime in current:
							isotime = datetime.now(timezone.utc).astimezone().isoformat()
							reduced["current"]["observationTime"] = "%s%s" % (isotime[:19], isotime[26:])
							reduced["current"]["sunrise"] = datetime.fromisoformat(daily["sunrise"][0]).astimezone().isoformat()
							reduced["current"]["sunset"] = datetime.fromisoformat(daily["sunset"][0]).astimezone().isoformat()
							reduced["current"]["isNight"] = self.info["isNight"]
							reduced["current"]["yahooCode"] = self.info["hourly"]["yahooCode"][idx]
							reduced["current"]["meteoCode"] = self.info["hourly"]["meteoCode"][idx]
							reduced["current"]["temp"] = "%s" % round(self.info["hourly"]["temperature_2m"][idx])
							reduced["current"]["feelsLike"] = "%s" % round(self.info["hourly"]["apparent_temperature"][idx])
							reduced["current"]["humidity"] = "%s" % round(self.info["hourly"]["relativehumidity_2m"][idx])
							reduced["current"]["windSpeed"] = "%s" % round(self.info["hourly"]["windspeed_10m"][idx])
							windDir = self.info["hourly"]["winddirection_10m"][idx]
							reduced["current"]["windDir"] = "%s" % windDir
							reduced["current"]["windDirSign"] = self.directionsign(windDir)
							reduced["current"]["day"] = datetime(int(current[:4]), int(current[5:7]), int(current[8:10])).strftime("%A")
							reduced["current"]["shortDay"] = datetime(int(current[:4]), int(current[5:7]), int(current[8:10])).strftime("%a")
							reduced["current"]["date"] = current[:10]
							reduced["current"]["text"] = "N/A"
							reduced["current"]["minTemp"] = "%s" % round(daily["temperature_2m_min"][0])
							reduced["current"]["maxTemp"] = "%s" % round(daily["temperature_2m_max"][0])
							reduced["current"]["precipitation"] = "%s" % round(daily["precipitation_sum"][0], 1)
							break
					reduced["forecast"] = dict()
					for idx in range(6):  # collect forecast of today and next 5 days
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = daily["yahooCode"][idx]
						reduced["forecast"][idx]["meteoCode"] = daily["meteoCode"][idx]
						reduced["forecast"][idx]["minTemp"] = "%s" % round(daily["temperature_2m_min"][idx])
						reduced["forecast"][idx]["maxTemp"] = "%s" % round(daily["temperature_2m_max"][idx])
						reduced["forecast"][idx]["precipitation"] = "%s" % round(daily["precipitation_sum"][idx], 1)
						date = daily["time"][idx]
						reduced["forecast"][idx]["day"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%A")
						reduced["forecast"][idx]["shortDay"] = datetime(int(date[:4]), int(date[5:7]), int(date[8:])).strftime("%a")
						reduced["forecast"][idx]["date"] = date
						reduced["forecast"][idx]["text"] = "N/A"
				except Exception as err:
					self.error = "[%s] ERROR in module 'getreducedinfo.owm': general error. %s" % (MODULE_NAME, str(err))
					return

			elif self.parser is not None and self.mode == "owm":
				try:
					current = self.info["list"][0]  # collect current weather data
					reduced["source"] = "OWM Weather"
					reduced["name"] = self.info["requested"]["cityName"]
					reduced["longitude"] = "%s" % self.info["requested"]["lon"]
					reduced["latitude"] = "%s" % self.info["requested"]["lat"]
					reduced["tempunit"] = "°F" if self.units == "imperial" else "°C"
					reduced["windunit"] = "mph" if self.units == "imperial" else "km/h"
					reduced["precunit"] = "in" if self.units == "imperial" else "mm"
					reduced["current"] = dict()
					isotime = datetime.now(timezone.utc).astimezone().isoformat()
					reduced["current"]["observationTime"] = "%s%s" % (isotime[:19], isotime[26:])
					reduced["current"]["sunrise"] = datetime.fromtimestamp(int(self.info["city"]["sunrise"])).astimezone().isoformat()
					reduced["current"]["sunset"] = datetime.fromtimestamp(int(self.info["city"]["sunset"])).astimezone().isoformat()
					reduced["current"]["isNight"] = self.info["isNight"]
					reduced["current"]["yahooCode"] = current["weather"][0]["yahooCode"]
					reduced["current"]["meteoCode"] = current["weather"][0]["meteoCode"]
					reduced["current"]["temp"] = "%s" % round(current["main"]["temp"])
					reduced["current"]["feelsLike"] = "%s" % round(current["main"]["feels_like"])
					reduced["current"]["humidity"] = "%s" % round(current["main"]["humidity"])
					reduced["current"]["windSpeed"] = "%s" % round(current["wind"]["speed"] * 3.6)
					windDir = current["wind"]["deg"]
					reduced["current"]["windDir"] = "%s" % windDir
					reduced["current"]["windDirSign"] = self.directionsign(int(windDir))
					reduced["current"]["day"] = current["day"]
					reduced["current"]["shortDay"] = current["shortDay"]
					reduced["current"]["date"] = datetime.fromtimestamp(current["dt"]).strftime("%Y-%m-%d")
					reduced["current"]["text"] = current["weather"][0]["description"]
					tmin = 88  # inits for today
					tmax = -88
					yahoocode = None
					meteocode = None
					text = None
					idx = 0
					prec = 0
					reduced["forecast"] = dict()
					for forecast in self.info["list"]:  # collect forecast of today and next 5 days
						tmin = min(tmin, forecast["main"]["temp_min"])
						tmax = max(tmax, forecast["main"]["temp_max"])
						prec += forecast["rain"]["3h"] if "rain" in forecast else 0
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
							reduced["forecast"][idx]["minTemp"] = "%s" % round(tmin)
							reduced["forecast"][idx]["maxTemp"] = "%s" % round(tmax)
							reduced["forecast"][idx]["precipitation"] = "%s" % round(prec, 1)
							reduced["forecast"][idx]["day"] = forecast["day"]
							reduced["forecast"][idx]["shortDay"] = forecast["shortDay"]
							reduced["forecast"][idx]["date"] = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
							reduced["forecast"][idx]["text"] = forecast["weather"][0]["description"]
							tmin = 88  # inits for next day
							tmax = -88
							prec = 0
							yahoocode = None
							meteocode = None
							text = None
							idx += 1
					if idx == 5 and "21:00:00" in forecast["dt_txt"]:  # in case day #5 is missing: create a copy of day 4 (=fake)
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = yahoocode if yahoocode else reduced["forecast"][idx - 1]["yahooCode"]
						reduced["forecast"][idx]["meteoCode"] = meteocode if meteocode else reduced["forecast"][idx - 1]["meteoCode"]
						reduced["forecast"][idx]["minTemp"] = "%s" % round(tmin) if tmin != 88 else reduced["forecast"][idx - 1]["minTemp"]
						reduced["forecast"][idx]["maxTemp"] = "%s" % round(tmax) if tmax != - 88 else reduced["forecast"][idx - 1]["maxTemp"]
						reduced["forecast"][idx]["precipitation"] = "%s" % round(prec, 1)
						nextdate = datetime.strptime(reduced["forecast"][idx - 1]["date"], "%Y-%m-%d") + timedelta(1)
						reduced["forecast"][idx]["day"] = nextdate.strftime("%A")
						reduced["forecast"][idx]["shortDay"] = nextdate.strftime("%a")
						reduced["forecast"][idx]["date"] = nextdate.strftime("%Y-%m-%d")
						reduced["forecast"][idx]["text"] = text if text else reduced["forecast"][idx - 1]["text"]
					elif idx == 5:  # in case day #5 is incomplete: use what we have
						reduced["forecast"][idx] = dict()
						reduced["forecast"][idx]["yahooCode"] = yahoocode if yahoocode else forecast["weather"][0]["yahooCode"]
						reduced["forecast"][idx]["meteoCode"] = meteocode if meteocode else forecast["weather"][0]["meteoCode"]
						reduced["forecast"][idx]["minTemp"] = "%s" % round(tmin) if tmin != 88 else reduced["forecast"][idx - 1]["minTemp"]
						reduced["forecast"][idx]["maxTemp"] = "%s" % round(tmax) if tmax != - 88 else reduced["forecast"][idx - 1]["maxTemp"]
						reduced["forecast"][idx]["precipitation"] = "%s" % round(prec, 1)
						reduced["forecast"][idx]["day"] = forecast["day"]
						reduced["forecast"][idx]["shortDay"] = forecast["shortDay"]
						reduced["forecast"][idx]["date"] = datetime.fromtimestamp(forecast["dt"]).strftime("%Y-%m-%d")
						reduced["forecast"][idx]["text"] = text if text else reduced["forecast"][idx - 1]["text"]
					reduced["current"]["minTemp"] = reduced["forecast"][0]["minTemp"]  # add missing data for today
					reduced["current"]["maxTemp"] = reduced["forecast"][0]["maxTemp"]
					reduced["current"]["precipitation"] = reduced["forecast"][0]["precipitation"]

				except Exception as err:
					self.error = "[%s] ERROR in module 'getreducedinfo.owm': general error. %s" % (MODULE_NAME, str(err))
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
		src = src.lower()
		selection = {"msn": None, "owm": self.owmDescs, "omw": self.omwDescs, "yahoo": self.yahooDescs, "meteo": self.meteoDescs}
		if src is not None and src in selection:
			descs = selection[src]
		else:
			self.error = "[%s] ERROR in module 'showDescription': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, SOURCES)
			return self.error
		print("\n+%s+" % ("-" * 39))
		print("| {0:<5}{1:<32} |".format("CODE", "DESCRIPTION_%s (COMPLETE)" % src.upper()))
		print("+%s+" % ("-" * 39))
		if src == "msn":
			for desc in self.msnCodes:
				print("| {0:<5}{1:<32} |".format("none", desc))
		else:
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
			print("| {0:<5}{1:<32} | {2:<5}{3:<25} |".format("CODE", "DESCRIPTION_%s (CONVERTER)" % src.upper(), "CODE", "DESCRIPTION_%s" % dest.upper()))
			print("+%s+%s+" % ("-" * 39, "-" * 32))
			if src == "msn":
				for scode in sCodes:
					dcode = sCodes[scode][destidx]
					print("| {0:<5}{1:<32} | {2:<5}{3:<25} |".format("none", scode, dcode, ddescs[dcode]))
			elif src == "omw":
				for scode in self.omwCodes:
					dcode = self.omwCodes[scode][destidx]
					print("| {0:<5}{1:<32} | {2:<5}{3:<25} |".format(scode, self.omwDescs[scode], dcode, ddescs[dcode]))
			elif src == "owm":
				for scode in self.owmCodes:
					dcode = self.owmCodes[scode][destidx]
					print("| {0:<5}{1:<32} | {2:<5}{3:<25} |".format(scode, self.owmDescs[scode], dcode, ddescs[dcode]))
			print("+%s+%s+" % ("-" * 39, "-" * 32))
		else:
			self.error = "[%s] ERROR in module 'showConvertrules': convert source '%s' is unknown. Valid is: %s" % (MODULE_NAME, src, SOURCES)
			return self.error


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
	geodata = None
	info = None

	helpstring = "Weatherinfo v1.5: try 'Weatherinfo -h' for more information"
	try:
		opts, args = getopt(argv, "hqm:a:j:r:x:s:u:i:c", ["quiet =", "mode=", "apikey=", "json =", "reduced =", "xml =", "scheme =", "units =", "id =", "control ="])
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
			if arg in SOURCES:
				mode = arg
			else:
				print("ERROR: mode '%s' is invalid. Valid parameters: 'msn', 'omw' or 'owm'" % arg)
				exit()
		elif opt in ("-a", "--apikey"):
			apikey = arg
		elif opt in ("-i", "--id"):
			cityID = arg
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
		cityname += "%s " % part
	cityname = cityname.strip()
	if len(cityname) < 3 and not specialopt:
		print("ERROR: Cityname too short, please use at least 3 letters!")
		exit()
	WI = Weatherinfo(mode, apikey)
	if control:
		for src in SOURCES + DESTINATIONS:
			if WI.showDescription(src):
				print(WI.error.replace("[__main__]", "").strip())
		for src in SOURCES:
			for dest in DESTINATIONS:
				WI.showConvertrules(src, dest)
	if WI.error:
		print(WI.error.replace("[__main__]", "").strip())
		exit()
	if cityname:
		citylist = WI.getCitylist(cityname, scheme)
		if WI.error:
			print(WI.error.replace("[__main__]", "").strip())
			exit()
		if len(citylist) == 0:
			print("No city '%s' found on the server. Try another wording.")
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
	if not specialopt:
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
