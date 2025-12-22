import os
import re
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

# Create client ONCE, at module level
amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

def get_airports(keyword: str):
    if not keyword:
        return []
    try:
        resp = amadeus.reference_data.locations.get(
            keyword=keyword,
            subType="AIRPORT"
        )
        out = []
        for item in resp.data:
            out.append({
                "name": item.get("name", ""),
                "iataCode": item.get("iataCode", "")
            })
        return out
    except ResponseError as error:
        print(f"Amadeus Error (get_airports): {error}")
        return []

def _iata(value: str) -> str:
    if not value:
        return ""
    m = re.search(r"\(([A-Z]{3})\)", value.upper())
    return m.group(1) if m else value.strip().upper()

def search_flights(where_from: str, where_to: str, date: str, adults: int = 1, limit: int = 10):
    origin = _iata(where_from)
    dest = _iata(where_to)

    if not origin or not dest or not date:
        return []

    try:
        resp = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=dest,
            departureDate=date,
            adults=adults,
            max=limit,
            currencyCode="EUR"
        )

        flights = []
        for offer in resp.data:
            itin = offer["itineraries"][0]
            segs = itin["segments"]
            first = segs[0]
            last = segs[-1]

            flights.append({
                "price": offer["price"]["total"],
                "currency": offer["price"]["currency"],
                "depart_at": first["departure"]["at"],
                "depart_iata": first["departure"]["iataCode"],
                "arrive_at": last["arrival"]["at"],
                "arrive_iata": last["arrival"]["iataCode"],
                "stops": len(segs) - 1,
                "duration": itin.get("duration", "")
            })

        return flights

    except ResponseError as error:
        print(f"Amadeus Error (search_flights): {error}")
        return []
