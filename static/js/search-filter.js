/*
 * Adapted archived search-filter for SSR
 * - Provides client-side filtering UI and order changes by fetching server-rendered pages
 */

function filterPhotos() {
    const searchInput = document.getElementById('photo-search')?.value.toLowerCase() || '';

    // Query only .gallery-item (which includes both gallery and grid photos)
    const photos = document.querySelectorAll('.gallery-item');
    let visibleCount = 0;

    photos.forEach(photo => {
        const title = photo.dataset.title?.toLowerCase() || '';
        const tagsText = photo.dataset.tagsText?.toLowerCase() || '';
        const tags = photo.dataset.tags?.toLowerCase() || '';
        const location = photo.dataset.location?.toLowerCase() || '';
        const description = photo.dataset.description?.toLowerCase() || '';

        // Check if photo matches search
        const matchesSearch =
            !searchInput ||
            title.includes(searchInput) ||
            tagsText.includes(searchInput) ||
            tags.includes(searchInput) ||
            location.includes(searchInput) ||
            description.includes(searchInput);

        // Show/hide based on search
        if (matchesSearch) {
            // Show photo: reset display and ensure opacity is 1 (overrides initial opacity: 0)
            photo.style.display = '';
            photo.style.opacity = '1';
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

/**
 * Change photo ordering dynamically without page reload (SSR)
 * Fetches the server-rendered page with the new `order` param and replaces grids
 */
async function changePhotoOrder() {
    const orderSelect = document.getElementById('photo-order');
    const selectedOrder = orderSelect?.value || 'popular';

    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set('order', selectedOrder);
    url.searchParams.set('page', '1');
    window.history.pushState({}, '', url.toString());

    // Show loading state
    const photoGrid = document.querySelector('.photo-grid');
    if (!photoGrid) return;

    photoGrid.style.opacity = '0.5';
    photoGrid.style.pointerEvents = 'none';

    try {
        const res = await fetch(url.toString());
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const html = await res.text();

        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');

        // Replace columns or photo grid
        const columns = [
            document.getElementById('col-0'),
            document.getElementById('col-1'),
            document.getElementById('col-2'),
        ].filter(Boolean);
        const newCols = [
            doc.getElementById('col-0'),
            doc.getElementById('col-1'),
            doc.getElementById('col-2'),
        ].filter(Boolean);

        if (columns.length === 3 && newCols.length === 3) {
            // Replace each column's contents
            for (let i = 0; i < 3; i++) {
                columns[i].innerHTML = newCols[i].innerHTML;
            }
        } else {
            const newPhotoGrid =
                doc.querySelector('.photo-grid') || doc.querySelector('.gallery-grid');
            const photoGrid = document.querySelector('.photo-grid');
            if (photoGrid && newPhotoGrid) {
                photoGrid.innerHTML = newPhotoGrid.innerHTML;
            }
        }

        // Update results count
        const resultsCount = document.getElementById('results-count');
        const newResults = doc.getElementById('results-count');
        if (resultsCount && newResults) resultsCount.textContent = newResults.textContent;

        // Update or show load more container
        const loadMoreContainer = document.getElementById('load-more-container');
        const newLoadMoreContainer = doc.getElementById('load-more-container');
        if (loadMoreContainer && newLoadMoreContainer) {
            loadMoreContainer.outerHTML = newLoadMoreContainer.outerHTML;
        }

        // Reinitialize lightbox and infinite scroll
        if (window.initLightbox) window.initLightbox();
        if (window.initInfiniteScroll) window.initInfiniteScroll();
    } catch (error) {
        console.error('Error fetching photos:', error);
        // Fallback to page reload on error
        window.location.href = url.toString();
    } finally {
        photoGrid.style.opacity = '1';
        photoGrid.style.pointerEvents = 'auto';
    }
}

// Set the order selector to match URL parameter on page load
document.addEventListener('DOMContentLoaded', function () {
    const orderSelect = document.getElementById('photo-order');
    if (orderSelect) {
        const urlParams = new URLSearchParams(window.location.search);
        const orderParam = urlParams.get('order') || 'popular';
        orderSelect.value = orderParam;
    }
});
