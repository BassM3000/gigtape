// Assuming you have an API endpoint for events (e.g., '/api/events/')
const apiUrl = 'http://localhost:8000/events/api/events/';
const eventContainer = document.querySelector('.event-content');
const loadMoreButton = document.querySelector('#load-more-button');
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

// Function to create an event card
function createEventCard(event) {
    const card = document.createElement('div');
    card.className = 'event-card';
    card.innerHTML = `
        <div class="event-img">
        <img src="${event.event_img || event.venue.venue_img}" onerror="handleImageError(this)">
        </div>
        <div class="event-info">
            <div class="event-name">
                ${event.event_name}
                <div class="event_date">${event.event_date}</div>
                <div class="event_venue">${event.venue.name}</div>
            </div>
        </div>
    `;
    // Add link to event website or venue website
    card.addEventListener('click', () => {
        window.location.href = event.website || event.venue.website;
    });
    return card;
}

// Function to load events
async function loadEvents() {
    const events = await fetchEvents();
    events.forEach((event) => {
        eventContainer.appendChild(createEventCard(event));
    });
    offset += events.length;
    // Disable "Load More" button if no more events
    loadMoreButton.disabled = events.length < 12;
}

// Load initial events
loadEvents();

// Event listener for "Load More" button
loadMoreButton.addEventListener('click', loadEvents);

function handleImageError(img, event) {
    // If event_img fails to load, use venue_img as fallback
    if (event && event.venue && event.venue.venue_img) {
        img.src = event.venue.venue_img;
    } else {
        // Fallback to a generic default image (you can customize this path)
        img.src = 'images/default_venue_image.png';
    }
}