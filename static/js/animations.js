/**
 * Scroll-triggered animations and effects
 */

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px',
};

const fadeInObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in-visible');
            // Optionally unobserve after animation
            // fadeInObserver.unobserve(entry.target);
        }
    });
}, observerOptions);

// Initialize fade-in animations on page load
function initScrollAnimations() {
    // Animate collection cards
    document.querySelectorAll('.collection-card').forEach(card => {
        card.classList.add('fade-in-element');
        fadeInObserver.observe(card);
    });

    // Animate photo items
    document.querySelectorAll('.photo-item').forEach((item, index) => {
        item.classList.add('fade-in-element');
        // Stagger delay
        item.style.transitionDelay = `${(index % 12) * 0.05}s`;
        fadeInObserver.observe(item);
    });

    // Animate section headers
    document.querySelectorAll('h2').forEach(header => {
        header.classList.add('fade-in-element');
        fadeInObserver.observe(header);
    });
}

// Back to top button functionality
function initBackToTop() {
    // Create button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'back-to-top';
    backToTopBtn.innerHTML =
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width: 24px; height: 24px; display: block;"><polyline points="18 15 12 9 6 15"></polyline></svg>';
    backToTopBtn.setAttribute('aria-label', 'Back to top');
    backToTopBtn.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        cursor: pointer;
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.3s ease;
        z-index: 1000;
        pointer-events: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        display: grid;
        place-items: center;
        padding: 0;
    `;
    document.body.appendChild(backToTopBtn);

    // Show/hide on scroll
    let scrollTimeout;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimeout);
        const scrolled = window.scrollY;

        if (scrolled > 500) {
            backToTopBtn.style.opacity = '1';
            backToTopBtn.style.transform = 'translateY(0)';
            backToTopBtn.style.pointerEvents = 'auto';
        } else {
            backToTopBtn.style.opacity = '0';
            backToTopBtn.style.transform = 'translateY(20px)';
            backToTopBtn.style.pointerEvents = 'none';
        }
    });

    // Click handler
    backToTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth',
        });
    });

    // Hover effects
    backToTopBtn.addEventListener('mouseenter', () => {
        backToTopBtn.style.background = 'rgba(255, 255, 255, 0.2)';
        backToTopBtn.style.transform = 'translateY(-5px)';
    });

    backToTopBtn.addEventListener('mouseleave', () => {
        backToTopBtn.style.background = 'rgba(255, 255, 255, 0.1)';
        backToTopBtn.style.transform = 'translateY(0)';
    });
}

// Enhanced hover effects for collection cards (if not using inline styles)
function initCollectionHoverEffects() {
    document.querySelectorAll('.collection-card').forEach(card => {
        const carousel = card.querySelector('.collection-carousel');

        card.addEventListener('mouseenter', () => {
            if (carousel) {
                carousel.style.transform = 'scale(1.02)';
            }
        });

        card.addEventListener('mouseleave', () => {
            if (carousel) {
                carousel.style.transform = 'scale(1)';
            }
        });
    });
}

// Initialize all animations when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initScrollAnimations();
        initBackToTop();
        initCollectionHoverEffects();
    });
} else {
    initScrollAnimations();
    initBackToTop();
    initCollectionHoverEffects();
}

// Re-apply animations to dynamically loaded content (infinite scroll)
function reapplyAnimations() {
    document.querySelectorAll('.photo-item:not(.fade-in-element)').forEach((item, index) => {
        item.classList.add('fade-in-element');
        item.style.transitionDelay = `${(index % 12) * 0.05}s`;
        fadeInObserver.observe(item);
    });
}

// Expose for use by infinite scroll
window.reapplyAnimations = reapplyAnimations;
