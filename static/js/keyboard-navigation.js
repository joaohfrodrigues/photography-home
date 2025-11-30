/**
 * Keyboard navigation for carousel and lightbox
 */

// Keyboard navigation for collection carousel
function initCarouselKeyboardNav() {
    const carousels = document.querySelectorAll('.collection-carousel');

    carousels.forEach(carousel => {
        const card = carousel.closest('.collection-card');

        // Make card focusable
        if (!card.hasAttribute('tabindex')) {
            card.setAttribute('tabindex', '0');
        }

        card.addEventListener('keydown', e => {
            // Only handle if the card itself is focused (not a child element)
            if (e.target !== card) return;

            const currentIndex = parseInt(
                carousel.querySelector('.carousel-dot[style*="rgba(255, 255, 255, 0.8)"]')?.dataset
                    .index || '0'
            );
            const totalSlides = carousel.querySelectorAll('.carousel-image').length;
            let newIndex = currentIndex;

            switch (e.key) {
                case 'ArrowLeft':
                case 'h': // Vim-style
                    e.preventDefault();
                    newIndex = currentIndex === 0 ? totalSlides - 1 : currentIndex - 1;
                    navigateCarousel(carousel, newIndex);
                    break;

                case 'ArrowRight':
                case 'l': // Vim-style
                    e.preventDefault();
                    newIndex = (currentIndex + 1) % totalSlides;
                    navigateCarousel(carousel, newIndex);
                    break;

                case 'Enter':
                case ' ':
                    e.preventDefault();
                    // Follow the link
                    card.click();
                    break;
            }
        });
    });
}

function navigateCarousel(carousel, newIndex) {
    const images = carousel.querySelectorAll('.carousel-image');
    const dots = carousel.querySelectorAll('.carousel-dot');

    // Hide all images
    images.forEach(img => {
        img.style.display = 'none';
        img.style.opacity = '0';
    });

    // Show current image
    if (images[newIndex]) {
        images[newIndex].style.display = 'block';
        setTimeout(() => {
            images[newIndex].style.opacity = '1';
        }, 10);
    }

    // Update dots
    dots.forEach((dot, i) => {
        dot.style.background =
            i === newIndex ? 'rgba(255, 255, 255, 0.8)' : 'rgba(255, 255, 255, 0.3)';
    });
}

// Enhanced lightbox keyboard navigation
function initLightboxKeyboardNav() {
    document.addEventListener('keydown', e => {
        const lightbox = document.getElementById('lightbox');
        if (!lightbox || lightbox.style.display !== 'flex') return;

        const currentIndex = parseInt(
            lightbox.querySelector('.lightbox-image')?.dataset.index || '0'
        );
        const allPhotos = Array.from(document.querySelectorAll('.gallery-item'));
        const totalPhotos = allPhotos.length;

        switch (e.key) {
            case 'Escape':
                e.preventDefault();
                closeLightbox();
                break;

            case 'ArrowLeft':
            case 'h': // Vim-style
            case 'a': // Gaming-style
                e.preventDefault();
                if (currentIndex > 0) {
                    openLightbox(currentIndex - 1);
                }
                break;

            case 'ArrowRight':
            case 'l': // Vim-style
            case 'd': // Gaming-style
                e.preventDefault();
                if (currentIndex < totalPhotos - 1) {
                    openLightbox(currentIndex + 1);
                }
                break;

            case 'ArrowUp':
            case 'k': // Vim-style
            case 'w': // Gaming-style
                e.preventDefault();
                // Jump back 5 photos
                if (currentIndex >= 5) {
                    openLightbox(currentIndex - 5);
                } else {
                    openLightbox(0);
                }
                break;

            case 'ArrowDown':
            case 'j': // Vim-style
            case 's': // Gaming-style
                e.preventDefault();
                // Jump forward 5 photos
                if (currentIndex + 5 < totalPhotos) {
                    openLightbox(currentIndex + 5);
                } else {
                    openLightbox(totalPhotos - 1);
                }
                break;

            case 'Home':
                e.preventDefault();
                openLightbox(0);
                break;

            case 'End':
                e.preventDefault();
                openLightbox(totalPhotos - 1);
                break;

            case 'f':
            case 'F11':
                e.preventDefault();
                toggleFullscreen();
                break;

            case 'i':
                e.preventDefault();
                toggleLightboxInfo();
                break;

            case '?':
                e.preventDefault();
                showKeyboardHelp();
                break;
        }
    });
}

function toggleFullscreen() {
    const lightbox = document.getElementById('lightbox');
    if (!lightbox) return;

    if (!document.fullscreenElement) {
        lightbox.requestFullscreen().catch(err => {
            console.log('Fullscreen failed:', err);
        });
    } else {
        document.exitFullscreen();
    }
}

function toggleLightboxInfo() {
    const info = document.querySelector('.lightbox-info');
    if (info) {
        info.style.display = info.style.display === 'none' ? 'block' : 'none';
    }
}

function showKeyboardHelp() {
    const helpOverlay = document.getElementById('keyboard-help-overlay');
    if (helpOverlay) {
        helpOverlay.style.display = 'flex';
        return;
    }

    // Create help overlay
    const help = document.createElement('div');
    help.id = 'keyboard-help-overlay';
    help.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.9);
        backdrop-filter: blur(10px);
        z-index: 10001;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    `;

    help.innerHTML = `
        <div style="
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2rem;
            max-width: 600px;
            color: white;
        ">
            <h2 style="margin-bottom: 1.5rem; font-weight: 300;">Keyboard Shortcuts</h2>
            <div style="display: grid; grid-template-columns: auto 1fr; gap: 1rem; font-size: 0.95rem;">
                <kbd style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">←/→ or H/L</kbd>
                <span>Previous/Next photo</span>

                <kbd style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">↑/↓ or K/J</kbd>
                <span>Jump 5 photos back/forward</span>

                <kbd style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">Home/End</kbd>
                <span>First/Last photo</span>

                <kbd style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">Esc</kbd>
                <span>Close lightbox</span>

                <kbd style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">F or F11</kbd>
                <span>Toggle fullscreen</span>

                <kbd style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">I</kbd>
                <span>Toggle info panel</span>

                <kbd style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px;">?</kbd>
                <span>Show this help</span>
            </div>
            <button onclick="document.getElementById('keyboard-help-overlay').style.display='none'"
                    style="
                        margin-top: 1.5rem;
                        padding: 0.75rem 1.5rem;
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.2);
                        border-radius: 6px;
                        color: white;
                        cursor: pointer;
                        font-size: 1rem;
                        width: 100%;
                    ">
                Got it!
            </button>
        </div>
    `;

    document.body.appendChild(help);

    // Close on click outside
    help.addEventListener('click', e => {
        if (e.target === help) {
            help.style.display = 'none';
        }
    });

    // Close on Escape
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape' && help.style.display === 'flex') {
            help.style.display = 'none';
        }
    });
}

// Initialize keyboard navigation
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initCarouselKeyboardNav();
        initLightboxKeyboardNav();
    });
} else {
    initCarouselKeyboardNav();
    initLightboxKeyboardNav();
}

// Re-initialize carousel navigation for dynamically loaded content
function reinitCarouselKeyboardNav() {
    initCarouselKeyboardNav();
}

window.reinitCarouselKeyboardNav = reinitCarouselKeyboardNav;
