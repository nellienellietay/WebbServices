from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from services.Amadeus_Api import get_airports, search_flights, get_airport_by_iata
from services.Weather_Api import get_current_weather, get_coordinates, get_daily_weather, calculate_statistics, get_forecast

def get_destination_weather(arrive_iata):
    """
    Mashup-koppling: tar destinationens IATA-kod från flygsökningen, hämtar flygplatsens
    koordinater via Amadeus (geoCode) och använder sedan OpenWeather för att hämta
    aktuellt väder för destinationen.
    """
    airport = get_airport_by_iata(arrive_iata)
    if not airport:
        return None

    geo = airport.get("geoCode")
    if not geo:
        return None

    lat = geo.get("latitude")
    lon = geo.get("longitude")
    if lat is None or lon is None:
        return None
    
    weather = get_current_weather(lat, lon)
    if not weather:
        return None

    weather["place_label"] = airport.get("name") or arrive_iata
    return weather

app = Flask(__name__)
app.secret_key = "dev-secret" 

# När man öppnar "http://127.0.0.1:5000/" körs denna funktionen
# Öppnar HTML filen för användaren
@app.route('/')
def search():
    return render_template('search.html') 

# Detta är en endpoint. Vår browser pratar med denna, inte med Amadeus direkt.
# T.ex GET /api/v1/airports/search?keyword=HEA
@app.route("/api/v1/airports/search")
def search_airports():
    keyword = request.args.get("keyword", "").strip()
    if len(keyword) < 3:
        return jsonify({"error": "keyword must be at least 3 characters"}), 400

    try:
        return jsonify(get_airports(keyword)), 200
    except Exception:
        return jsonify({"error": "failed to fetch airports"}), 503

# Öppnar nästa HTML sida och hämtar flygresultat
@app.route("/search-results")
def results():
    where_from = request.args.get("whereFrom", "").strip()
    where_to = request.args.get("whereTo", "").strip()
    departure_date = request.args.get("departureDate", "").strip()
    return_date = request.args.get("returnDate", "").strip()

    if not (where_from and where_to and departure_date and return_date):
        return render_template("results.html", flights=[], error="Missing input.")

    flights_all = []
    try:
        dep = search_flights(where_from, where_to, departure_date, adults=1, limit=10)

        print(f"DEBUG: Söker flyg från {where_from} till {where_to} datum {departure_date}")
        print(f"DEBUG: Hittade {len(dep)} avgångar (Departure)")


        for f in dep:
            f["leg"] = "Departure"
            f["search_date"] = departure_date
        flights_all.extend(dep)

        ret = search_flights(where_to, where_from, return_date, adults=1, limit=10)

        print(f"DEBUG: Söker retur från {where_to} till {where_from} datum {return_date}")
        print(f"DEBUG: Hittade {len(ret)} returresor (Return)")

        for f in ret:
            f["leg"] = "Return"
            f["search_date"] = return_date
        flights_all.extend(ret)
        
# om inga flyg hittas, visa ett tydligt felmeddelande
        if not flights_all:
            return render_template("results.html", flights=[], error="No flights found for your search.")

        ## Hämtar aktuellt väder för destinationen
        weather = None
        if flights_all:
            weather = get_destination_weather(flights_all[0]["arrive_iata"])

            destination_label = where_to  # fallback = IATA-kod

        if flights_all:
            airport = get_airport_by_iata(flights_all[0]["arrive_iata"])
            if airport:
                destination_label = (
                    airport.get("address", {}).get("cityName")
                    or airport.get("name")
                    or flights_all[0]["arrive_iata"]
                )
        
        session["flights"] = flights_all
        session["last_search"] = {
            "whereFrom": where_from,
            "whereTo": where_to,
            "departureDate": departure_date,
            "returnDate": return_date
        }

        session.pop("selected_departure_id", None)
        session.pop("selected_return_id", None)

        print("DEBUG destination_label =", destination_label)


        return render_template(
            "results.html",
            flights=flights_all, 
            weather=weather,
            destination_label=destination_label,
            error=None)

    except Exception as e:
        print("ERROR in /search-results:", str(e))
        return render_template("results.html", flights=[], error="Something went wrong. Please try again.")

# API endpoint för att hämta flygdata i JSON-format
@app.route("/api/v1/flights")
def api_flights():
    where_from = request.args.get("whereFrom", "").strip()
    where_to = request.args.get("whereTo", "").strip()
    date = request.args.get("date", "").strip()
    if not (where_from and where_to and date):
        return jsonify({"error": "whereFrom, whereTo and date are required"}), 400

    try:
        flights = search_flights(where_from, where_to, date, adults=1, limit=10)
        return jsonify(flights), 200
    except Exception as e:
        print("ERROR in /api/v1/flights:", str(e))
        return jsonify({"error": "Failed to fetch flights"}), 503
    


# Detta är en endpoint för vårt väder-API som frontend pratar med. Denna endpoint
# anropar get_current_weather funtkionen som i sin tur hämtar och bearbetar väderdatan.
# exempelurl: GET /api/v1/weather/current?city=Stockholm
@app.route('/api/v1/weather/current')
def current_weather():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400
                           
    weather_data = get_current_weather(lat, lon)

    if not weather_data:
        return jsonify({"Error": "Could not fetch weather data"}), 400

    return jsonify(weather_data)

# GET /api/v1/weather/forecast?city=Stockholm
@app.route('/api/v1/weather/forecast')
def get_forecast_route():
    location_input = request.args.get('city').strip()
    
# saknad input = 400
    if not location_input:
        return jsonify({"error": "city is required"}), 400

    lat=None
    lon=None

    if len(location_input) == 3: 
        airport_data = get_airport_by_iata(location_input)
        if airport_data and "geoCode" in airport_data:
            lat = airport_data["geoCode"]["latitude"]
            lon = airport_data["geoCode"]["longitude"]
            print(f"DEBUG: Hittade flygplatskoordinater via Amadeus: {lat}, {lon}")
            
#annars försök via stadsnamn
    if lat is None:
        lat,lon = get_coordinates(location_input)
        print(f"DEBUG: Sökte via stadsnamn för {location_input}: {lat}, {lon}")
        

    if lat is None:
        return jsonify({"error": "City not found"}), 404

    forecast_data = get_forecast(lat, lon)

    return jsonify(forecast_data)


@app.route('/api/v1/weather/monthly')
def monthly_weather():
    city = request.args.get('city')

    lat, lon = get_coordinates(city)  # koordinater för staden
    daily_data = get_daily_weather(lat, lon)  # hämta dagligt väder
    stats = calculate_statistics(daily_data)  # räkna ut statistik

    return jsonify(stats)

# mashup-endpoint som kombinerar flyg & aktuellt väder
# exempel: /api/v1/mashup/airports-with-weather?keyword=STO
@app.route('/api/v1/mashup/airports-with-weather')
def search_airports_with_weather():

    # hämtar sökordet som användaren skickar med i URL:en (t.ex. STO)
    keyword = request.args.get('keyword')

    # hämtar flygplatser baserat på keyword
    airports = get_airports(keyword)

    results = []

    for airport in airports: 
        geo = airport.get("geoCode")
        if not geo: 
            continue

        lat = geo.get("latitude")
        lon = geo.get("longitude")

        if lat is None or lon is None:
            continue

        weather = get_current_weather(lat, lon)
        if not weather:
            continue

        results.append({
            "airport": airport,
            "weather": weather
        })

    return jsonify(results)

@app.route("/actions/select-flight")
def select_flight():
    flight_id = request.args.get("flight_id", type=int)
    leg = request.args.get("leg", "")
    last_search = session.get("last_search")

    flights = session.get("flights", [])
    if flight_id is None or flight_id < 0 or flight_id >= len(flights):
        return "Invalid flight selecetion.", 400
    
    if leg == "Departure":
        session["selected_departure_id"] = flight_id
    elif leg == "Return":
        session["selected_return_id"] = flight_id
    else:
        return "Invalid.", 400
    
    if session.get("selected_departure_id") is not None and session.get("selected_return_id") is not None:
        return redirect(url_for("trip_summary"))
    
    return redirect(url_for("results", **last_search)) if last_search else redirect(url_for("search"))

@app.route("/trip-summary")
def trip_summary():
    flights = session.get("flights", [])
    dep_id = session.get("selected_departure_id")
    ret_id = session.get("selected_return_id")

    if dep_id is None or ret_id is None:
        return redirect(url_for("results", **session["last_search"])) if session.get("last_search") else redirect(url_for("search"))

    if not flights or dep_id >= len(flights) or ret_id >= len(flights):
        return redirect(url_for("results", **session["last_search"])) if session.get("last_search") else redirect(url_for("search"))

    dep = flights[dep_id]
    ret = flights[ret_id]

    total_price = None
    try:
        total_price = float(dep["price"]) + float(ret["price"])
    except:
        pass
    
    return render_template("trip_summary.html", dep=dep, ret=ret, total_price=total_price)

# starta programmet
if __name__ == '__main__':
    app.run(debug=True)