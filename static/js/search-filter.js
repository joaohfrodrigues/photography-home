/**
 * Photo search and filter functionality
 */

function filterPhotos() {
    const searchInput = document.getElementById('photo-search')?.value.toLowerCase() || '';

    const photos = document.querySelectorAll('.photo-card');
    let visibleCount = 0;

    photos.forEach(photo => {
        const title = photo.dataset.title?.toLowerCase() || '';
        const tags = photo.dataset.tags?.toLowerCase() || '';
        const location = photo.dataset.location?.toLowerCase() || '';

        // Check if photo matches search
        const matchesSearch =
            !searchInput ||
            title.includes(searchInput) ||
            tags.includes(searchInput) ||
            location.includes(searchInput);

        // Show/hide based on search
        if (matchesSearch) {
            photo.style.display = '';
            photo.style.animation = 'fadeIn 0.3s ease-in';
            visibleCount++;
        } else {
            photo.style.display = 'none';
        }
    });

    // Update results count if element exists
    const resultsCount = document.getElementById('results-count');
    if (resultsCount) {
        resultsCount.textContent = `${visibleCount} photo${visibleCount !== 1 ? 's' : ''}`;
    }

    // Show "no results" message if needed
    updateNoResultsMessage(visibleCount);
}

function clearFilters() {
    // Reset search input
    const searchInput = document.getElementById('photo-search');

    if (searchInput) searchInput.value = '';

    // Show all photos
    filterPhotos();
}

function updateNoResultsMessage(visibleCount) {
    let noResultsMsg = document.getElementById('no-results-message');

    if (visibleCount === 0) {
        if (!noResultsMsg) {
            // Create the message element
            noResultsMsg = document.createElement('div');
            noResultsMsg.id = 'no-results-message';
            noResultsMsg.style.cssText = `
                text-align: center;
                padding: 4rem 2rem;
                color: rgba(255, 255, 255, 0.6);
                font-size: 1.1rem;
                grid-column: 1 / -1;
            `;
            noResultsMsg.innerHTML = `
                <p style="margin-bottom: 1rem; font-size: 1.5rem;">📷</p>
                <p>No photos match your search.</p>
                <p style="margin-top: 0.5rem; font-size: 0.9rem;">Try a different search term.</p>
            `;

            // Insert after photo grid
            const photoGrid = document.querySelector('.photo-grid');
            if (photoGrid) {
                photoGrid.parentNode.insertBefore(noResultsMsg, photoGrid.nextSibling);
            }
        }
        noResultsMsg.style.display = 'block';
    } else {
        if (noResultsMsg) {
            noResultsMsg.style.display = 'none';
        }
    }
}

// Add CSS animation for fade in
if (!document.getElementById('filter-animations')) {
    const style = document.createElement('style');
    style.id = 'filter-animations';
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    `;
    document.head.appendChild(style);
}
