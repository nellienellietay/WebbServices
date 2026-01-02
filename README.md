# WebbServices

## Viktigt om flygsökning (IATA-koder)

Flygsökningen i applikationen använder Amadeus Flight Offers API, som
kräver att flygplatser anges med giltiga IATA-koder (t.ex. ARN, BCN).

När man söker efter flyg måste därför både avrese- och destinationsflygplats
väljas från autocomplete-menyn i sökfältet.
Om man istället skriver in ett stadsnamn manuellt (t.ex. "Stockholm Arlanda")
kommer inga flyg att returneras, eftersom API:t endast accepterar IATA-koder.

Exempel på fungerande sökningar:
- ARN → BCN
- CPH → BCN
- CDG → BCN

Datum bör ligga minst 2–3 veckor framåt i tiden, då API:t annars kan returnera
tomma resultat.