import json
import os
import time

from inky.auto import auto
inky_display = auto()
inky_display.set_border(inky_display.WHITE)

BLACK = inky_display.BLACK
WHITE = inky_display.WHITE

from PIL import Image, ImageFont, ImageDraw
from font_fredoka_one import FredokaOne

font_large = ImageFont.truetype(FredokaOne, 36)
font_medium = ImageFont.truetype(FredokaOne, 22)
font_small = ImageFont.truetype(FredokaOne, 16)

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")

print("""Inky pHAT: Weather Dashboard

Displays weather information for a given location.

""")

PATH = os.path.dirname(__file__)

CITY = "Indianapolis"
COUNTRYCODE = "USA"
WARNING_TEMP = 25.0

def get_coords(address):
    g = geocoder.arcgis(address)
    coords = g.latlng
    return coords

def get_weather(address):
    coords = get_coords(address)
    weather = {}
    res = requests.get("https://api.open-meteo.com/v1/forecast?latitude=" + str(coords[0]) + "&longitude=" + str(coords[1]) + "&temperature_unit=fahrenheit&wind_speed_unit=mph&current_weather=true&daily=temperature_2m_max,temperature_2m_min")
    print(res.text)
    if res.status_code == 200:
        j = json.loads(res.text)
        current = j["current_weather"]
        daily = j["daily"]
        weather["temperature"] = current["temperature"]
        weather["max_temp"] = daily["temperature_2m_max"]
        weather["min_temp"] = daily["temperature_2m_min"]
        weather["windspeed"] = current["windspeed"]
        weather["weathercode"] = current["weathercode"]
        return weather
    else:
        return weather

location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)

windspeed = 0.0
temperature = 0.0

if weather:
    temperature = weather["temperature"]
    max_temp = weather['max_temp'][0]
    min_temp = weather['min_temp'][0]
    windspeed = weather["windspeed"]
    weathercode = weather["weathercode"]

else:
    print("Warning, no weather information found!")
    

img = Image.new("P", (inky_display.width, inky_display.height))
draw = ImageDraw.Draw(img)

box1_coordinates = [10, 6, 120, 116]
box2_coordinates = [130, 6, 240, 116]

draw.rounded_rectangle(
    xy = box1_coordinates,
    radius = 10,
    fill = BLACK,
    outline = BLACK,
    width = 1
)

draw.rounded_rectangle(
    xy = box2_coordinates,
    radius = 10,
    fill = WHITE,
    outline = BLACK,
    width = 2
)
date_local=time.strftime("%m/%d")
time_local=time.strftime("%H:%M")

draw.text((15, 11), "{}°F".format(temperature), WHITE, font=font_large)
draw.text((135, 11), date_local, BLACK, font=font_medium)
draw.text((135, 35), time_local, BLACK, font=font_medium)
draw.text((15, 61), "High: {}°F".format(max_temp), WHITE, font=font_small)
draw.text((15, 85), "Low: {}°F".format(min_temp), WHITE, font=font_small)
draw.text((135, 92), "{}".format(CITY), BLACK, font=font_small)


inky_display.set_image(img)
inky_display.show()