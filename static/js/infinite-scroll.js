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

    let isLoading = false;

    function findLoadMoreAnchor() {
        const container = document.getElementById('load-more-container');
        if (!container) return null;
        return container.querySelector('a') || container.querySelector('button') || null;
    }

    function getCurrentPageFromLink(link) {
        try {
            const url = new URL(link.href, window.location.origin);
            return parseInt(url.searchParams.get('page') || '1', 10);
        } catch (e) {
            return 1;
        }
    }

    async function loadMore() {
        if (isLoading) return;
        const link = findLoadMoreAnchor();
        if (!link) return;

        isLoading = true;
        const prevText = link.textContent;
        link.textContent = 'Loading...';

        try {
            const url = link.href;
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const html = await res.text();

            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            // Prefer gallery grid (collection) else photo-grid (homepage)
            const newGallery = doc.getElementById('gallery-grid');
            const gallery = document.getElementById('gallery-grid');

            if (gallery && newGallery) {
                // Append gallery items directly
                Array.from(newGallery.children).forEach(child => {
                    gallery.appendChild(child);
                });
            } else {
                // Photo grid / columns
                const newPhotoGrid =
                    doc.querySelector('.photo-grid') || doc.querySelector('.gallery-grid');
                const photoGrid = document.querySelector('.photo-grid');

                if (photoGrid && newPhotoGrid) {
                    // If server uses columns (col-0..col-2), extract items and append round-robin
                    const columns = [
                        document.getElementById('col-0'),
                        document.getElementById('col-1'),
                        document.getElementById('col-2'),
                    ].filter(Boolean);
                    if (columns.length === 3) {
                        // Get items from newPhotoGrid
                        const items = Array.from(
                            newPhotoGrid.querySelectorAll('.photo-card, .gallery-item')
                        );
                        let idx = 0;
                        items.forEach(item => {
                            // Adopt node into current document
                            const node = document.importNode(item, true);
                            columns[idx % 3].appendChild(node);
                            idx++;
                        });
                    } else {
                        // Fallback: append children directly
                        Array.from(newPhotoGrid.children).forEach(child => {
                            photoGrid.appendChild(child);
                        });
                    }
                }
            }

            // Replace or remove the load more container with whatever the server returned
            const newLoadMore = doc.getElementById('load-more-container');
            const oldLoadMore = document.getElementById('load-more-container');
            if (oldLoadMore) {
                if (newLoadMore) {
                    oldLoadMore.outerHTML = newLoadMore.outerHTML;
                } else {
                    oldLoadMore.remove();
                }
            }

            // Reinitialize lightbox and animations
            if (window.initLightbox) window.initLightbox();
            if (window.reapplyAnimations) window.reapplyAnimations();

            // Re-bind observer for new container
            // We allow initInfiniteScroll to be idempotent
            window.__infiniteScrollInitialized = false;
            if (window.initInfiniteScroll) window.initInfiniteScroll();
        } catch (err) {
            console.error('Infinite scroll load failed', err);
            if (link) link.textContent = 'Error - Try Again';
        } finally {
            isLoading = false;
            if (link) link.textContent = prevText;
        }
    }

    function initInfiniteScroll() {
        const loadMoreAnchor = findLoadMoreAnchor();
        if (!loadMoreAnchor) return;

        if (window.__infiniteScrollInitialized) return;
        window.__infiniteScrollInitialized = true;

        // If the anchor is an <a>, we observe its container for intersection
        const container = document.getElementById('load-more-container');
        if (!container) return;

        // Add click fallback
        const anchor = container.querySelector('a, button');
        if (anchor && anchor.tagName.toLowerCase() === 'a') {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                loadMore();
            });
        }

        const observer = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (entry.isIntersecting && !isLoading) {
                        loadMore();
                    }
                });
            },
            { rootMargin: '300px' }
        );

        observer.observe(container);

        window.initInfiniteScroll = initInfiniteScroll;
        window.__infiniteScrollObserver = observer;
    }

    // Auto-init on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initInfiniteScroll);
    } else {
        initInfiniteScroll();
    }
})();
