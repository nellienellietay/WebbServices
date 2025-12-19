import os
from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

#starta klient

amadeus = Client (
    client_id = os.getenv('AMADEUS_API_KEY'),
    client_secret = os.getenv('AMADEUS_API_SECRET')
)


# Hämtar data och ger en lista
def get_airports(keyword):

    if not keyword:
        return []

    try:
        response = amadeus.reference_data.locations.get(
            keyword = keyword,
            subType = 'AIRPORT'
        )

        return response.data
    except ResponseError as error:
        print (f"Amadeus Error: {error}")
        return []