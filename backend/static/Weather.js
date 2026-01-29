/**
 * Uppdaterar alla flygkort i listan med ett "Sol-index"
 * Funktionen kombinerar både väderdata (medeltemperaturen) med flygets pris
 * för att räkna ut ett betyg mellan 1 till 5 solar.
 * @param avgTemp - Medeltemperaturen för destinationen de kommande 5 dagarna
 */
function updateFlightRatings(avgTemp) {
    const ratingBoxes = document.querySelectorAll('.sun-rating');

    ratingBoxes.forEach(box => {

        //Hämta priset som vi sparat i data-attributet i HTML
        const price = parseFloat(box.getAttribute('data-price'));

        if (!price) return;

        let score = 0;

        // Mashup logik för pris och väder
        // Baspoäng för värme (Från openWeatherMap)
        // Steg 1:
        if (avgTemp >= 25) score = 5;
        else if (avgTemp >= 20) score = 4;
        else if (avgTemp >= 15) score = 3;
        else score = 2;

        // Bonus/avrag baserat på pris (Från Amadeus)
        // Steg 2:
        if (price < 1500) {
            score += 1; // Billigt flyg ger bonus
        } else if (price > 4000) {
            score -= 1; // Dyrt flyg ger avdrag
        } else if (price > 6000) {
            score -= 2;
        }

        // För att säkerställa att det inte går under 1 eller över 5
        if (score > 5) score = 5;
        if (score < 1) score = 1;

        //HTML för solarna
        let sunsHTML = "";
        for (let i = 0; i < 5; i++) {
            if (i < score) {
                sunsHTML += "☀️";
            } else {
                sunsHTML += "<span style='opacity:0.3'>☀️</span>" // Genomskinlig sol
            }
        }

        // Resultatet läggs i DOM:en
        box.innerHTML = `<span style="font-size: 18px;">${sunsHTML}</span> <span style="font-size:12px; color:gray;">(Sol-index)</span>`;
    });
}

/**
 * Hämtar 5-dagars väderprognos för en specifik stad/flygplatskod.
 * Renderar väderkorten och triggar igång rating-funktionen
 * @param city - IATA kod eller stadsnamn (T.ex "BCN" eller Barcelona)
 * @returns {Promise<void>}
 */
async function fetchAndDisplayWeather(city) {
    if (!city) return;

    try {
        const container = document.getElementById("weatherResult");

        const response = await fetch(`/api/v1/weather/forecast?city=${encodeURIComponent(city)}`);

        if (!response.ok) {
            if (container) {
                if (response.status === 400) container.innerHTML = "<p>Missing destination.</p>";
                else if (response.status === 404) container.innerHTML = "<p>Destination not found.</p>";
                else container.innerHTML = "<p>Weather service unavailable.</p>";
            }
            return;
        }

        const forecastList = await response.json();

        const template = document.getElementById("weather-card-template");

        if (!template) {
            console.log("Hittade ingen template");
            return
        }

        container.innerHTML = `<h3>5-dagars prognos för ${city}</h3>`;

        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'forecast-container';

        let totalTemp = 0;

        forecastList.forEach(day => {
            const clone = template.content.cloneNode(true);
            clone.querySelector('.date').textContent = day.date;
            clone.querySelector('.temp').textContent = day.temp + "°C";
            clone.querySelector('.desc').textContent = day.description;
            clone.querySelector('.icon').src = `https://openweathermap.org/img/wn/${day.icon}@2x.png`;

            cardsContainer.appendChild(clone);

            totalTemp += day.temp;
        });

        container.appendChild(cardsContainer);

        if (forecastList.length > 0) {
            const averageTemp = Math.round(totalTemp / forecastList.length);
            updateFlightRatings(averageTemp)
        }
    }
    catch (error) {
        console.error(error);
    }
}


// Initiera vädersökning om vi är på resultatsidan
const destinationInput = document.getElementById('destinationCity');
if (destinationInput) {
    const city = destinationInput.value;
    console.log("Hämtar väder för: ", city)
    fetchAndDisplayWeather(city)
}