/**
 * Theme Toggle - Light/Dark Mode Support
 *
 * Handles localStorage SecurityError gracefully (private browsing, etc.)
 */

// Check if localStorage is available
function isLocalStorageAvailable() {
    try {
        const test = '__storage_test__';
        localStorage.setItem(test, test);
        localStorage.removeItem(test);
        return true;
    } catch (e) {
        return false;
    }
}

// Safe localStorage getter
function getTheme() {
    if (!isLocalStorageAvailable()) return null;
    try {
        return localStorage.getItem('theme');
    } catch (e) {
        console.warn('Cannot read localStorage:', e);
        return null;
    }
}

// Safe localStorage setter
function saveTheme(theme) {
    if (!isLocalStorageAvailable()) {
        console.warn('localStorage not available, theme will not persist');
        return false;
    }
    try {
        localStorage.setItem('theme', theme);
        return true;
    } catch (e) {
        console.warn('Cannot save to localStorage:', e);
        return false;
    }
}

// Toggle between light and dark themes
function toggleTheme() {
    // Get current theme, fallback to 'dark' if not set
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    console.log('Toggle: ' + currentTheme + ' → ' + newTheme);

    // Update DOM
    document.documentElement.setAttribute('data-theme', newTheme);

    // Try to save to localStorage
    if (saveTheme(newTheme)) {
        console.log('Theme saved:', newTheme);
    } else {
        console.log('Theme applied but not saved (localStorage unavailable)');
    }

    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: newTheme } }));
}

// Listen for OS theme changes (only if user hasn't set a preference)
if (window.matchMedia) {
    try {
        const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');

        darkModeQuery.addEventListener('change', e => {
            // Only auto-switch if user hasn't explicitly set a preference
            if (!getTheme()) {
                const newTheme = e.matches ? 'dark' : 'light';
                document.documentElement.setAttribute('data-theme', newTheme);
                console.log('OS theme changed to:', newTheme);
            }
        });
    } catch (e) {
        console.warn('Cannot listen to OS theme changes:', e);
    }
}

// Debug: log initial state
console.log('Theme initialized:', document.documentElement.getAttribute('data-theme'));
