// Sticky header that compacts on scroll
console.log('📌 Sticky header script loaded');

let lastScrollY = 0;
let ticking = false;
let isCompact = false;

function updateHeaderState() {
    const hero = document.querySelector('.hero, #hero');
    if (!hero) return;

    const scrollY = window.scrollY;

    // Threshold: compact when scrolled more than 200px
    const threshold = 200;
    const shouldBeCompact = scrollY > threshold;

    // Only update if state actually changed
    if (shouldBeCompact !== isCompact) {
        isCompact = shouldBeCompact;
        if (isCompact) {
            hero.classList.add('compact');
        } else {
            hero.classList.remove('compact');
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

// Initial state check (in case page loads scrolled)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateHeaderState);
} else {
    updateHeaderState();
}
