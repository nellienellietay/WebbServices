//hämtar och visar väder för en stad
async function fetchAndDisplayWeather(city) {
    if (!city) return; // om


    try{
        const response = await fetch(`/get_forecast?city=${city}`);

        if(!response.ok){
            throw new Error("Weather request failed");
        }

        const forecastList = await response.json();
        //väljer var vi vill visa resultatet
        const container = document.getElementById("weatherResult");
        const template = document.getElementById("weather-card-template");

        container.innerHTML = `<h3>5-dagars prognos för ${city}</h3>`;

        const cardsContainer = document.createElement('div');
        cardsContainer.className = 'forecast-container';

        forecastList.forEach(day => {
            const clone = template.content.cloneNode(true);
            clone.querySelector('.date').textContent = day.date;
            clone.querySelector('.temp').textContent = day.temp + "°C";
            clone.querySelector('.desc').textContent = day.description;
            clone.querySelector('.icon').src = `https://openweathermap.org/img/wn/${day.icon}@2x.png`;

            cardsContainer.appendChild(clone);

        });

        container.appendChild(cardsContainer);
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