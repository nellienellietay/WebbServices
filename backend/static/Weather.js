

function updateFlightRatings(avgTemp) {
    const ratingBoxes = document.querySelectorAll('.sun-rating');

    ratingBoxes.forEach(box => {

        const price = parseFloat(box.getAttribute('data-price'));

        if (!price) return;

        let score = 0;

        // Mashup logik för pris och väder
        // Baspoäng för värme
        if (avgTemp >= 25) score = 5;
        else if (avgTemp >= 20) score = 4;
        else if (avgTemp >= 15) score = 3;
        else score = 2;

        // Bonus poäng för pris
        if (price < 1500) {
            score += 1;
        } else if (price > 4000) {
            score -= 1;
        } else if (price > 6000) {
            score -= 2;
        }

        if (score > 5) score = 5;
        if (score < 1) score = 1;

        let sunsHTML = "";
        for (let i = 0; i < 5; i++) {
            if (i < score) {
                sunsHTML += "☀️";
            } else {
                sunsHTML += "<span style='opacity:0.3'>☀️</span>"
            }
        }
        box.innerHTML = `<span style="font-size: 18px;">${sunsHTML}</span> <span style="font-size:12px; color:gray;">(Sol-index)</span>`;
    });
}

//hämtar och visar väder för en stad
async function fetchAndDisplayWeather(city) {
    if (!city) return;


    try{
        const response = await fetch(`/get_forecast?city=${city}`);

        if(!response.ok){
            throw new Error("Weather request failed");
        }

        const forecastList = await response.json();
        //väljer var vi vill visa resultatet
        const container = document.getElementById("weatherResult");
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

const destinationInput = document.getElementById('destinationCity');

if (destinationInput) {
    const city = destinationInput.value;
    console.log("Hämtar väder för: ", city)
    fetchAndDisplayWeather(city)
}