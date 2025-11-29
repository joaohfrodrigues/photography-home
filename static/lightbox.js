// Lightbox functionality for photography portfolio

let currentPhotoIndex = 0;
let photos = [];
let allGalleryItems = [];  // Keep reference to all items for filtering

function formatDate(dateStr) {
    if (!dateStr) return 'Unknown';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
}

// Filter and search functions
function applyFilters() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const sortBy = document.getElementById('sort-select').value;
    const year = document.getElementById('year-select') ? document.getElementById('year-select').value : 'all';
    const tag = document.getElementById('tag-select') ? document.getElementById('tag-select').value : 'all';
    
    let visibleItems = Array.from(allGalleryItems).filter(item => {
        // Search filter
        const title = item.dataset.title || '';
        const description = item.dataset.description || '';
        const tagsText = item.dataset.tagsText || '';
        const location = item.dataset.location || '';
        const searchMatch = !searchTerm || 
            title.includes(searchTerm) || 
            description.toLowerCase().includes(searchTerm) ||
            tagsText.includes(searchTerm) ||
            location.toLowerCase().includes(searchTerm);
        
        if (!searchMatch) return false;
        
        // Year filter
        if (year !== 'all' && item.dataset.year !== year) {
            return false;
        }
        
        // Tag filter
        if (tag !== 'all') {
            const itemTags = item.dataset.tagsText || '';
            if (!itemTags.includes(tag.toLowerCase())) {
                return false;
            }
        }
        
        return true;
    });
    
    // Sort
    if (sortBy === 'popular') {
        visibleItems.sort((a, b) => {
            const likesA = parseInt(a.dataset.likes || '0');
            const likesB = parseInt(b.dataset.likes || '0');
            return likesB - likesA;
        });
    } else if (sortBy === 'oldest') {
        visibleItems.sort((a, b) => {
            return (a.dataset.created || '').localeCompare(b.dataset.created || '');
        });
    } else {
        // Latest (default)
        visibleItems.sort((a, b) => {
            return (b.dataset.created || '').localeCompare(a.dataset.created || '');
        });
    }
    
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
    document.getElementById('search-input').value = '';
    document.getElementById('sort-select').value = 'latest';
    if (document.getElementById('year-select')) {
        document.getElementById('year-select').value = 'all';
    }
    if (document.getElementById('tag-select')) {
        document.getElementById('tag-select').value = 'all';
    }
    document.getElementById('grid-select').value = '3';
    changeGridSize();
    applyFilters();
}

function changeGridSize() {
    const gridSize = document.getElementById('grid-select').value;
    const grid = document.getElementById('gallery-grid');
    if (grid) {
        grid.style.columnCount = gridSize;
    }
}

function updateLightboxPhotos() {
    // Get currently visible items
    const visibleItems = Array.from(allGalleryItems).filter(item => {
        return !item.classList.contains('hidden');
    });
    
    // Update photos array
    photos = visibleItems.map(item => {
        return {
            url: item.querySelector('img').src,
            title: item.querySelector('.photo-title').textContent,
            description: item.dataset.description || '',
            tags: item.dataset.tags || '',
            created: item.dataset.created || '',
            location: item.dataset.location || '',
            camera: item.dataset.camera || '',
            exposure: item.dataset.exposure || '',
            aperture: item.dataset.aperture || '',
            focal: item.dataset.focal || '',
            iso: item.dataset.iso || '',
            likes: item.dataset.likes || '0',
            dimensions: item.dataset.dimensions || '',
            photographer: item.dataset.photographer || '',
            photographerUrl: item.dataset.photographerUrl || '',
            unsplashUrl: item.dataset.unsplashUrl || '',
            photoId: item.dataset.photoId || '',
            downloadLocation: item.dataset.downloadLocation || '',
            lazyExif: item.dataset.lazyExif === 'true',
        };
    });
}

function initLightbox() {
    allGalleryItems = Array.from(document.querySelectorAll('.gallery-item'));
    
    // Store photo data
    updateLightboxPhotos();
    
    // Add click handlers
    allGalleryItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            // Find the index in the visible photos array
            const visibleItems = allGalleryItems.filter(i => !i.classList.contains('hidden'));
            const visibleIndex = visibleItems.indexOf(item);
            if (visibleIndex !== -1) {
                openLightbox(visibleIndex);
            }
        });
    });
    
    // Initial filter application
    applyFilters();
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        const lightbox = document.getElementById('lightbox');
        if (!lightbox.classList.contains('active')) return;
        
        if (e.key === 'Escape') closeLightbox();
        if (e.key === 'ArrowLeft') navigateLightbox(-1);
        if (e.key === 'ArrowRight') navigateLightbox(1);
    });
}

function triggerDownload(downloadLocation, photoId) {
    // Trigger Unsplash download event (required for API compliance)
    if (!downloadLocation) return;
    
    fetch(`/api/trigger-download?photo_id=${photoId}&download_location=${encodeURIComponent(downloadLocation)}`)
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
    currentPhotoIndex = index;
    const lightbox = document.getElementById('lightbox');
    updateLightboxContent();
    lightbox.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // Trigger download event when photo is viewed (Unsplash requirement)
    const photo = photos[currentPhotoIndex];
    if (photo.downloadLocation && photo.photoId) {
        triggerDownload(photo.downloadLocation, photo.photoId);
    }
    
    // Fetch detailed EXIF data on-demand only if lazy loading is enabled
    if (photo.lazyExif && photo.photoId) {
        fetchPhotoDetails(photo.photoId);
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
    
    cameraValue.textContent = 'Loading...';
    
    fetch(`/api/photo-details/${photoId}`)
        .then(response => response.json())
        .then(exif => {
            if (exif && !exif.error) {
                // Update camera info with fetched EXIF data
                const cameraMake = exif.make || 'Unknown';
                const cameraModel = exif.model || 'Unknown';
                const cameraFull = cameraMake !== 'Unknown' ? `${cameraMake} ${cameraModel}` : 'Unknown';
                
                cameraValue.textContent = cameraFull;
                exposureValue.textContent = exif.exposure_time || 'N/A';
                apertureValue.textContent = exif.aperture ? `f/${exif.aperture}` : 'N/A';
                focalValue.textContent = exif.focal_length && exif.focal_length !== 'N/A' ? `${exif.focal_length}mm` : 'N/A';
                isoValue.textContent = exif.iso || 'N/A';
                
                console.log('EXIF data loaded:', exif);
                
                // Update visibility after loading EXIF
                cameraItem.style.display = (cameraFull === 'N/A' || cameraFull === 'Unknown') ? 'none' : 'flex';
                exposureItem.style.display = (exif.exposure_time === 'N/A' || !exif.exposure_time) ? 'none' : 'flex';
                apertureItem.style.display = (!exif.aperture || exif.aperture === 'N/A') ? 'none' : 'flex';
                focalItem.style.display = (!exif.focal_length || exif.focal_length === 'N/A') ? 'none' : 'flex';
                isoItem.style.display = (!exif.iso || exif.iso === 'N/A') ? 'none' : 'flex';
                
                // Hide entire camera section if all items are N/A
                const allNA = [cameraItem, exposureItem, apertureItem, focalItem, isoItem]
                    .every(item => item.style.display === 'none');
                cameraSection.style.display = allNA ? 'none' : 'block';
            } else {
                cameraValue.textContent = 'Not available';
                cameraItem.style.display = 'none';
                cameraSection.style.display = 'none';
            }
        })
        .catch(err => {
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
    
    // Fetch EXIF for new photo if lazy loading enabled
    if (photo.lazyExif && photo.photoId) {
        fetchPhotoDetails(photo.photoId);
    }
}

function updateLightboxContent() {
    const photo = photos[currentPhotoIndex];
    
    // Update metadata
    document.getElementById('lightbox-img').src = photo.url;
    document.getElementById('lightbox-title').textContent = photo.title;
    document.getElementById('lightbox-description').textContent = photo.description || '';
    document.getElementById('lightbox-index').textContent = `${currentPhotoIndex + 1} / ${photos.length}`;
    
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
    cameraItem.style.display = (cameraValue === 'N/A' || cameraValue === 'Unknown' || cameraValue === 'Loading...') ? 'none' : 'flex';
    
    document.getElementById('meta-exposure').textContent = exposureValue;
    exposureItem.style.display = exposureValue === 'N/A' ? 'none' : 'flex';
    
    document.getElementById('meta-aperture').textContent = apertureValue;
    apertureItem.style.display = apertureValue === 'N/A' || apertureValue === 'f/N/A' ? 'none' : 'flex';
    
    document.getElementById('meta-focal').textContent = focalValue;
    focalItem.style.display = focalValue === 'N/A' ? 'none' : 'flex';
    
    document.getElementById('meta-iso').textContent = isoValue;
    isoItem.style.display = isoValue === 'N/A' ? 'none' : 'flex';
    
    // Hide entire camera section if all items are N/A
    const allNA = [cameraItem, exposureItem, apertureItem, focalItem, isoItem]
        .every(item => item.style.display === 'none');
    cameraSection.style.display = allNA ? 'none' : 'block';
    
    // Set tags
    const tagsContainer = document.getElementById('meta-tags');
    if (photo.tags) {
        tagsContainer.innerHTML = photo.tags;
        tagsContainer.style.display = 'flex';
    } else {
        tagsContainer.style.display = 'none';
    }
    
    // Update attribution links
    const photographerLink = document.getElementById('photographer-link');
    const unsplashLink = document.getElementById('unsplash-link');
    photographerLink.textContent = photo.photographer || 'Unknown';
    photographerLink.href = photo.photographerUrl || '#';
    unsplashLink.href = photo.unsplashUrl || '#';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initLightbox);
