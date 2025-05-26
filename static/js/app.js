// Helper function to create a product card
function createProductCard(item) {
    const card = document.createElement('div');
    card.className = 'flex h-full flex-1 flex-col gap-4 rounded-lg min-w-40';

    const imageDiv = document.createElement('div');
    imageDiv.className = 'w-full bg-center bg-no-repeat aspect-square bg-cover rounded-xl flex flex-col';
    imageDiv.style.backgroundImage = `url("${item.image_url || 'https://via.placeholder.com/150'}")`; // Placeholder if no image

    const textDiv = document.createElement('div');
    const nameP = document.createElement('p');
    nameP.className = 'text-[#181411] text-base font-medium leading-normal';
    nameP.textContent = item.name;

    const priceP = document.createElement('p');
    priceP.className = 'text-[#887563] text-sm font-normal leading-normal';
    priceP.textContent = `$${item.price.toFixed(2)}`;

    textDiv.appendChild(nameP);
    textDiv.appendChild(priceP);
    card.appendChild(imageDiv);
    card.appendChild(textDiv);

    return card;
}

// Fetch and display Featured Artist
async function fetchFeaturedArtist() {
    try {
        const response = await fetch('/api/artists/featured');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const artist = await response.json();

        if (artist && artist.id) { // Check if an artist was actually returned
            const featuredArtistSection = document.getElementById('featured-artist-section');
            const featuredArtistName = document.getElementById('featured-artist-name');

            if (featuredArtistSection && artist.image_url) {
                featuredArtistSection.style.backgroundImage = `linear-gradient(0deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0) 25%), url("${artist.image_url}")`;
            }
            if (featuredArtistName) {
                featuredArtistName.textContent = `Featured Artist: ${artist.name}`;
            }
        } else {
             console.log('No featured artist found or artist data incomplete.');
             // Optionally, hide the section or set a default state
             const featuredArtistName = document.getElementById('featured-artist-name');
             if (featuredArtistName) {
                featuredArtistName.textContent = 'No featured artist currently.';
             }
        }
    } catch (error) {
        console.error('Error fetching featured artist:', error);
    }
}

// Fetch and display ceramics by category
async function fetchCeramics(category, containerId, headingText = null) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container with id ${containerId} not found.`);
        return;
    }
    container.innerHTML = ''; // Clear existing content

    try {
        const response = await fetch(`/api/ceramics?category=${category}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const items = await response.json();

        if (items.length === 0) {
            // Optionally display a message if no items are found for that category
            const messageP = document.createElement('p');
            messageP.textContent = `No items found in ${category.replace('-', ' ')}.`;
            messageP.className = 'text-gray-500 px-4';
            container.appendChild(messageP);
        } else {
            items.forEach(item => {
                const card = createProductCard(item);
                container.appendChild(card);
            });
        }
        
        // Update heading if a new heading is provided (used for search results)
        if (headingText && container.previousElementSibling && container.previousElementSibling.tagName === 'H3') {
            container.previousElementSibling.textContent = headingText;
        }

    } catch (error) {
        console.error(`Error fetching ${category} ceramics:`, error);
        const errorP = document.createElement('p');
        errorP.textContent = `Could not load ${category.replace('-', ' ')}. Please try again later.`;
        errorP.className = 'text-red-500 px-4';
        container.appendChild(errorP);
    }
}

// Implement Search Functionality
async function searchCeramics(query) {
    const newArrivalsContainer = document.getElementById('new-arrivals-container');
    const bestSellersContainer = document.getElementById('best-sellers-container');
    const newArrivalsHeading = document.querySelector('#new-arrivals-container').previousElementSibling; // Assuming H3 is direct sibling
    const bestSellersHeading = document.querySelector('#best-sellers-container').previousElementSibling;


    if (!newArrivalsContainer || !bestSellersContainer) {
        console.error('Cannot find product containers for search.');
        return;
    }

    newArrivalsContainer.innerHTML = '';
    bestSellersContainer.innerHTML = ''; // Clear best sellers too

    // Hide Best Sellers section during search or repurpose it.
    // For simplicity, we'll repurpose New Arrivals and hide Best Sellers section elements.
    if (bestSellersHeading) bestSellersHeading.style.display = 'none';
    bestSellersContainer.style.display = 'none';


    try {
        const response = await fetch(`/api/ceramics?search=${encodeURIComponent(query)}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const items = await response.json();

        if (newArrivalsHeading && newArrivalsHeading.tagName === 'H3') {
            newArrivalsHeading.textContent = `Search Results for "${query}"`;
        }
        
        if (items.length === 0) {
            const messageP = document.createElement('p');
            messageP.textContent = `No items found matching "${query}".`;
            messageP.className = 'text-gray-500 px-4';
            newArrivalsContainer.appendChild(messageP);
        } else {
            items.forEach(item => {
                const card = createProductCard(item);
                newArrivalsContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Error during search:', error);
        const errorP = document.createElement('p');
        errorP.textContent = `Error searching for "${query}". Please try again.`;
        errorP.className = 'text-red-500 px-4';
        newArrivalsContainer.appendChild(errorP);
        if (newArrivalsHeading && newArrivalsHeading.tagName === 'H3') {
           newArrivalsHeading.textContent = 'Search Results';
        }
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchFeaturedArtist();
    fetchCeramics('new-arrival', 'new-arrivals-container');
    fetchCeramics('best-seller', 'best-sellers-container');

    const searchInput = document.querySelector('input[placeholder="Search for ceramics"]');
    if (searchInput) {
        searchInput.addEventListener('keypress', (event) => {
            if (event.key === 'Enter' && searchInput.value.trim() !== '') {
                searchCeramics(searchInput.value.trim());
            }
        });
        // Optional: search as user types (debounced) or add a search button
        // For now, only Enter key press
    }
});
