// Navbar scroll effect
console.log('📌 Navbar scroll effect loaded');

let ticking = false;
let hasScrolled = false;

function updateNavbarState() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const scrollY = window.scrollY;
    const threshold = 50; // Add background after 50px scroll

    const shouldHaveBackground = scrollY > threshold;

    // Only update if state actually changed
    if (shouldHaveBackground !== hasScrolled) {
        hasScrolled = shouldHaveBackground;
        if (hasScrolled) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }

    ticking = false;
}

function onScroll() {
    if (!ticking) {
        window.requestAnimationFrame(updateNavbarState);
        ticking = true;
    }
}

// Initialize on page load
window.addEventListener('scroll', onScroll, { passive: true });

// Initial state check (in case page loads scrolled)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateNavbarState);
} else {
    updateNavbarState();
}
