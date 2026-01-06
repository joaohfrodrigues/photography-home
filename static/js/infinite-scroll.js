/**
 * Infinite scroll loader
 * - Observes the `#load-more-container` element and fetches the next page
 * - Appends new photos to `.photo-grid` or `.gallery-grid`
 * - Reinitializes lightbox and other UI hooks after appending
 */

/*
 * Adapted archived infinite scroll (SSR-friendly)
 * - Uses the archived script logic and DOM helpers but fetches server-rendered HTML
 * - Appends DOM nodes from the next page instead of calling a JSON API
 */

(function () {
    'use strict';

    const state = {
        inited: false,
        isLoading: false,
        observer: null,
        abortController: null,
    };

    /**
     * Determine the number of columns based on viewport width
     * Matches the responsive breakpoints in responsive.css
     */
    function getColumnCount() {
        const width = window.innerWidth;
        if (width < 768) return 1; // Mobile: 1 column
        if (width < 1200) return 2; // Tablet: 2 columns
        return 3; // Desktop: 3 columns
    }

    /**
     * Reorganize columns based on data-order to preserve backend sort
     * across different viewport column counts.
     */
    function reorganizeColumns() {
        const numColumns = getColumnCount();
        const col0 = document.getElementById('col-0');
        const col1 = document.getElementById('col-1');
        const col2 = document.getElementById('col-2');

        if (!col0) return;

        // Collect all items, sort by data-order (numeric)
        const items = Array.from(document.querySelectorAll('.photo-card, .gallery-item')).sort(
            (a, b) => (parseInt(a.dataset.order, 10) || 0) - (parseInt(b.dataset.order, 10) || 0)
        );

        if (!items.length) return;

        // Clear all columns
        col0.innerHTML = '';
        if (col1) col1.innerHTML = '';
        if (col2) col2.innerHTML = '';

        // Determine active columns
        const columns = [col0, col1, col2].filter(Boolean).slice(0, numColumns);

        // Hide extras
        for (let i = numColumns; i < 3; i++) {
            const col = document.getElementById(`col-${i}`);
            if (col) col.style.display = 'none';
        }
        for (let i = 0; i < numColumns; i++) {
            const col = document.getElementById(`col-${i}`);
            if (col) col.style.display = 'flex';
        }

        // Redistribute round-robin in sorted order
        items.forEach((item, idx) => {
            columns[idx % numColumns].appendChild(item);
        });
    }

    // Expose for other scripts (e.g., search handler) to reflow columns after DOM swaps
    window.reorganizeColumns = reorganizeColumns;

    function findLoadMoreAnchor() {
        const container = document.getElementById('load-more-container');
        if (!container) return null;
        return container.querySelector('a') || container.querySelector('button') || null;
    }

    function bindAnchorClick(anchor) {
        if (!anchor) return;
        if (anchor.dataset.infiniteBound === 'true') return;
        if (anchor.tagName.toLowerCase() !== 'a') return;

        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            if (state.isLoading) return;
            loadMore();
        });

        anchor.dataset.infiniteBound = 'true';
    }

    function setLoading(loading, link, prevText) {
        const spinner = document.getElementById('loading-indicator');
        if (spinner) spinner.style.display = loading ? 'flex' : 'none';
        if (link) link.textContent = loading ? 'Loading...' : prevText;
    }

    async function fetchNextPage(url) {
        if (state.abortController) {
            state.abortController.abort();
        }
        state.abortController = new AbortController();
        const res = await fetch(url, { signal: state.abortController.signal });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const html = await res.text();
        const parser = new DOMParser();
        return parser.parseFromString(html, 'text/html');
    }

    function appendContent(doc) {
        let appended = 0;
        const newGallery = doc.getElementById('gallery-grid');
        const gallery = document.getElementById('gallery-grid');

        if (gallery && newGallery) {
            Array.from(newGallery.children).forEach(child => {
                gallery.appendChild(child);
            });
            appended += newGallery.children.length;
            return appended;
        }

        const newPhotoGrid = doc.querySelector('.photo-grid') || doc.querySelector('.gallery-grid');
        const photoGrid = document.querySelector('.photo-grid');

        if (!photoGrid || !newPhotoGrid) return;

        const columns = [
            document.getElementById('col-0'),
            document.getElementById('col-1'),
            document.getElementById('col-2'),
        ].filter(Boolean);

        const existing = Array.from(document.querySelectorAll('.photo-card, .gallery-item'));
        const maxOrder = existing.reduce((max, el) => {
            const val = parseInt(el.dataset.order, 10);
            return Number.isFinite(val) ? Math.max(max, val) : max;
        }, -1);
        const baseOrder = maxOrder + 1;

        if (columns.length === 3) {
            const items = Array.from(newPhotoGrid.querySelectorAll('.photo-card, .gallery-item'));
            const numColumns = getColumnCount();
            let idx = 0;
            items.forEach(item => {
                const node = document.importNode(item, true);
                node.dataset.order = String(baseOrder + idx);
                node.style.animationDelay = '0s';
                columns[idx % numColumns].appendChild(node);
                idx++;
                appended++;
            });
        } else {
            Array.from(newPhotoGrid.children).forEach((child, i) => {
                const node = document.importNode(child, true);
                node.dataset.order = String(baseOrder + i);
                node.style.animationDelay = '0s';
                photoGrid.appendChild(node);
                appended++;
            });
        }

        if (window.updateLightboxPhotos) {
            window.updateLightboxPhotos();
        }

        return appended;
    }

    function updateSentinel(doc) {
        const currentContainer = document.getElementById('load-more-container');
        if (!currentContainer) return false;

        const newContainer = doc.getElementById('load-more-container');
        const noMore =
            !newContainer ||
            newContainer.dataset.hasMore === 'false' ||
            newContainer.style.display === 'none';

        if (noMore) {
            if (state.observer) state.observer.disconnect();
            state.observer = null;
            window.__infiniteScrollObserver = null;
            currentContainer.remove();
            state.inited = false;
            window.__infiniteScrollInitialized = false;
            return false;
        }

        const newAnchor = newContainer.querySelector('a, button');
        let currentAnchor = currentContainer.querySelector('a, button');

        if (newAnchor) {
            if (!currentAnchor) {
                currentContainer.innerHTML = '';
                currentContainer.appendChild(document.importNode(newAnchor, true));
                currentAnchor = currentContainer.querySelector('a, button');
            } else {
                if (newAnchor.href) currentAnchor.href = newAnchor.href;
                if (newAnchor.textContent) currentAnchor.textContent = newAnchor.textContent;
            }

            currentContainer.style.display = newContainer.style.display || '';
            bindAnchorClick(currentAnchor);
        }

        return true;
    }

    function refreshUi() {
        if (window.initLightbox) window.initLightbox();
        if (window.reapplyAnimations) window.reapplyAnimations();
        bindAnchorClick(findLoadMoreAnchor());
    }

    async function loadMore() {
        if (state.isLoading) return;
        const link = findLoadMoreAnchor();
        if (!link) return;

        state.isLoading = true;
        const prevText = link.textContent;
        setLoading(true, link, prevText);

        const targetUrl = link.href;
        const startTime = performance.now();
        if (window.logDevEvent) {
            window.logDevEvent('InfiniteScroll', `GET ${targetUrl}`);
        }

        try {
            const doc = await fetchNextPage(targetUrl);
            const appended = appendContent(doc) || 0;
            const hasMore = updateSentinel(doc);
            refreshUi();
            const duration = Math.round(performance.now() - startTime);
            if (window.logDevEvent) {
                window.logDevEvent('Network', `GET ${targetUrl} (${duration}ms)`);
                window.logDevEvent(
                    'InfiniteScroll',
                    `Appended ${appended} items | total ${document.querySelectorAll('.photo-card, .gallery-item').length}`
                );
            }
            if (!hasMore) cleanupInfiniteScroll();
        } catch (err) {
            console.error('Infinite scroll load failed', err);
            if (link) link.textContent = 'Error - Try Again';
            if (window.logDevEvent) {
                window.logDevEvent('Error', `Infinite scroll failed: ${err.message}`);
            }
        } finally {
            state.isLoading = false;
            setLoading(false, link, prevText);
            state.abortController = null;
            if (window.logDevEvent && !findLoadMoreAnchor()) {
                window.logDevEvent('InfiniteScroll', 'No further pages available.');
            }
        }
    }

    // Expose manual trigger for re-init scenarios
    window.triggerLoadMore = loadMore;

    function initInfiniteScroll() {
        if (state.inited) return;
        const loadMoreAnchor = findLoadMoreAnchor();
        if (!loadMoreAnchor) return;

        const container = document.getElementById('load-more-container');
        if (!container) return;

        state.inited = true;
        window.__infiniteScrollInitialized = true;
        bindAnchorClick(loadMoreAnchor);

        state.observer = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !state.isLoading) {
                        loadMore();
                    }
                });
            },
            { rootMargin: '300px' }
        );

        state.observer.observe(container);

        window.initInfiniteScroll = initInfiniteScroll;
        window.__infiniteScrollObserver = state.observer;
    }

    function cleanupInfiniteScroll() {
        if (state.observer) {
            state.observer.disconnect();
            state.observer = null;
            window.__infiniteScrollObserver = null;
        }
        if (state.abortController) {
            state.abortController.abort();
            state.abortController = null;
        }
        state.isLoading = false;
        state.inited = false;
        window.__infiniteScrollInitialized = false;
    }

    function forceReinitInfiniteScroll() {
        cleanupInfiniteScroll();
        state.isLoading = false;
        state.inited = false;
        if (window.initInfiniteScroll) {
            initInfiniteScroll();
        }
    }

    // Auto-init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            reorganizeColumns();
            initInfiniteScroll();
        });
    } else {
        reorganizeColumns();
        initInfiniteScroll();
    }

    window.addEventListener('pagehide', cleanupInfiniteScroll);
    window.addEventListener('beforeunload', cleanupInfiniteScroll);

    // Reorganize on resize (debounced) to keep order with column count changes
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            reorganizeColumns();
            if (window.updateLightboxPhotos) {
                window.updateLightboxPhotos();
            }
        }, 150);
    });

    // Expose helpers
    window.reorganizeColumns = reorganizeColumns;
    window.triggerLoadMore = loadMore;
    window.resetInfiniteScroll = cleanupInfiniteScroll;
    window.forceReinitInfiniteScroll = forceReinitInfiniteScroll;
})();
