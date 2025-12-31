// Lightbox functionality for photography portfolio
console.log('🎬 Lightbox.js file loaded successfully!');

let currentPhotoIndex = 0;
let photos = [];
let allGalleryItems = []; // Keep reference to all items for filtering

// Loading state helpers
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Debounce helper for search input
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function formatDate(dateStr) {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    });
}

// Filter and search functions
function applyFilters() {
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput ? searchInput.value.toLowerCase() : '';

    let visibleItems = Array.from(allGalleryItems).filter(item => {
        // Search filter only
        const title = item.dataset.title || '';
        const description = item.dataset.description || '';
        const tagsText = item.dataset.tagsText || '';
        const location = item.dataset.location || '';
        const searchMatch =
            !searchTerm ||
            title.includes(searchTerm) ||
            description.toLowerCase().includes(searchTerm) ||
            tagsText.includes(searchTerm) ||
            location.toLowerCase().includes(searchTerm);

        return searchMatch;
    });

    // Hide all items
    allGalleryItems.forEach(item => {
        item.classList.add('hidden');
    });

    // Show filtered items
    visibleItems.forEach(item => {
        item.classList.remove('hidden');
    });

    // Update count
    const count = visibleItems.length;
    const total = allGalleryItems.length;
    const countEl = document.getElementById('results-count');
    if (countEl) {
        if (count === total) {
            countEl.textContent = `Showing all ${total} photos`;
        } else {
            countEl.textContent = `Showing ${count} of ${total} photos`;
        }
    }

    // Reinitialize lightbox with filtered items
    updateLightboxPhotos();
}

function resetFilters() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
    applyFilters();
}

function updateLightboxPhotos() {
    // Get currently visible items
    const visibleItems = Array.from(allGalleryItems).filter(item => {
        return !item.classList.contains('hidden');
    });

    console.log('Updating lightbox photos, visible items:', visibleItems.length);

    // Update photos array
    photos = visibleItems.map(item => {
        const img = item.querySelector('img');
        const titleDiv = item.querySelector('.photo-title');

        if (!img) {
            console.error('No img found in gallery item:', item);
        }
        if (!titleDiv) {
            console.error('No photo-title found in gallery item:', item);
        }

        return {
            url: item.dataset.lightboxUrl || (img ? img.src : ''),
            title: titleDiv ? titleDiv.textContent : '',
            description: item.dataset.description || '',
            tags: item.dataset.tags || '',
            created: item.dataset.created || '',
            location: item.dataset.location || '',
            camera: item.dataset.camera || '',
            exposure: item.dataset.exposure || '',
            aperture: item.dataset.aperture || '',
            focal: item.dataset.focal || '',
            iso: item.dataset.iso || '',
            views: item.dataset.views || '0',
            downloads: item.dataset.downloads || '0',
            dimensions: item.dataset.dimensions || '',
            photographer: item.dataset.photographer || '',
            photographerUrl: item.dataset.photographerUrl || '',
            unsplashUrl: item.dataset.unsplashUrl || '',
            photoId: item.dataset.photoId || '',
            downloadLocation: item.dataset.downloadLocation || '',
            lazyExif: item.dataset.lazyExif === 'true',
        };
    });

    console.log('Photos array updated:', photos.length, 'photos');
}

function initLightbox() {
    allGalleryItems = Array.from(document.querySelectorAll('.gallery-item'));
    console.log('Lightbox init: Found', allGalleryItems.length, 'gallery items');

    // Store photo data
    updateLightboxPhotos();

    // Add click handlers
    allGalleryItems.forEach((item, index) => {
        // Avoid binding the same handler multiple times when reinitializing
        if (item.dataset.lightboxBound === 'true') return;

        const handler = e => {
            // Don't open lightbox if clicking on attribution links
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                console.log('Click on link, not opening lightbox');
                return;
            }

            console.log('Gallery item clicked:', index);
            // Find the index in the visible photos array
            const visibleItems = allGalleryItems.filter(i => !i.classList.contains('hidden'));
            const visibleIndex = visibleItems.indexOf(item);
            console.log('Visible index:', visibleIndex, 'of', visibleItems.length, 'visible items');
            if (visibleIndex !== -1) {
                openLightbox(visibleIndex);
            }
        };

        item.addEventListener('click', handler);
        // Mark as bound so subsequent init calls won't rebind
        item.dataset.lightboxBound = 'true';
    });

    // Initial filter application
    applyFilters();

    // Keyboard navigation (bind only once)
    if (!window.__lightboxKeyBound) {
        document.addEventListener('keydown', e => {
            const lightbox = document.getElementById('lightbox');
            if (!lightbox || !lightbox.classList.contains('active')) return;

            if (e.key === 'Escape') closeLightbox();
            if (e.key === 'ArrowLeft') navigateLightbox(-1);
            if (e.key === 'ArrowRight') navigateLightbox(1);
        });
        window.__lightboxKeyBound = true;
    }
}

function triggerDownload(downloadLocation, photoId) {
    // Trigger Unsplash download event (required for API compliance)
    if (!downloadLocation) return;

    fetch(
        `/api/trigger-download?photo_id=${photoId}&download_location=${encodeURIComponent(downloadLocation)}`
    )
        .then(response => {
            if (response.ok) {
                console.log('Download event triggered for photo:', photoId);
            } else {
                console.warn('Failed to trigger download event');
            }
        })
        .catch(err => console.error('Error triggering download:', err));
}

function openLightbox(index) {
    console.log('Opening lightbox at index:', index);
    currentPhotoIndex = index;
    const lightbox = document.getElementById('lightbox');
    if (!lightbox) {
        console.error('Lightbox element not found!');
        return;
    }
    updateLightboxContent();
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
    console.log('Lightbox opened, active class added');

    // Trigger download event when photo is viewed (Unsplash requirement)
    const photo = photos[currentPhotoIndex];
    if (photo.downloadLocation && photo.photoId) {
        triggerDownload(photo.downloadLocation, photo.photoId);
    }
}

function fetchPhotoDetails(photoId) {
    // Get references to value elements and their parent items
    const cameraValue = document.getElementById('meta-camera');
    const exposureValue = document.getElementById('meta-exposure');
    const apertureValue = document.getElementById('meta-aperture');
    const focalValue = document.getElementById('meta-focal');
    const isoValue = document.getElementById('meta-iso');

    const cameraItem = document.getElementById('camera-item');
    const exposureItem = document.getElementById('exposure-item');
    const apertureItem = document.getElementById('aperture-item');
    const focalItem = document.getElementById('focal-item');
    const isoItem = document.getElementById('iso-item');
    const cameraSection = document.getElementById('camera-section');

    // Show loading state
    cameraValue.textContent = 'Loading...';
    showLoading();

    fetch(`/api/photo-details/${photoId}`)
        .then(response => response.json())
        .then(photoData => {
            hideLoading();

            if (photoData && !photoData.error) {
                // Use pre-formatted EXIF data from API
                const cameraMake = photoData.camera || 'Unknown';
                const exposureVal = photoData.exposure || 'N/A';
                const apertureVal = photoData.aperture || 'N/A';
                const focalVal = photoData.focal || 'N/A';
                const isoVal = photoData.iso || 'N/A';

                cameraValue.textContent = cameraMake;
                exposureValue.textContent = exposureVal;
                apertureValue.textContent = apertureVal;
                focalValue.textContent = focalVal;
                isoValue.textContent = isoVal;

                console.log('EXIF data loaded from API:', {
                    camera: cameraMake,
                    exposure: exposureVal,
                    aperture: apertureVal,
                    focal: focalVal,
                    iso: isoVal,
                });

                // Update visibility after loading EXIF
                cameraItem.style.display =
                    cameraMake === 'N/A' || cameraMake === 'Unknown' ? 'none' : 'flex';
                exposureItem.style.display =
                    exposureVal === 'N/A' || !exposureVal ? 'none' : 'flex';
                apertureItem.style.display =
                    apertureVal === 'N/A' || !apertureVal ? 'none' : 'flex';
                focalItem.style.display = focalVal === 'N/A' || !focalVal ? 'none' : 'flex';
                isoItem.style.display = isoVal === 'N/A' || !isoVal ? 'none' : 'flex';

                // Hide entire camera section if all items are N/A
                const allNA = [cameraItem, exposureItem, apertureItem, focalItem, isoItem].every(
                    item => item.style.display === 'none'
                );
                cameraSection.style.display = allNA ? 'none' : 'block';
            } else {
                cameraValue.textContent = 'Not available';
                cameraItem.style.display = 'none';
                cameraSection.style.display = 'none';
            }
        })
        .catch(err => {
            hideLoading();
            console.error('Error fetching photo details:', err);
            cameraValue.textContent = 'Error loading';
            cameraItem.style.display = 'none';
            cameraSection.style.display = 'none';
        });
}
function closeLightbox() {
    const lightbox = document.getElementById('lightbox');
    lightbox.classList.remove('active');
    document.body.style.overflow = '';
}

function navigateLightbox(direction) {
    currentPhotoIndex += direction;
    if (currentPhotoIndex < 0) currentPhotoIndex = photos.length - 1;
    if (currentPhotoIndex >= photos.length) currentPhotoIndex = 0;
    updateLightboxContent();

    // Trigger download for new photo
    const photo = photos[currentPhotoIndex];
    if (photo.downloadLocation && photo.photoId) {
        triggerDownload(photo.downloadLocation, photo.photoId);
    }
}

function updateLightboxContent() {
    const photo = photos[currentPhotoIndex];
    const imgElement = document.getElementById('lightbox-img');

    // Fade out the current image first
    imgElement.style.opacity = '0';

    // Preload the new image
    const newImg = new Image();
    newImg.src = photo.url;

    newImg.onload = () => {
        // Once loaded, update the src and fade in
        imgElement.src = photo.url;
        imgElement.dataset.index = currentPhotoIndex;
        setTimeout(() => {
            imgElement.style.opacity = '1';
        }, 50);
    };

    // Update metadata only after starting image transition
    document.getElementById('lightbox-title').textContent = photo.title;
    document.getElementById('lightbox-description').textContent = photo.description || '';
    document.getElementById('lightbox-index').textContent =
        `${currentPhotoIndex + 1} / ${photos.length}`;

    // Format and set date
    const dateStr = formatDate(photo.created);
    document.getElementById('meta-created').textContent = dateStr;

    // Set dimensions
    document.getElementById('meta-dimensions').textContent = photo.dimensions;

    // Set location (hide if empty)
    const locationElement = document.getElementById('meta-location').closest('.lightbox-meta-item');
    if (photo.location && photo.location.trim()) {
        document.getElementById('meta-location').textContent = photo.location;
        locationElement.style.display = 'flex';
    } else {
        locationElement.style.display = 'none';
    }

    // Set camera info with N/A hiding
    const cameraValue = photo.camera;
    const exposureValue = photo.exposure;
    const apertureValue = photo.aperture;
    const focalValue = photo.focal;
    const isoValue = photo.iso;

    // Hide/show camera items based on N/A values
    const cameraItem = document.getElementById('camera-item');
    const exposureItem = document.getElementById('exposure-item');
    const apertureItem = document.getElementById('aperture-item');
    const focalItem = document.getElementById('focal-item');
    const isoItem = document.getElementById('iso-item');
    const cameraSection = document.getElementById('camera-section');

    // Update values and hide if N/A
    document.getElementById('meta-camera').textContent = cameraValue;
    cameraItem.style.display =
        cameraValue === 'N/A' || cameraValue === 'Unknown' || cameraValue === 'Loading...'
            ? 'none'
            : 'flex';

    document.getElementById('meta-exposure').textContent = exposureValue;
    exposureItem.style.display = exposureValue === 'N/A' ? 'none' : 'flex';

    document.getElementById('meta-aperture').textContent = apertureValue;
    apertureItem.style.display =
        apertureValue === 'N/A' || apertureValue === 'f/N/A' ? 'none' : 'flex';

    document.getElementById('meta-focal').textContent = focalValue;
    focalItem.style.display = focalValue === 'N/A' ? 'none' : 'flex';

    document.getElementById('meta-iso').textContent = isoValue;
    isoItem.style.display = isoValue === 'N/A' ? 'none' : 'flex';

    // Hide entire camera section if all items are N/A
    const allNA = [cameraItem, exposureItem, apertureItem, focalItem, isoItem].every(
        item => item.style.display === 'none'
    );
    cameraSection.style.display = allNA ? 'none' : 'block';

    // Set tags
    const tagsContainer = document.getElementById('meta-tags');
    if (photo.tags) {
        tagsContainer.innerHTML = photo.tags;
        tagsContainer.style.display = 'flex';
    } else {
        tagsContainer.style.display = 'none';
    }

    // Set stats (views, downloads)
    const viewsElement = document.getElementById('meta-views');
    const downloadsElement = document.getElementById('meta-downloads');
    const statsSection = document.getElementById('stats-section');

    const views = parseInt(photo.views || 0);
    const downloads = parseInt(photo.downloads || 0);

    // Update values with formatting
    let hasStats = false;
    if (viewsElement && views > 0) {
        viewsElement.textContent = views.toLocaleString();
        document.getElementById('stats-views').style.display = 'flex';
        hasStats = true;
    } else if (viewsElement) {
        document.getElementById('stats-views').style.display = 'none';
    }

    if (downloadsElement && downloads > 0) {
        downloadsElement.textContent = downloads.toLocaleString();
        document.getElementById('stats-downloads').style.display = 'flex';
        hasStats = true;
    } else if (downloadsElement) {
        document.getElementById('stats-downloads').style.display = 'none';
    }

    // Hide entire stats section if no stats available
    if (statsSection) {
        statsSection.style.display = hasStats ? 'block' : 'none';
    }

    // Update attribution links
    const photographerLink = document.getElementById('photographer-link');
    const unsplashLink = document.getElementById('unsplash-link');
    photographerLink.textContent = photo.photographer || 'Unknown';
    photographerLink.href = photo.photographerUrl || '#';
    unsplashLink.href = photo.unsplashUrl || '#';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded, initializing lightbox...');
    initLightbox();
});

// Fallback initialization in case DOMContentLoaded already fired
if (document.readyState === 'loading') {
    // Document still loading, DOMContentLoaded will fire
    console.log('Document still loading');
} else {
    // DOMContentLoaded already fired
    console.log('Document already loaded, initializing immediately');
    initLightbox();
}

// Create debounced version of applyFilters for search input
const debouncedFilter = debounce(applyFilters, 300);

// Expose functions to global scope for inline event handlers
window.closeLightbox = closeLightbox;
window.navigateLightbox = navigateLightbox;
window.applyFilters = applyFilters;
window.debouncedFilter = debouncedFilter;

// Performance monitoring
if (window.performance && window.performance.getEntriesByType) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = window.performance.getEntriesByType('navigation')[0];
            if (perfData) {
                console.log('Page load metrics:', {
                    loadTime: Math.round(perfData.loadEventEnd - perfData.fetchStart),
                    domReady: Math.round(perfData.domContentLoadedEventEnd - perfData.fetchStart),
                    ttfb: Math.round(perfData.responseStart - perfData.requestStart),
                });
            }
        }, 0);
    });
}
