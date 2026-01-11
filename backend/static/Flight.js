// hämtar input-fälten
const fromInput = document.getElementById('whereFrom');
const toInput = document.getElementById('whereTo');

//hämtar listorna från HTML
const fromList = document.getElementById('fromList');
const toList = document.getElementById('toList');

// Funktion som kopplar både from och to fälten med en datalist
// och hämtar från Python
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
// och det finns ej på HTMLsida2.html. Denna Guard säkerställer att koden endast körs när det finns sökfält.

if (fromInput && fromList) {
    setupAutoSearch(fromInput, fromList);
}

if (toInput && toList) {
    setupAutoSearch(toInput, toList)
}


//hämtar och visar väder för en stad 
async function fetchAndDisplayWeather(city) {
    if (!city) return; // om 


    try{
        const response = await fetch(`/monthly_weather?city=${city}`);

        if(!response.ok){
            throw new Error("Weather request failed");
        }

        const weather = await response.json();

        //väljer var vi vill visa resultatet 
        const container = document.getElementById("weatherResult");

        container.innerHTML = `
            <h3>Väderstatistik för ${city}</h3>
            <p>🌞 Medel dagtemp: ${weather.avg_day} °C</p>
            <p>🌙 Medel natttemp: ${weather.avg_night} °C</p>
            <p>⬇️ Lägsta temp: ${weather.min_temp} °C</p>
            <p>⬆️ Högsta temp: ${weather.max_temp} °C</p>
        `;
        
    }
    catch (error) {
        console.error(error);
    }
    
}