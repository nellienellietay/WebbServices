from flask import Flask, render_template, request, jsonify
from Amadeus_Api import get_airports
from Weather_Api import get_weather

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
# anropar get_weather funtkionen som i sin tur hämtar och bearbetar väderdatan.
@app.route('/weather')
def weather():

    # Hämtar stadens namn från query parameter
    city = request.args.get('city')

    # Anropar väderfunktionen från Weather_Api.py filen
    weather_data = get_weather(city)

    # Felhantering
    if not weather_data:
        return jsonify({"Error": "Could not fetch weather data"}), 400
    
    return jsonify(weather_data)

#starta programmet
if __name__ == '__main__':
    # debug=True gör en auto refresh när saker förändras
    app.run(debug = True)