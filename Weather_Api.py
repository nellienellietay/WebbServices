import os
import requests

# Hämtar väderdata från en stad, returnerar dictionary med relevanta data eller None vid fel
def get_weather(city):

    if not city:
        return None
    
    # Hämtar api-nyckeln från .env 
    api_key = os.getenv('OPENWEATHER_API_KEY')

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

    if response.status_code != 200:
        return None
    
    data = response.json()

    # Plockar ut relevant info
    weather_data = {
        "city": data["main"]["temp"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "wind_speed": data["wind"]["speed"]
    }

    return weather_data