/*
 * swipe.js
 * Lightweight swipe/drag utility with pointer/touch fallback.
 * Usage (global):
 *   const detach = attachSwipe(element, { onSwipeLeft, onSwipeRight, threshold, verticalThreshold });
 *   // later: detach();
 */

(function (global) {
    'use strict';

    function noop() {}

    function createHandler(el, opts) {
        const threshold = opts.threshold ?? 50;
        const verticalThreshold = opts.verticalThreshold ?? 100;
        const onLeft = opts.onSwipeLeft ?? noop;
        const onRight = opts.onSwipeRight ?? noop;
        const ignoreSelector = opts.ignoreSelector || null;

        let startX = 0;
        let startY = 0;
        let lastX = 0;
        let lastY = 0;
        let pointerId = null;
        let tracking = false;

        function reset() {
            startX = startY = lastX = lastY = 0;
            pointerId = null;
            tracking = false;
        }

        // Pointer events (mouse, pen, touch) - modern and recommended
        function onPointerDown(e) {
            // Ignore interactions that start on interactive controls (buttons/links/dots)
            let ignored = false;
            try {
                if (
                    ignoreSelector &&
                    e.target &&
                    e.target.closest &&
                    e.target.closest(ignoreSelector)
                ) {
                    ignored = true;
                }
            } catch (err) {
                // ignore selector evaluation errors and continue
            }

            // Only track primary button/touch
            if (e.pointerType === 'mouse' && e.button !== 0) return;
            pointerId = e.pointerId;
            tracking = true;
            startX = lastX = e.clientX;
            startY = lastY = e.clientY;
            // el.setPointerCapture?.(pointerId);
        }

        function onPointerMove(e) {
            if (!tracking || e.pointerId !== pointerId) return;
            lastX = e.clientX;
            lastY = e.clientY;
        }

        function onPointerUp(e) {
            if (!tracking || e.pointerId !== pointerId) return;
            const dx = lastX - startX;
            const dy = lastY - startY;

            // Check if it was a swipe (movement > threshold)
            if (Math.abs(dx) > threshold && Math.abs(dy) < verticalThreshold) {
                if (dx > 0) onRight(e);
                else onLeft(e);

                // --- NEW CODE: PREVENT CLICK ---
                // Add a temporary attribute to the element to signal a swipe occurred
                el.setAttribute('data-swiped', 'true');
                setTimeout(() => el.removeAttribute('data-swiped'), 100); // Clear it quickly
                // -------------------------------
            }

            // el.releasePointerCapture?.(pointerId); // (You already commented this out)
            reset();
        }

        // Fallback for older touch-only environments
        function onTouchStart(e) {
            if (!e.touches || e.touches.length !== 1) return;
            // Ignore if touch starts on an interactive control
            let ignored = false;
            try {
                if (
                    ignoreSelector &&
                    e.target &&
                    e.target.closest &&
                    e.target.closest(ignoreSelector)
                ) {
                    ignored = true;
                }
            } catch (err) {
                // ignore and continue
            }

            tracking = true;
            startX = lastX = e.touches[0].clientX;
            startY = lastY = e.touches[0].clientY;
        }

        function onTouchMove(e) {
            if (!tracking || !e.touches || e.touches.length !== 1) return;
            lastX = e.touches[0].clientX;
            lastY = e.touches[0].clientY;
        }

        function onTouchEnd(e) {
            if (!tracking) return;
            const dx = lastX - startX;
            const dy = lastY - startY;
            if (Math.abs(dx) > threshold && Math.abs(dy) < verticalThreshold) {
                if (dx > 0) onRight(e);
                else onLeft(e);
            }
            reset();
        }

        function attach() {
            if (window.PointerEvent) {
                el.addEventListener('pointerdown', onPointerDown, { passive: true });
                el.addEventListener('pointermove', onPointerMove, { passive: true });
                el.addEventListener('pointerup', onPointerUp, { passive: true });
                el.addEventListener('pointercancel', reset, { passive: true });
            } else {
                el.addEventListener('touchstart', onTouchStart, { passive: true });
                el.addEventListener('touchmove', onTouchMove, { passive: true });
                el.addEventListener('touchend', onTouchEnd, { passive: true });
                el.addEventListener('touchcancel', reset, { passive: true });
            }
        }

        function detach() {
            dbg('detach handler');
            if (window.PointerEvent) {
                el.removeEventListener('pointerdown', onPointerDown);
                el.removeEventListener('pointermove', onPointerMove);
                el.removeEventListener('pointerup', onPointerUp);
                el.removeEventListener('pointercancel', reset);
            } else {
                el.removeEventListener('touchstart', onTouchStart);
                el.removeEventListener('touchmove', onTouchMove);
                el.removeEventListener('touchend', onTouchEnd);
                el.removeEventListener('touchcancel', reset);
            }
            reset();
        }

        return { attach, detach };
    }

    function attachSwipe(element, opts) {
        if (!element) return () => {};
        // Automatically disable browser horizontal scrolling on this element
        element.style.touchAction = 'pan-y';
        const h = createHandler(element, opts || {});
        h.attach();
        return function detach() {
            // Optional: reset it back if you want
            element.style.touchAction = '';
            h.detach();
        };
    }

    // Expose globally for use in non-module environments
    global.attachSwipe = attachSwipe;
})(window);
