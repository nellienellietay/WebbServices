import os
import re
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# -----------------------
# Load .env from backend/.env
# -----------------------
backend_dir = Path(__file__).resolve().parent.parent  # .../backend
load_dotenv(dotenv_path=backend_dir / ".env")

KEY_OK = bool(os.getenv("AMADEUS_API_KEY"))
SECRET_OK = bool(os.getenv("AMADEUS_API_SECRET"))
print("KEY loaded:", KEY_OK)
print("SECRET loaded:", SECRET_OK)

BASE_URL = "https://test.api.amadeus.com"  # change only if you truly use production

_token_cache = {
    "access_token": None,
    "expires_at": 0.0,
}


def _iata(value: str) -> str:
    if not value:
        return ""
    v = value.strip().upper()

    if len(v) == 3 and v.isalpha():
        return v

    m = re.search(r"\(([A-Z]{3})\)", v)
    if m:
        return m.group(1)

    return ""


def _get_access_token() -> str:
    now = time.time()
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    client_id = os.getenv("AMADEUS_API_KEY")
    client_secret = os.getenv("AMADEUS_API_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Missing AMADEUS_API_KEY or AMADEUS_API_SECRET")

    url = f"{BASE_URL}/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }

    r = requests.post(url, data=data, timeout=15)
    if r.status_code != 200:
        raise RuntimeError(f"Token request failed: {r.status_code} - {r.text[:300]}")

    payload = r.json()
    access_token = payload.get("access_token")
    expires_in = payload.get("expires_in", 1800)

    if not access_token:
        raise RuntimeError(f"Token response missing access_token - {payload}")

    # small safety margin
    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = now + int(expires_in) - 30
    return access_token


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {_get_access_token()}"}


def get_airports(keyword: str):
    if not keyword:
        return []

    url = f"{BASE_URL}/v1/reference-data/locations"
    params = {
        "keyword": keyword,
        "subType": "AIRPORT",
        "view": "LIGHT"
    }

    r = requests.get(url, headers=_auth_headers(), params=params, timeout=15)
    if r.status_code != 200:
        # return [] for autocomplete, but with a visible server log
        print("get_airports failed:", r.status_code, "-", r.text[:300])
        return []

    data = r.json().get("data", [])
    out = []
    for item in data:
        out.append({
            "name": item.get("name",),
            "iataCode": item.get("iataCode"),
            "geoCode": item.get("geoCode")
        })
    return out


def search_flights(where_from: str, where_to: str, date: str, adults: int = 1, limit: int = 10):
    origin = _iata(where_from)
    dest = _iata(where_to)

    if len(origin) != 3 or len(dest) != 3:
        raise ValueError(f"Invalid IATA. origin='{origin}', dest='{dest}'")

    if not date:
        raise ValueError("Missing departure date")

    url = f"{BASE_URL}/v2/shopping/flight-offers"
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": dest,
        "departureDate": date,
        "adults": adults,
        "max": limit,
        "currencyCode": "EUR",
    }

    r = requests.get(url, headers=_auth_headers(), params=params, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"Flight search failed: {r.status_code} - {r.text[:400]}")

    offers = r.json().get("data", [])
    print("Amadeus offers:", len(offers))

    flights = []
    for offer in offers:
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            continue
        itin = itineraries[0]
        segs = itin.get("segments", [])
        if not segs:
            continue

        first = segs[0]
        last = segs[-1]

        flights.append({
            "price": offer.get("price", {}).get("total"),
            "currency": offer.get("price", {}).get("currency"),
            "depart_at": first.get("departure", {}).get("at"),
            "depart_iata": first.get("departure", {}).get("iataCode"),
            "arrive_at": last.get("arrival", {}).get("at"),
            "arrive_iata": last.get("arrival", {}).get("iataCode"),
            "stops": max(len(segs) - 1, 0),
            "duration": itin.get("duration", ""),
        })

    return flights

def get_airport_by_iata(iata: str):
    """
    Hämtar exakt flygplats via IATA-kod (tex BCN) så vi får geoCode (lat/lon). Detta behövs 
    för mashupen eftersom OpenWeather kräver koordinater för att hämta aktuellt väder.
    """
    iata = _iata(iata)
    if not iata or len(iata) != 3:
        return None

    url = f"{BASE_URL}/v1/reference-data/locations"
    params = {
        "keyword": iata,
        "subType": "AIRPORT",
        "view": "FULL",
        "page[limit]": 10
    }

    r = requests.get(url, headers=_auth_headers(), params = params, timeout=15)
    if r.status_code != 200:
        print("get_airport_by_iata failed:", r.status_code, r.text[:300])
        return None

    data = r.json().get("data", [])
    if not data:
        return None
    
    # Välj träff som matchar exakt IATA-kod + AIRPORT och som faktiskt har geoCode.
    match = next(
        (x for x in data
         if x.get("iataCode") == iata
         and x.get("subType") == "AIRPORT"
         and x.get("geoCode")),
        None
    )

    if not match:
        return None

    return {
        "iataCode": match.get("iataCode"),
        "geoCode": match.get("geoCode"),
        "name": match.get("name"),
        "id": match.get("id"),
    }