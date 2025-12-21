from flask import Flask, render_template, request, jsonify
from services.Amadeus_Api import get_airports
from services.Weather_Api import get_current_weather, get_coordinates, get_daily_weather, calculate_statistics

app = Flask(__name__)

# När man öppnar "http://127.0.0.1:5000/" körs denna funktionen
# Öppnar HTML filen för användaren
@app.route('/')
def search():
    return render_template('search.html')

# Öppnar nästa HTML sida
@app.route('/results')
def results():
    '''
    TODO: hantera sökresultaten här sedan tror jag?
    '''
    return render_template('HTMLsida2.html')

# Detta är en endpoint. Vår browser pratar med denna, inte med Amadeus direkt.
# T.ex /search_airports?keyword=HEA
@app.route('/search_airports')
def search_airports():

    # hämtar datan efter '?'
    keyword = request.args.get('keyword')

    # anropar funktion från Amadeus_Api.py fil
    airports_data = get_airports(keyword)

    return jsonify(airports_data)

# Detta är en endpoint för vårt väder-API som frontend pratar med. Denna endpoint
# anropar get_current_weather funtkionen som i sin tur hämtar och bearbetar väderdatan.
# exempelurl: /current_weather?city=Stockholm
@app.route('/current_weather')
def current_weather():

    # Hämtar stadens namn från query parameter
    city = request.args.get('city')

    # Anropar väderfunktionen från Weather_Api.py filen
    weather_data = get_current_weather(city)

    # Felhantering
    if not weather_data:
        return jsonify({"Error": "Could not fetch weather data"}), 400
    
    return jsonify(weather_data)

@app.route('/monthly_weather')
def monthly_weather():
    city = request.args.get('city')

    lat, lon = get_coordinates(city) #koordinater för staden
    daily_data = get_daily_weather(lat,lon) # hämta dagligt väder
    stats = calculate_statistics(daily_data) #räkna ut statistik (medelvärde, lägsta, högsta)

    return jsonify(stats) #retunerar statistik

# mashup-endpoint som kombinerar flyg & aktuellt väder
# exempel: /search_airports_with_weather?keyword=STO
@app.route('/search_airports_with_weather')
def search_airports_with_weather():

    # hämtar användarens inskickade keyword
    keyword = request.args.get('keyword')

    # hämtar flygplatser baserat på keyword
    airports = get_airports(keyword)

    # lista (flyg + väder)
    results = []

    for airport in airports: # loopar igenom varje flygplats 

        city = airport.get("cityName") #försöker hämta stadens namn från Amadeus

        if not city: 
            continue
 
        weather = get_current_weather(city) #hämtar väder 

        if not weather:
            continue

        combined_result = {
            "airport": airport,
            "weather": weather
        }

        results.append(combined_result)

    return jsonify(results)
    

#starta programmet
if __name__ == '__main__':
    # debug=True gör en auto refresh när saker förändras
    app.run(debug = True)