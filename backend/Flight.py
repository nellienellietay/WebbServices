from flask import Flask, render_template, request, jsonify
from services.Amadeus_Api import get_airports, search_flights
from services.Weather_Api import get_weather, get_coordinates, get_daily_weather, calculate_statistics

app = Flask(__name__)

# När man öppnar "http://127.0.0.1:5000/" körs denna funktionen
# Öppnar HTML filen för användaren
@app.route('/')
def search():
    return render_template('search.html')

# Öppnar nästa HTML sida
@app.route('/results')
def results():
    where_from = request.args.get("whereFrom", "")
    where_to = request.args.get("whereTo", "")
    date = request.args.get("date", "")

    try:
        flights = search_flights(where_from, where_to, date, adults=1, limit=10)
        return render_template("HTMLsida2.html", flights=flights)
    except Exception as e:
        return render_template("HTMLsida2.html", flights=[], error=str(e))


# Detta är en endpoint. Vår browser pratar med denna, inte med Amadeus direkt.
# T.ex /search_airports?keyword=HEA
@app.route('/search_airports')
def search_airports():
    keyword = request.args.get('keyword', '')
    if len(keyword) < 3:
        return jsonify([])

    # hämtar datan efter '?'
    keyword = request.args.get('keyword')

    # anropar funktion från Amadeus_Api.py fil
    airports_data = get_airports(keyword)

    return jsonify(airports_data)

# Detta är en endpoint för vårt väder-API som frontend pratar med. Denna endpoint
# anropar get_weather funtkionen som i sin tur hämtar och bearbetar väderdatan.
@app.route('/current_weather')
def current_weather():

    # Hämtar stadens namn från query parameter
    city = request.args.get('city')

    # Anropar väderfunktionen från Weather_Api.py filen
    weather_data = get_weather(city)

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
    

#starta programmet
if __name__ == '__main__':
    # debug=True gör en auto refresh när saker förändras
    app.run(debug = True)