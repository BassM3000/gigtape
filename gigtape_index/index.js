const apiUrl = 'http://localhost:8000/events/api/events/';
const eventContainer = document.querySelector('.event-content');
const loadMoreButton = document.querySelector('#load-more-button');
const imageUrls = ["./images/default_venue_image.png", "./images/default_yotalo.png", "./images/default_vastavirta.png",  "./images/default_tullikamari.png", "./images/default_telakka.jpg", "./images/default_tavaraasema.png", "./images/default_tamperetalo.jpg",  "./images/default_paappa.png", "./images/default_olympia.jpg", "./images/default_nokiaarena.jpg", "./images/default_glivelab.png"];
let offset = 0; // Initial offset for pagination


// Function to fetch events from the API
async function fetchEvents() {
    try {
        const response = await fetch(`${apiUrl}?offset=${offset}&limit=12`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching events:', error);
        return [];
    }
}

// Declare a function to change the background image based on the venue id or event_img
async function changeBackgroundImage(vId, eImgUrl, eventCard) {
    try {
        // Get the venue id from the API
        const venueId = vId;
        const eventImgUrl = eImgUrl;
        let backgroundImgIndex;

        // Check the venue id and assign the corresponding background image index
        if (venueId === 1) {
            backgroundImgIndex = 1;
        } else if (venueId === 2 || venueId === 3) {
            backgroundImgIndex = 2;
        } else if (venueId === 4 || venueId === 5) {
            backgroundImgIndex = 3;
        } else if (venueId === 6) {
            backgroundImgIndex = 4;
        } else if (venueId === 7) {
            backgroundImgIndex = 5;
        } else if ([8, 9, 10, 11, 12, 13, 14, 15].includes(venueId)) {
            backgroundImgIndex = 6;
        } else if (venueId === 16) {
            backgroundImgIndex = 7;
        } else if (venueId === 17) {
            backgroundImgIndex = 8;
        } else if (venueId === 18) {
            backgroundImgIndex = 9;
        } else if (venueId === 19) {
            backgroundImgIndex = 10;
        } else {
            // If the venue id is not valid, use a default background image index
            backgroundImgIndex = 0;
        }

        // Select the element that has the background image
        const element = eventCard.querySelector('.event-img');

        // Create an image object to see if the image is succesfully loaded
        const eventImg = new Image();
        eventImg.src = eventImgUrl;

        // Check for the load event
        eventImg.onload = function () {
            // Change the background image using the event_img URL or the default background image
            element.style.backgroundImage = `url(${eventImgUrl})`;
        };

        // Check for the error event
        eventImg.onerror = function () {
            // Change the background image using the event_img URL or the default background image
            element.style.backgroundImage = `url(${imageUrls[backgroundImgIndex]})`;
        };
        
    } catch (error) {
        // Log the error
        console.error('Error changing background image:', error);
    }
}

function formatDate(inputDate) {
    const date = new Date(inputDate);
    const day = date.getDate().toString().padStart(2, '0');
    const month = (date.getMonth() + 1).toString().padStart(2, '0'); // Months are zero-based
    const year = date.getFullYear();

    return `${day}.${month}.${year}`;
}

// Function to create an event card
function createEventCard(event) {
    const card = document.createElement('div');
    card.className = 'event-card';
    card.innerHTML = `
        <div class="event-img"></div>
        <div class="event-info">
            <div class="event-name">${event.event_name}</div>
            <div class="event-date">${formatDate(event.event_date)}</div>
            <div class="event-venue">${event.venue.name}</div>      
        </div>
    `;
    // Add link to event website or venue website
    card.addEventListener('click', () => {
        window.location.href = event.website || event.venue.website;
    });

    changeBackgroundImage(event.venue.id, event.event_img, card);

    return card;
}

// Function to load events
async function loadEvents() {
    try {
        const events = await fetchEvents();
        events.forEach((event) => {
            eventContainer.appendChild(createEventCard(event));
        });
        offset += events.length;
        // Disable "Load More" button if no more events
        loadMoreButton.disabled = events.length < 12;
    } catch (error) {
        console.error('Error loading events:', error);
    }
}

// Load initial events
loadEvents();

// Event listener for "Load More" button
loadMoreButton.addEventListener('click', loadEvents);
