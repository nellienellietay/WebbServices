import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from amadeus import Client, ResponseError

load_dotenv()

app = Flask(__name__)

# Startar Amadeus klienten med nycklarna

amadeus = Client (
    client_id = os.getenv('AMADEUS_API_KEY'),
    client_secret = os.getenv('AMADEUS_API_SECRET')
)


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

    #Skicka en tom lista om användaren inte skrivit något
    if not keyword:
        return jsonify([])

    try:
        # Vi ber amadeus hämta platserna som matchar vårt keyword
        response = amadeus.reference_data.locations.get(
            keyword = keyword,

            # Här ber vi om flyplatser så att vi inte får fram någonting annat
            subType = 'AIRPORT'
        )

        # jsonify gör om Python till JSON text som JS i browsern kan förstå
        return jsonify(response.data)

    except ResponseError as error:

        print(error)
        return jsonify([])

#starta programmet
if __name__ == '__main__':
    # debug=True gör en auto refresh när saker förändras
    app.run(debug = True)