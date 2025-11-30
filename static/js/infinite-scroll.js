// Infinite scroll for collection galleries
console.log('🔄 Infinite scroll script loaded');

let isLoading = false;
let currentPage = 1;

function initInfiniteScroll() {
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (!loadMoreBtn) {
        console.log('No load more button found');
        return;
    }

    const collectionId = loadMoreBtn.dataset.collectionId;
    currentPage = parseInt(loadMoreBtn.dataset.page) || 2;

    console.log(
        `Infinite scroll initialized for collection ${collectionId}, starting page ${currentPage}`
    );

    // Click handler for manual load more
    loadMoreBtn.addEventListener('click', () => {
        loadMore(collectionId);
    });

    // Intersection Observer for automatic loading
    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !isLoading) {
                    console.log('Load more button in view, auto-loading...');
                    loadMore(collectionId);
                }
            });
        },
        {
            rootMargin: '200px', // Start loading 200px before button is visible
        }
    );

    observer.observe(loadMoreBtn);
}

async function loadMore(collectionId) {
    if (isLoading) return;

    isLoading = true;
    const loadMoreBtn = document.getElementById('load-more-btn');
    const originalText = loadMoreBtn.textContent;

    loadMoreBtn.textContent = 'Loading...';
    loadMoreBtn.disabled = true;

    try {
        console.log(`Loading page ${currentPage} for collection ${collectionId}`);

        const response = await fetch(`/api/collection/${collectionId}/photos?page=${currentPage}`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        console.log(`Loaded ${data.photos.length} photos, has_more: ${data.has_more}`);

        // Append new photos to gallery
        appendPhotosToGallery(data.photos);

        // Update page number
        currentPage++;
        loadMoreBtn.dataset.page = currentPage;

        // Hide button if no more photos
        if (!data.has_more) {
            const container = document.getElementById('load-more-container');
            if (container) {
                container.remove();
            }
            console.log('No more photos to load');
        } else {
            loadMoreBtn.textContent = originalText;
            loadMoreBtn.disabled = false;
        }
    } catch (error) {
        console.error('Error loading more photos:', error);
        loadMoreBtn.textContent = 'Error - Try Again';
        loadMoreBtn.disabled = false;
    } finally {
        isLoading = false;
    }
}

function appendPhotosToGallery(photos) {
    const galleryGrid = document.getElementById('gallery-grid');
    const currentCount = galleryGrid.querySelectorAll('.gallery-item').length;

    photos.forEach((photo, idx) => {
        const photoIndex = currentCount + idx;
        const galleryItem = createGalleryItem(photo, photoIndex);
        galleryGrid.appendChild(galleryItem);
    });

    // Re-initialize lightbox for new items
    if (window.initLightbox) {
        window.initLightbox();
    }

    console.log(`Appended ${photos.length} new photos to gallery`);
}

function createGalleryItem(photo, index) {
    const div = document.createElement('div');
    div.className = 'gallery-item';
    div.style.aspectRatio = `${photo.width / photo.height}`;

    // Extract photographer info from nested user object or direct properties
    const photographer = photo.user?.name || photo.photographer || 'Unknown';
    const photographerUrl = photo.user?.profile_url || photo.photographer_url || '';
    const unsplashUrl = photo.links?.html || photo.unsplash_url || '';
    const downloadLocation = photo.links?.download_location || photo.download_location || '';

    // Set data attributes
    div.dataset.index = index;
    div.dataset.photoId = photo.id;
    div.dataset.downloadLocation = downloadLocation;
    div.dataset.description = photo.description || '';
    div.dataset.title = (photo.title || photo.alt_description || '').toLowerCase();
    div.dataset.tagsText = (photo.tags || []).join(',').toLowerCase();
    div.dataset.created = photo.created_at || '';
    div.dataset.year = photo.created_at ? photo.created_at.substring(0, 4) : '';
    div.dataset.color = photo.color || '';
    div.dataset.location = photo.location?.name || '';
    div.dataset.camera =
        photo.exif?.make && photo.exif?.model ? `${photo.exif.make} ${photo.exif.model}` : 'N/A';
    div.dataset.exposure = photo.exif?.exposure_time || 'N/A';
    div.dataset.aperture = photo.exif?.aperture || 'N/A';
    div.dataset.focal = photo.exif?.focal_length || 'N/A';
    div.dataset.iso = photo.exif?.iso || 'N/A';
    div.dataset.likes = photo.likes || 0;
    div.dataset.dimensions = `${photo.width} × ${photo.height}`;
    div.dataset.photographer = photographer;
    div.dataset.photographerUrl = photographerUrl;
    div.dataset.unsplashUrl = unsplashUrl;
    div.dataset.lazyExif = 'false';

    // Create image
    const img = document.createElement('img');
    img.src = photo.url_raw || photo.url;
    img.alt = photo.title || photo.alt_description || 'Photo';
    img.loading = 'lazy';

    // Create title overlay
    const titleDiv = document.createElement('div');
    titleDiv.className = 'photo-title';
    titleDiv.textContent = photo.title || photo.alt_description || 'Untitled';

    // Create attribution overlay
    const attrDiv = document.createElement('div');
    attrDiv.className = 'photo-attribution';
    attrDiv.innerHTML = `
        <span>Photo by </span>
        <a href="${photographerUrl}" target="_blank" rel="noopener noreferrer" style="color: #fff; text-decoration: underline;">${photographer}</a>
        <span> on </span>
        <a href="https://unsplash.com" target="_blank" rel="noopener noreferrer" style="color: #fff; text-decoration: underline;">Unsplash</a>
    `;

    div.appendChild(img);
    div.appendChild(titleDiv);
    div.appendChild(attrDiv);

    return div;
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInfiniteScroll);
} else {
    initInfiniteScroll();
}
