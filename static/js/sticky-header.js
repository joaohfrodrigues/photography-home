// Sticky header that compacts on scroll
console.log('📌 Sticky header script loaded');

let lastScrollY = 0;
let ticking = false;
let isCompact = false;
let heroHeight = 0;

function updateHeaderState() {
    const hero = document.querySelector('.hero, #hero');
    if (!hero) return;

    const scrollY = window.scrollY;

    // Get hero's natural height if not already stored
    if (!heroHeight) {
        heroHeight = hero.offsetHeight;
    }

    // Threshold: compact when scrolled past the hero section
    const threshold = heroHeight - 100; // Start transition 100px before hero scrolls out
    const shouldBeCompact = scrollY > threshold;

    // Only update if state actually changed
    if (shouldBeCompact !== isCompact) {
        isCompact = shouldBeCompact;
        if (isCompact) {
            hero.classList.add('compact');
            // Add padding to body to prevent content jump
            document.body.style.paddingTop = hero.offsetHeight + 'px';
        } else {
            hero.classList.remove('compact');
            document.body.style.paddingTop = '0';
        }
    }

    lastScrollY = scrollY;
    ticking = false;
}

function onScroll() {
    if (!ticking) {
        window.requestAnimationFrame(updateHeaderState);
        ticking = true;
    }
}

// Initialize on page load
window.addEventListener('scroll', onScroll, { passive: true });

// Recalculate on resize
window.addEventListener('resize', () => {
    heroHeight = 0; // Reset to recalculate
    updateHeaderState();
});

// Initial state check (in case page loads scrolled)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateHeaderState);
} else {
    updateHeaderState();
}
