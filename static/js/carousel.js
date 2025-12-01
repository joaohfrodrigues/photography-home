/**
 * Collection Carousel - Auto-rotating image carousel with manual controls
 */

// Carousel with arrows and auto-rotate on hover
document.addEventListener('DOMContentLoaded', function () {
    const carousels = document.querySelectorAll('.collection-carousel');

    carousels.forEach(carousel => {
        const images = carousel.querySelectorAll('.carousel-image');
        const dots = carousel.querySelectorAll('.carousel-dot');
        const prevBtn = carousel.querySelector('.carousel-prev');
        const nextBtn = carousel.querySelector('.carousel-next');
        const card = carousel.closest('.collection-card');
        let currentIndex = 0;
        let intervalId;
        let isTransitioning = false;

        function showImage(index) {
            if (isTransitioning) return;
            isTransitioning = true;

            // Fade out current image
            const currentImg = images[currentIndex];
            if (currentImg) {
                currentImg.style.opacity = '0';
            }

            // Wait for fade out, then switch and fade in
            setTimeout(() => {
                images.forEach((img, i) => {
                    if (i === index) {
                        img.style.display = 'block';
                        // Force reflow for animation
                        void img.offsetWidth;
                        img.style.opacity = '1';
                    } else {
                        img.style.display = 'none';
                        img.style.opacity = '0';
                    }
                });

                dots.forEach((dot, i) => {
                    dot.style.background =
                        i === index ? 'rgba(255, 255, 255, 0.8)' : 'rgba(255, 255, 255, 0.3)';
                });

                // Allow next transition after animation completes
                setTimeout(() => {
                    isTransitioning = false;
                }, 250);
            }, 250); // Half of the transition duration
        }

        function nextImage() {
            if (isTransitioning) return;
            currentIndex = (currentIndex + 1) % images.length;
            showImage(currentIndex);
        }

        function prevImage() {
            if (isTransitioning) return;
            currentIndex = (currentIndex - 1 + images.length) % images.length;
            showImage(currentIndex);
        }

        function startCarousel() {
            if (!intervalId) {
                intervalId = setInterval(nextImage, 4000);
            }
        }

        function stopCarousel() {
            if (intervalId) {
                clearInterval(intervalId);
                intervalId = null;
            }
        }

        // Arrow click handlers
        prevBtn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
            prevImage();
            stopCarousel();
        });

        nextBtn.addEventListener('click', e => {
            e.preventDefault();
            e.stopPropagation();
            nextImage();
            stopCarousel();
        });

        // Dot click handlers
        dots.forEach((dot, index) => {
            dot.addEventListener('click', e => {
                e.preventDefault();
                e.stopPropagation();
                if (currentIndex !== index && !isTransitioning) {
                    currentIndex = index;
                    showImage(currentIndex);
                }
                stopCarousel();
            });
        });

        // Show arrows on card hover
        card.addEventListener('mouseenter', () => {
            prevBtn.style.opacity = '1';
            nextBtn.style.opacity = '1';
            startCarousel();
        });

        card.addEventListener('mouseleave', () => {
            prevBtn.style.opacity = '0';
            nextBtn.style.opacity = '0';
            stopCarousel();
        });

        // Arrow hover effects
        [prevBtn, nextBtn].forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.background = 'rgba(0, 0, 0, 0.7)';
            });
            btn.addEventListener('mouseleave', () => {
                btn.style.background = 'rgba(0, 0, 0, 0.5)';
            });
        });

        // Attach generic swipe handler (pointer + touch) from `static/js/swipe.js`.
        // This keeps swipe logic reusable (carousel, lightbox, etc.).
        if (typeof attachSwipe === 'function') {
            // Ignore pointer/touch gestures that start on carousel controls
            attachSwipe(carousel, {
                threshold: 50,
                verticalThreshold: 100,
                ignoreSelector: '.carousel-prev, .carousel-next, .carousel-dot, .carousel-dot *',
                onSwipeLeft: () => {
                    nextImage();
                    stopCarousel();
                },
                onSwipeRight: () => {
                    prevImage();
                    stopCarousel();
                },
            });
        }
    });
});
