import os
from pathlib import Path
from amadeus import Client, ResponseError
from dotenv import load_dotenv

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
root_dir = backend_dir

if (root_dir / ".env").exists():
    load_dotenv(dotenv_path=root_dir / ".env")
else:
    load_dotenv(dotenv_path=backend_dir / ".env")

load_dotenv()

#starta klient

print("AMADEUS_API_KEY:", os.getenv("AMADEUS_API_KEY"))

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