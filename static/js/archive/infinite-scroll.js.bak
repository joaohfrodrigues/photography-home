// Universal infinite scroll - works anywhere with a load-more button
// Version: 2.0 - Unified photo item creator
console.log('🔄 Infinite scroll script loaded v2.0');

let isLoading = false;
let currentPage = 1;

function initInfiniteScroll() {
    const loadMoreBtn = document.getElementById('load-more-btn');
    if (!loadMoreBtn) {
        console.log('No load more button found');
        return;
    }

    currentPage = parseInt(loadMoreBtn.dataset.page) || 2;

    console.log(`Infinite scroll initialized, starting page ${currentPage}`);

    // Click handler for manual load more
    loadMoreBtn.addEventListener('click', () => {
        loadMore();
    });

    // Intersection Observer for automatic loading
    const observer = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting && !isLoading) {
                    console.log('Load more button in view, auto-loading...');
                    loadMore();
                }
            });
        },
        {
            rootMargin: '300px', // Start loading 300px before button is visible
        }
    );

    observer.observe(loadMoreBtn);
}

async function loadMore() {
    if (isLoading) return;

    isLoading = true;
    const loadMoreBtn = document.getElementById('load-more-btn');
    const originalText = loadMoreBtn.textContent;

    loadMoreBtn.textContent = 'Loading...';
    loadMoreBtn.disabled = true;

    try {
        // Build URL from button data attributes
        const collectionId = loadMoreBtn.dataset.collectionId;
        const order = loadMoreBtn.dataset.order;

        let url;
        if (collectionId) {
            url = `/api/collection/${collectionId}/photos?page=${currentPage}`;
        } else if (order !== undefined) {
            url = `/api/latest-photos?order=${order}&page=${currentPage}`;
        } else {
            throw new Error('Cannot determine API endpoint');
        }

        console.log(`Loading page ${currentPage} from ${url}`);

        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        console.log(`Loaded ${data.photos.length} photos, has_more: ${data.has_more}`);

        // Append photos to the appropriate container
        appendPhotos(data.photos);

        // Update page number
        currentPage++;
        loadMoreBtn.dataset.page = currentPage;

        // Hide button if no more photos
        if (!data.has_more) {
            const container = document.getElementById('load-more-container');
            if (container) {
                container.style.display = 'none';
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

// Universal append - detects container type automatically
function appendPhotos(photos) {
    // Try to find gallery grid (collection pages)
    const galleryGrid = document.getElementById('gallery-grid');
    if (galleryGrid) {
        appendToGallery(galleryGrid, photos);
        return;
    }

    // Try to find masonry columns (homepage)
    const col0 = document.getElementById('col-0');
    if (col0) {
        appendToGrid(null, photos); // Pass null, we find columns inside
        return;
    }

    console.error('Could not find photo container');
}

function appendToGallery(container, photos) {
    const currentCount = container.querySelectorAll('.gallery-item').length;

    photos.forEach((photo, idx) => {
        const photoIndex = currentCount + idx;
        const item = createPhotoItem(photo, photoIndex, 'gallery');
        container.appendChild(item);
    });

    reinitLightbox();

    // Trigger animations for new photos
    if (window.reapplyAnimations) {
        window.reapplyAnimations();
    }

    console.log(`Appended ${photos.length} photos to gallery`);
}

function appendToGrid(container, photos) {
    const currentCount = document.querySelectorAll('.photo-card').length;

    // Get all column elements
    const columns = [
        document.getElementById('col-0'),
        document.getElementById('col-1'),
        document.getElementById('col-2'),
    ];

    if (!columns[0]) {
        console.error('Column elements not found');
        return;
    }

    // Track column heights for distribution
    const columnHeights = columns.map(col => {
        let totalHeight = 0;
        const cards = col.querySelectorAll('.photo-card');
        cards.forEach(card => {
            const style = window.getComputedStyle(card);
            const aspectRatio = parseFloat(style.aspectRatio) || 1;
            totalHeight += 1.0 / aspectRatio; // Relative height
        });
        return totalHeight;
    });

    // Distribute new photos to shortest columns
    photos.forEach((photo, idx) => {
        const photoIndex = currentCount + idx;
        const card = createPhotoItem(photo, photoIndex, 'grid');

        // Find shortest column
        const shortestIdx = columnHeights.indexOf(Math.min(...columnHeights));

        // Append to shortest column
        columns[shortestIdx].appendChild(card);

        // Update column height tracker
        const aspectRatio = photo.width / photo.height || 1;
        columnHeights[shortestIdx] += 1.0 / aspectRatio;
    });

    reinitLightbox();
    updateResultsCount();

    // Trigger animations for new photos
    if (window.reapplyAnimations) {
        window.reapplyAnimations();
    }

    console.log(`Appended ${photos.length} photos to grid columns`);
}

function reinitLightbox() {
    if (window.initLightbox) {
        window.initLightbox();
    }
}

function updateResultsCount() {
    const resultsCount = document.getElementById('results-count');
    if (resultsCount) {
        const visiblePhotos = document.querySelectorAll(
            '.photo-card:not([style*="display: none"])'
        ).length;
        resultsCount.textContent = `${visiblePhotos} photo${visiblePhotos !== 1 ? 's' : ''}`;
    }
}

// Unified photo item creator - works for both gallery and grid layouts
function createPhotoItem(photo, index, layout = 'gallery') {
    const div = document.createElement('div');

    // Common data setup
    const photographer = photo.user?.name || photo.photographer || 'Unknown';
    const photographerUrl = photo.user?.profile_url || photo.photographer_url || '';
    const unsplashUrl = photo.links?.html || photo.unsplash_url || '';
    const downloadLocation = photo.links?.download_location || photo.download_location || '';
    const aspectRatio = photo.width / photo.height || 1;

    // Location
    const locationParts = [];
    if (photo.location?.name) {
        locationParts.push(photo.location.name);
    } else {
        if (photo.location?.city) locationParts.push(photo.location.city);
        if (photo.location?.country) locationParts.push(photo.location.country);
    }
    const location = locationParts.join(', ');

    // Tags
    const tags = photo.tags || [];
    const tagsStr = tags.join(', ');
    const tagsHtml = tags
        .slice(0, 10)
        .map(tag => `<span class="lightbox-tag">${tag}</span>`)
        .join('');

    // Common data attributes
    const dataAttrs = {
        'data-index': index,
        'data-photo-id': photo.id || '',
        'data-download-location': downloadLocation,
        'data-description': photo.description || '',
        'data-title': (photo.title || photo.alt_description || '').toLowerCase(),
        'data-tags': tagsHtml,
        'data-tags-text': tagsStr.toLowerCase(),
        'data-created': photo.created_at || '',
        'data-year': photo.created_at ? photo.created_at.substring(0, 4) : '',
        'data-color': photo.color || '',
        'data-location': location,
        'data-orientation':
            aspectRatio > 1.2 ? 'landscape' : aspectRatio < 0.8 ? 'portrait' : 'square',
        'data-camera':
            photo.exif?.make && photo.exif?.model
                ? `${photo.exif.make} ${photo.exif.model}`
                : 'N/A',
        'data-exposure': photo.exif?.exposure_time || 'N/A',
        'data-aperture': photo.exif?.aperture || 'N/A',
        'data-focal': photo.exif?.focal_length || 'N/A',
        'data-iso': photo.exif?.iso || 'N/A',
        'data-views': photo.views || photo.statistics?.views?.total || 0,
        'data-downloads': photo.downloads || photo.statistics?.downloads?.total || 0,
        'data-dimensions': `${photo.width || 0} × ${photo.height || 0}`,
        'data-photographer': photographer,
        'data-photographer-url': photographerUrl,
        'data-unsplash-url': unsplashUrl,
        'data-lazy-exif': 'false',
        'data-lightbox-url': photo.url_raw || photo.url_regular || photo.url || '',
    };

    // Apply data attributes
    Object.keys(dataAttrs).forEach(key => {
        div.setAttribute(key, dataAttrs[key]);
    });

    const title = photo.title || photo.alt_description || 'Untitled';

    if (layout === 'gallery') {
        // Gallery layout for collection pages
        div.className = 'gallery-item';
        div.style.aspectRatio = `${aspectRatio}`;

        const img = document.createElement('img');
        img.src = photo.url_regular || photo.url; // Regular quality for display
        img.alt = title;
        img.loading = 'lazy';

        const titleDiv = document.createElement('div');
        titleDiv.className = 'photo-title';
        titleDiv.textContent = title;

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
    } else {
        // Grid layout for homepage
        div.className = 'photo-card gallery-item';
        const delayIndex = index % 12;
        div.style.cssText = `
            position: relative;
            width: 100%;
            overflow: hidden;
            border-radius: 8px;
            background: #1a1a1a;
            opacity: 0;
            animation: fadeInScale 0.5s ease-out forwards;
            animation-delay: ${Math.min(delayIndex * 0.05, 0.6)}s;
            cursor: pointer;
            aspect-ratio: ${aspectRatio};
        `;

        const img = document.createElement('img');
        img.src = photo.url_regular || photo.url; // Regular quality for display
        img.alt = title;
        img.loading = 'lazy';
        img.style.cssText = `
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        `;

        const photoTitle = document.createElement('div');
        photoTitle.className = 'photo-title';
        photoTitle.textContent = title;
        photoTitle.style.display = 'none';

        const overlay = document.createElement('div');
        overlay.className = 'photo-overlay';
        overlay.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 1.5rem;
            background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        `;

        const titleH3 = document.createElement('h3');
        titleH3.textContent = title;
        titleH3.style.cssText = 'font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 300;';
        overlay.appendChild(titleH3);

        if (location) {
            const locP = document.createElement('p');
            locP.textContent = location;
            locP.style.cssText =
                'font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem;';
            overlay.appendChild(locP);
        }

        if (tagsStr) {
            const tagsP = document.createElement('p');
            tagsP.textContent =
                tagsStr.length > 50 ? `Tags: ${tagsStr.substring(0, 50)}...` : `Tags: ${tagsStr}`;
            tagsP.style.cssText = 'font-size: 0.75rem; color: rgba(255, 255, 255, 0.6);';
            overlay.appendChild(tagsP);
        }

        // Stats overlay (views and downloads)
        const views = photo.views || photo.statistics?.views?.total || 0;
        const downloads = photo.downloads || photo.statistics?.downloads?.total || 0;

        if (views > 0 || downloads > 0) {
            const statsDiv = document.createElement('div');
            statsDiv.className = 'photo-stats';

            if (views > 0) {
                const viewsDiv = document.createElement('div');
                viewsDiv.className = 'stat-item';
                viewsDiv.innerHTML = `
                    <span style="opacity: 0.8;">👁️</span>
                    <span style="margin-left: 4px;">${views.toLocaleString()}</span>
                `;
                statsDiv.appendChild(viewsDiv);
            }

            if (downloads > 0) {
                const downloadsDiv = document.createElement('div');
                downloadsDiv.className = 'stat-item';
                downloadsDiv.innerHTML = `
                    <span style="opacity: 0.8;">⬇️</span>
                    <span style="margin-left: 4px;">${downloads.toLocaleString()}</span>
                `;
                statsDiv.appendChild(downloadsDiv);
            }

            div.appendChild(statsDiv);
        }

        div.appendChild(img);
        div.appendChild(photoTitle);
        div.appendChild(overlay);

        div.addEventListener('mouseover', () => {
            overlay.style.opacity = '1';
            img.style.transform = 'scale(1.05)';
        });
        div.addEventListener('mouseout', () => {
            overlay.style.opacity = '0';
            img.style.transform = 'scale(1)';
        });
    }

    return div;
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initInfiniteScroll);
} else {
    initInfiniteScroll();
}

// Expose for external re-initialization (e.g., after order change)
window.initInfiniteScroll = initInfiniteScroll;
