# WebbServices

## Viktigt om flygsökning (IATA-koder)

Flygsökningen i applikationen använder Amadeus Flight Offers API, som
kräver att flygplatser anges med giltiga IATA-koder (t.ex. ARN, BCN).

När man söker efter flyg måste därför både avrese- och destinationsflygplats
väljas från autocomplete-menyn i sökfältet.
Om man istället skriver in ett stadsnamn manuellt (tex "Stockholm Arlanda")
kommer inga flyg att returneras, eftersom API:t just nu endast accepterar IATA-koder.
