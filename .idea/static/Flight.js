const fromInput = document.getElementById('fromInput');
const dataList = document.getElementById('airportList');

// Vi lyssnar på input events, detta körs varje gång användaren skriver in en bokstav
fromInput.addEventListener('input', async function() {

    const keyword = this.value;

    // Vi söker bara efter flygplatser om användaren har skrivit in 3 bokstäver
    // Annars blir det onödiga API calls
    if (keyword.length < 3)
        return;

    try {
        // Skickar keyword till vår python "/search_airports"
        const response = await fetch(`/search_airports?keyword=${keyword}`);

        // Gör om text till ett användbart JS objekt
        const airports = await response.json();

        // Ta bort gamla sökningar
        dataList.innerHTML = '';

        // Loopa genom airports som vi fick tillbaka
        airports.forEach(airport => {

            // Skapar ett <option> tag (dropdown)
            const option = document.createElement('option');

            // Vi sätter flyplatsen namn först och sedan
            // iata koden som är den unika koden för flygplatserna
            option.value = `${airport.name} (${airport.iataCode})`;

            // Lägger till option i dataList containern
            dataList.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching airports:', error);
    }
});