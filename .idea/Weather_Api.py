import os
import requests

# Hämtar väderdata från en stad, returnerar dictionary med relevanta data eller None vid fel
def get_weather(city):

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