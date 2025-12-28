from flask import Flask, render_template, request, jsonify
from services.Amadeus_Api import get_airports, search_flights
from services.Weather_Api import get_weather, get_coordinates, get_daily_weather, calculate_statistics

app = Flask(__name__) 

# När man öppnar "http://127.0.0.1:5000/" körs denna funktionen
# Öppnar HTML filen för användaren
@app.route('/')
def search():
    return render_template('search.html') 


# Detta är en endpoint. Vår browser pratar med denna, inte med Amadeus direkt.
# T.ex /search_airports?keyword=HEA
@app.route("/search_airports")
def search_airports():
    keyword = request.args.get("keyword", "")
    try:
        return jsonify(get_airports(keyword)) # anropar funktionen i Amadeus_Api.py
    except Exception as e:
            return jsonify({"error": str(e)}), 500


# Öppnar nästa HTML sida och hämtar flygresultat
@app.route("/results")
def results():
    where_from = request.args.get("whereFrom", "")
    where_to = request.args.get("whereTo", "")
    departure_date = request.args.get("departureDate", "")
    return_date = request.args.get("returnDate", "")

    if not (where_from and where_to and departure_date and return_date):
        return render_template("HTMLsida2.html", flights=[], error="Missing input.")

    flights_all = []
    try:
        dep = search_flights(where_from, where_to, departure_date, adults=1, limit=10)
        for f in dep:
            f["leg"] = "Departure"
            f["search_date"] = departure_date
        flights_all.extend(dep)

        ret = search_flights(where_to, where_from, return_date, adults=1, limit=10)
        for f in ret:
            f["leg"] = "Return"
            f["search_date"] = return_date
        flights_all.extend(ret)

        return render_template("HTMLsida2.html", flights=flights_all, error=None)

    except Exception as e:
        return render_template("HTMLsida2.html", flights=[], error=str(e))


# API endpoint för att hämta flygdata i JSON-format
@app.route("/api/flights")
def api_flights():
    where_from = request.args.get("whereFrom", "")
    where_to = request.args.get("whereTo", "")
    date = request.args.get("date", "")
    return jsonify(search_flights(where_from, where_to, date, adults=1, limit=10))



# Detta är en endpoint för vårt väder-API som frontend pratar med. Denna endpoint
# anropar get_weather funtkionen som i sin tur hämtar och bearbetar väderdatan.
@app.route('/current_weather')
def current_weather():
    city = request.args.get('city')
    weather_data = get_weather(city)

    if not weather_data:
        return jsonify({"Error": "Could not fetch weather data"}), 400

    return jsonify(weather_data)


@app.route('/monthly_weather')
def monthly_weather():
    city = request.args.get('city')

    lat, lon = get_coordinates(city)  # koordinater för staden
    daily_data = get_daily_weather(lat, lon)  # hämta dagligt väder
    stats = calculate_statistics(daily_data)  # räkna ut statistik

    return jsonify(stats)


# starta programmet
if __name__ == '__main__':
    app.run(debug=True)
