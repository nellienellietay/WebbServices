// hämtar input-fälten
const fromInput = document.getElementById('whereFrom');
const toInput = document.getElementById('whereTo');

//hämtar listorna från HTML
const fromList = document.getElementById('fromList');
const toList = document.getElementById('toList');

/**
 * Kopplar ett inmatningsfält till en <datalist> för autocomplete.
 * Lyssnar på input och hämtar flygplatsförslag från backend.
 * @param inputField - Input-fältet där användaren skriver
 * @param dataListElement - Datalist-elementet som ska fyllas
 */
function setupAutoSearch (inputField, dataListElement) {

    inputField.addEventListener('input', async function() {
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

            // Ta bort gamla resultat
            dataListElement.innerHTML = '';

            // Loopa genom airports som vi fick tillbaka
            airports.forEach(airport => {

                // Skapar ett <option> tag (dropdown)
                const option = document.createElement('option');

                // Vi sätter flyplatsen namn först och sedan
                // iata koden som är den unika koden för flygplatserna
                option.value = airport.iataCode;
                option.label = airport.name; // visar namnet i dropdown


                // Lägger till option i dataList containern
                dataListElement.appendChild(option);
            });
        } catch (error) {
            console.error('Error fetching airports:', error);
        }
    });
}

// Guard: autocomplete ska bara aktiveras på sidor där sökfält finns 
// och det finns ej på results.html. Denna Guard säkerställer att koden endast körs när det finns sökfält.

if (fromInput && fromList) {
    setupAutoSearch(fromInput, fromList);
}

if (toInput && toList) {
    setupAutoSearch(toInput, toList)
}
