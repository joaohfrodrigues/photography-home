/**
 * Developer Mode overlay and event bus
 * - Toggle persists to localStorage
 * - Logs network/search/masonry events in a floating console
 * - Highlights lazy-loaded images when they hydrate
 * - Draws masonry column guides to visualize layout calculations
 */
(function () {
    'use strict';

    const DEV_KEY = 'devMode';
    const DEV_CLASS = 'dev-mode-active';
    const GUIDES_ID = 'dev-masonry-overlay';
    let lazyObserver = null;
    let gridObserver = null;
    let resizeTimeout = null;
    let lastMasonryLog = 0;

    function persistDevMode(enabled) {
        try {
            localStorage.setItem(DEV_KEY, enabled ? 'true' : 'false');
        } catch (e) {
            // localStorage might be blocked; ignore
        }
    }

    function ensureConsole() {
        let container = document.getElementById('dev-console');
        if (!container) {
            container = document.createElement('div');
            container.id = 'dev-console';
            container.className = 'dev-console';
            document.body.appendChild(container);
        }
        return container;
    }

    window.logDevEvent = function (source, message) {
        if (!window.devMode) return;
        const container = ensureConsole();
        const entry = document.createElement('div');
        entry.className = 'dev-console-entry';
        entry.innerHTML = `<strong>[${source}]</strong> ${message}`;
        container.appendChild(entry);
        requestAnimationFrame(() => {
            entry.classList.add('visible');
        });
        setTimeout(() => {
            entry.classList.remove('visible');
            setTimeout(() => entry.remove(), 400);
        }, 5000);
    };

    function removeGuides() {
        const overlay = document.getElementById(GUIDES_ID);
        if (overlay) overlay.remove();
    }

    function renderMasonryGuides() {
        if (!window.devMode) {
            removeGuides();
            return;
        }

        const grid =
            document.querySelector('.photo-grid') || document.querySelector('.gallery-grid');
        if (!grid) {
            removeGuides();
            return;
        }

        const rectGrid = grid.getBoundingClientRect();
        let overlay = document.getElementById(GUIDES_ID);
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = GUIDES_ID;
            overlay.className = 'dev-overlay';
            document.body.appendChild(overlay);
        }

        overlay.className = 'dev-overlay';
        overlay.style.top = `${rectGrid.top + window.scrollY}px`;
        overlay.style.left = `${rectGrid.left + window.scrollX}px`;
        overlay.style.width = `${rectGrid.width}px`;
        overlay.style.height = `${rectGrid.height}px`;
        overlay.innerHTML = '';

        const columns = Array.from(grid.querySelectorAll('.masonry-column'));
        columns.forEach((col, idx) => {
            const rectCol = col.getBoundingClientRect();
            const guide = document.createElement('div');
            guide.className = 'dev-grid-guide';
            guide.style.left = `${rectCol.left - rectGrid.left}px`;
            guide.style.top = `${rectCol.top - rectGrid.top}px`;
            guide.style.width = `${rectCol.width}px`;
            guide.style.height = `${rectCol.height}px`;
            guide.dataset.label = `Col ${idx + 1}: ${col.children.length} items`;
            overlay.appendChild(guide);
        });

        const now = Date.now();
        if (window.devMode && now - lastMasonryLog > 400) {
            const heights = columns.map(col => Math.round(col.getBoundingClientRect().height));
            const totalItems = columns.reduce((sum, col) => sum + col.children.length, 0);
            logDevEvent(
                'Masonry',
                `Reflowed ${columns.length} cols | items ${totalItems} | heights ${heights.join(' / ')}px`
            );
            lastMasonryLog = now;
        }
    }

    function ensureLazyObserver() {
        if (lazyObserver) return;
        lazyObserver = new IntersectionObserver(
            entries => {
                entries.forEach(entry => {
                    if (!entry.isIntersecting) return;
                    const img = entry.target;
                    lazyObserver.unobserve(img);
                    const card = img.closest('.photo-card, .gallery-item, .photo-item');
                    if (card) card.classList.add('dev-lazy-hydrated');
                    const alt = img.getAttribute('alt') || img.dataset.photoId || 'image';
                    logDevEvent('LazyLoad', `Hydrated ${alt}`);
                });
            },
            { rootMargin: '150px', threshold: 0.1 }
        );
    }

    function bindLazyImages() {
        if (!window.devMode) return;
        ensureLazyObserver();
        const selector = 'img[loading="lazy"]:not([data-dev-lazy-bound])';
        document.querySelectorAll(selector).forEach(img => {
            img.dataset.devLazyBound = 'true';
            lazyObserver.observe(img);
        });
    }

    function bindGridObserver() {
        if (gridObserver) gridObserver.disconnect();
        const grid =
            document.querySelector('.photo-grid') || document.querySelector('.gallery-grid');
        if (!grid) return;
        if (!gridObserver) {
            gridObserver = new MutationObserver(() => {
                if (!window.devMode) return;
                bindLazyImages();
                renderMasonryGuides();
            });
        }
        gridObserver.observe(grid, { childList: true, subtree: true });
    }

    function hookReorganize() {
        const fn = window.reorganizeColumns;
        if (!fn || fn.__devWrapped) return;
        const wrapped = function () {
            const result = fn.apply(this, arguments);
            if (window.devMode) {
                requestAnimationFrame(renderMasonryGuides);
            }
            return result;
        };
        wrapped.__devWrapped = true;
        window.reorganizeColumns = wrapped;
    }

    function teardownDevOverlays() {
        if (lazyObserver) lazyObserver.disconnect();
        if (gridObserver) gridObserver.disconnect();
        document
            .querySelectorAll('.dev-lazy-hydrated')
            .forEach(el => el.classList.remove('dev-lazy-hydrated'));
        removeGuides();
    }

    function applyDevMode(enabled) {
        window.devMode = enabled;
        persistDevMode(enabled);
        document.documentElement.classList.toggle(DEV_CLASS, enabled);

        if (enabled) {
            bindLazyImages();
            bindGridObserver();
            hookReorganize();
            renderMasonryGuides();
            logDevEvent('System', 'Developer Mode Activated. Tracking events...');
        } else {
            teardownDevOverlays();
        }
    }

    window.toggleDevMode = function () {
        applyDevMode(!window.devMode);
    };

    // Initialize state from the early bootstrap (which read localStorage)
    // The class on html reflects the saved state from head.py
    window.devMode = document.documentElement.classList.contains(DEV_CLASS);

    // Set up overlays if dev mode is already active (after page load)
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            if (window.devMode) {
                bindLazyImages();
                bindGridObserver();
                hookReorganize();
                renderMasonryGuides();
            }
        });
    } else {
        if (window.devMode) {
            bindLazyImages();
            bindGridObserver();
            hookReorganize();
            renderMasonryGuides();
        }
    }

    // Keep overlays aligned on resize
    window.addEventListener('resize', () => {
        if (!window.devMode) return;
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            renderMasonryGuides();
        }, 150);
    });

    // Try to hook reflow logic after other scripts load
    const hookInterval = setInterval(() => {
        hookReorganize();
        if (window.reorganizeColumns && window.reorganizeColumns.__devWrapped) {
            clearInterval(hookInterval);
        }
    }, 400);

    window.addEventListener('load', () => {
        if (window.devMode) {
            bindLazyImages();
            bindGridObserver();
            renderMasonryGuides();
        }
    });
})();
