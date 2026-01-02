import os
import requests
from pathlib import Path
from dotenv import load_dotenv

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
root_dir = backend_dir

if (root_dir / ".env").exists():
    load_dotenv(dotenv_path=root_dir / ".env")
else:
    load_dotenv(dotenv_path=backend_dir / ".env")

# Hämtar väderdata från en stad, returnerar dictionary med relevanta data eller None vid fel
def get_current_weather(city):

    if not city:
        return None
    
    # Hämtar api-nyckeln från .env 
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')

    if not api_key:
        return None
    
    # APIets endpoint för 'aktuellt väder'
    url = "https://api.openweathermap.org/data/2.5/weather"

    # Parametrar som skickas med i API-anropet
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    # Skickar HTTP GET-request till API
    response = requests.get(url, params=params)

    # Om APIt inte svarar korrekt
    if response.status_code != 200:
        return None
    
    # Gör om svaret från JSON till Python-dictionary
    data = response.json()

    # Plockar ut relevant info till vårt dictionary
    weather_data = {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }

    # Returnerar den bearbetade väderdatan
    return weather_data

#hämtar koordinaterna för staden 
def get_coordinates(city):

    if not city:
        return None
    
    # Hämtar api-nyckeln från .env 
    api_key = os.getenv('OPENWEATHERMAP_API_KEY')

    if not api_key:
        return None
    
    url = "http://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": city,
        "limit": 1,
        "appid": api_key
    }

    data = requests.get(url, params=params).json()

    if not data:
        return None, None
    
    return data[0]["lat"], data[0]["lon"]

#för att hämta dagligt väder
def get_daily_weather(lat,lon):
    url = "https://api.openweathermap.org/data/3.0/onecall"

    api_key = os.getenv('OPENWEATHERMAP_API_KEY')

    params = {
        "lat" : lat,
        "lon" : lon,
        "exclude": "current,minutely,hourly,alerts",
        "units": "metric",
        "appid": api_key
    }

    response = requests.get(url, params=params)
    return response.json()["daily"]

def calculate_statistics(daily_data):

    day = [] #dag temp
    night = [] #natt temp
    min_t = [] #minsta temp
    max_t = [] #max temp

    for d in daily_data:
        day.append(d["temp"]["day"])
        night.append(d["temp"]["night"])
        min_t.append(d["temp"]["min"])
        max_t.append(d["temp"]["max"])

    def avg(arr):
        return round(sum(arr) / len(arr), 1)
    
    return {
        "avg_day": avg(day),
        "avg_night": avg(night),
        "min_temp": min(min_t),
        "max_temp": max(max_t)
    }

