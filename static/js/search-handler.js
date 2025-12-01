/**
 * AJAX-based search handler
 * Submits search form via fetch and updates content in place
 */

console.log('🔍 Search handler loaded');

document.addEventListener('DOMContentLoaded', function () {
    const searchForm = document.querySelector('.search-filter-bar');
    if (!searchForm) {
        console.log('No search form found');
        return;
    }

    // Intercept form submission
    searchForm.addEventListener('submit', async function (e) {
        e.preventDefault();

        const formData = new FormData(searchForm);
        const searchQuery = formData.get('q') || '';
        const order = formData.get('order') || 'popular';

        // Build URL with query params
        const url = new URL(window.location.origin + window.location.pathname);
        if (searchQuery) url.searchParams.set('q', searchQuery);
        url.searchParams.set('order', order);
        url.searchParams.set('page', '1');

        console.log('Fetching:', url.toString());

        try {
            // Show loading state
            const photoGrid =
                document.querySelector('.photo-grid') || document.querySelector('.gallery-grid');
            if (photoGrid) {
                photoGrid.style.opacity = '0.5';
                photoGrid.style.pointerEvents = 'none';
            }

            // Fetch the new page
            const response = await fetch(url.toString());
            const html = await response.text();

            // Parse the response
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Extract and update the photo grid
            const newPhotoGrid =
                doc.querySelector('.photo-grid') || doc.querySelector('.gallery-grid');
            if (photoGrid && newPhotoGrid) {
                photoGrid.innerHTML = newPhotoGrid.innerHTML;
                photoGrid.style.opacity = '1';
                photoGrid.style.pointerEvents = 'auto';
            }

            // Update load more button
            const loadMoreContainer = document.getElementById('load-more-container');
            const newLoadMoreContainer = doc.getElementById('load-more-container');
            if (loadMoreContainer && newLoadMoreContainer) {
                loadMoreContainer.outerHTML = newLoadMoreContainer.outerHTML;
            }

            // Update URL without reload
            window.history.pushState({}, '', url.toString());

            // Reinitialize lightbox if available
            if (window.initLightbox) {
                window.initLightbox();
            }

            // Reinitialize infinite scroll if available
            if (window.initInfiniteScroll) {
                window.initInfiniteScroll();
            }

            console.log('Search completed');
        } catch (error) {
            console.error('Search failed:', error);
            // Fall back to normal form submission
            searchForm.submit();
        }
    });

    // Also handle order change
    const orderSelect = document.getElementById('photo-order');
    if (orderSelect) {
        orderSelect.addEventListener('change', function () {
            searchForm.dispatchEvent(new Event('submit'));
        });
    }
});
