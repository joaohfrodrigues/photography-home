/**
 * Photo search and filter functionality
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
 * Change photo ordering dynamically without page reload
 */
async function changePhotoOrder() {
    const orderSelect = document.getElementById('photo-order');
    const selectedOrder = orderSelect?.value || 'popular';

    // Update URL without reload
    const url = new URL(window.location);
    url.searchParams.set('order', selectedOrder);
    window.history.pushState({}, '', url.toString());

    // Show loading state
    const photoGrid = document.querySelector('.photo-grid');
    if (!photoGrid) return;

    photoGrid.style.opacity = '0.5';
    photoGrid.style.pointerEvents = 'none';

    try {
        // Fetch photos with new ordering (page 1, with 12 photos for initial load)
        const response = await fetch(`/api/latest-photos?order=${selectedOrder}&page=1`);
        const data = await response.json();

        if (data.photos && data.photos.length > 0) {
            // Clear all columns
            const columns = [
                document.getElementById('col-0'),
                document.getElementById('col-1'),
                document.getElementById('col-2'),
            ];

            columns.forEach(col => {
                if (col) col.innerHTML = '';
            });

            // Distribute photos to columns using height-aware algorithm
            const columnHeights = [0, 0, 0];

            data.photos.forEach((photo, index) => {
                const photoCard = createPhotoCard(photo, index);

                // Find shortest column
                const shortestIdx = columnHeights.indexOf(Math.min(...columnHeights));

                // Append to shortest column
                if (columns[shortestIdx]) {
                    columns[shortestIdx].appendChild(photoCard);
                }

                // Update height tracker
                const aspectRatio = photo.width / photo.height || 1;
                columnHeights[shortestIdx] += 1.0 / aspectRatio;
            });

            // Update results count
            const resultsCount = document.getElementById('results-count');
            if (resultsCount) {
                resultsCount.textContent = `${data.photos.length} photo${data.photos.length !== 1 ? 's' : ''}`;
            }

            // Update or show load more button
            const loadMoreBtn = document.getElementById('load-more-btn');
            const loadMoreContainer = document.getElementById('load-more-container');

            if (loadMoreBtn && loadMoreContainer) {
                loadMoreBtn.dataset.page = '2';
                loadMoreBtn.dataset.order = selectedOrder;
                loadMoreBtn.textContent = 'Load More Photos';
                loadMoreBtn.disabled = false;
                loadMoreContainer.style.display = data.has_more ? 'block' : 'none';

                // Reset infinite scroll state - reinitialize
                if (window.initInfiniteScroll) {
                    window.initInfiniteScroll();
                }
            }

            // Reinitialize lightbox with new photos
            if (window.initLightbox) {
                window.initLightbox();
            }
        }
    } catch (error) {
        console.error('Error fetching photos:', error);
        // Fallback to page reload on error
        window.location.href = url.toString();
    } finally {
        photoGrid.style.opacity = '1';
        photoGrid.style.pointerEvents = 'auto';
    }
}

// Note: createPhotoCard is now defined in infinite-scroll.js as createPhotoItem
// We import it via the global window object if needed, or just reference it directly
function createPhotoCard(photo, index) {
    // Use the unified createPhotoItem function from infinite-scroll.js if available
    if (typeof createPhotoItem === 'function') {
        return createPhotoItem(photo, index, 'grid');
    }

    // Fallback implementation (should not be needed if infinite-scroll.js is loaded)
    console.warn('createPhotoItem not found, using fallback');
    const div = document.createElement('div');
    div.className = 'photo-card gallery-item';
    div.textContent = 'Error: Photo creation function not available';
    return div;
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
