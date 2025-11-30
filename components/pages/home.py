"""Home page component - Hybrid layout with featured collections and latest photos"""

from fasthtml.common import *

from components.ui.footer import create_footer
from components.ui.head import create_head
from components.ui.header import create_hero, create_navbar
from components.ui.lightbox import create_lightbox
from components.ui.photo_grid import create_photo_grid
from services import fetch_collection_photos, fetch_latest_user_photos, fetch_user_collections


def create_collection_card(collection, index):
    """Create a compact collection card with carousel"""
    collection_id = collection['id']
    photos, _ = fetch_collection_photos(collection_id, page=1, per_page=6)

    # Create carousel items with smaller images for faster loading
    carousel_items = []
    for i, photo in enumerate(photos[:6]):
        # Use smaller thumbnail for carousel (400px width is sufficient for card display)
        img_url = photo['url_thumb'] if 'url_thumb' in photo else photo['url']

        carousel_items.append(
            Img(
                src=img_url,
                alt=photo['title'],
                loading='lazy' if i > 0 else 'eager',  # First image loads immediately
                cls='carousel-image',
                style=f'display: {"block" if i == 0 else "none"}; width: 100%; height: 100%; object-fit: contain; opacity: {1 if i == 0 else 0}; transition: opacity 0.5s ease-in-out;',
                **{'data-index': str(i)},
            )
        )

    carousel_id = f'carousel-{collection_id}'

    return A(
        # Carousel container
        Div(
            # Images
            Div(
                *carousel_items,
                cls='carousel-images',
                style="""
                    position: relative;
                    aspect-ratio: 4/3;
                    overflow: hidden;
                    border-radius: 8px 8px 0 0;
                    background: #1a1a1a;
                """,
            ),
            # Previous arrow
            Button(
                Span('‹', style='display: block; transform: translateX(-1px);'),
                cls='carousel-arrow carousel-prev',
                style="""
                    position: absolute;
                    left: 12px;
                    top: 50%;
                    transform: translateY(-50%);
                    background: rgba(0, 0, 0, 0.5);
                    color: white;
                    border: none;
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    font-size: 24px;
                    cursor: pointer;
                    z-index: 3;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    opacity: 0;
                    transition: opacity 0.3s ease, background 0.2s ease;
                    padding: 0;
                    line-height: 1;
                    user-select: none;
                    -webkit-tap-highlight-color: transparent;
                """,
                onclick='event.preventDefault(); event.stopPropagation();',
            ),
            # Next arrow
            Button(
                Span('›', style='display: block; transform: translateX(1px);'),
                cls='carousel-arrow carousel-next',
                style="""
                    position: absolute;
                    right: 12px;
                    top: 50%;
                    transform: translateY(-50%);
                    background: rgba(0, 0, 0, 0.5);
                    color: white;
                    border: none;
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    font-size: 24px;
                    cursor: pointer;
                    z-index: 3;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    opacity: 0;
                    transition: opacity 0.3s ease, background 0.2s ease;
                    padding: 0;
                    line-height: 1;
                    user-select: none;
                    -webkit-tap-highlight-color: transparent;
                """,
                onclick='event.preventDefault(); event.stopPropagation();',
            ),
            # Carousel indicators (dots)
            Div(
                *[
                    Span(
                        cls='carousel-dot',
                        style=f"""
                            width: 8px;
                            height: 8px;
                            border-radius: 50%;
                            background: {"rgba(255, 255, 255, 0.8)" if i == 0 else "rgba(255, 255, 255, 0.3)"};
                            display: inline-block;
                            margin: 0 4px;
                            transition: background 0.3s ease;
                            cursor: pointer;
                        """,
                        **{'data-index': str(i)},
                    )
                    for i in range(len(photos[:6]))
                ],
                cls='carousel-dots',
                style="""
                    position: absolute;
                    bottom: 12px;
                    left: 50%;
                    transform: translateX(-50%);
                    z-index: 2;
                    display: flex;
                    gap: 4px;
                """,
            ),
            id=carousel_id,
            cls='collection-carousel',
            style='position: relative;',
        ),
        # Collection info
        Div(
            H3(
                collection['title'],
                style='font-size: 1.3rem; margin-bottom: 0.5rem; color: #fff; font-weight: 300;',
            ),
            P(f"{collection['total_photos']} photos", style='color: #888; font-size: 0.85rem;'),
            style='padding: 1.25rem;',
        ),
        href=f'/collection/{collection_id}',
        cls='collection-card',
        style=f"""
            display: block;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            overflow: hidden;
            text-decoration: none;
            transition: all 0.3s ease;
            opacity: 0;
            animation: fadeInScale 0.6s ease-out forwards;
            animation-delay: {index * 0.1}s;
            height: fit-content;
        """,
        onmouseover="this.style.transform='translateY(-8px)'; this.style.background='rgba(255, 255, 255, 0.05)'",
        onmouseout="this.style.transform='translateY(0)'; this.style.background='rgba(255, 255, 255, 0.03)'",
    )


def home_page(collections=None, latest_photos=None, order='popular'):
    """Render the home page with featured collections and latest photos grid"""
    if collections is None:
        collections = fetch_user_collections()

    # Filter for featured collections only (first 3-4)
    featured_collections = [c for c in collections if c.get('featured', False)]

    # Fetch latest photos if not provided
    if latest_photos is None:
        latest_photos, _ = fetch_latest_user_photos(page=1, per_page=24, order_by=order)

    return Html(
        create_head(),
        Body(
            create_navbar(current_page='home'),
            create_hero(),
            # Main content
            Main(
                # Featured Collections Section (30%)
                Section(
                    Div(
                        Div(
                            H2(
                                'Featured Collections',
                                style='font-size: 2rem; margin-bottom: 0.5rem; font-weight: 200; letter-spacing: 0.05em;',
                            ),
                            P(
                                'Curated photo series from my portfolio',
                                style='color: rgba(255, 255, 255, 0.6); font-size: 1rem; margin-bottom: 3rem;',
                            ),
                            style='text-align: center;',
                        ),
                        # Featured collections grid
                        Div(
                            *[
                                create_collection_card(c, i)
                                for i, c in enumerate(featured_collections)
                            ],
                            cls='featured-collections-grid',
                            style="""
                                display: grid;
                                grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                                gap: 2rem;
                                margin-bottom: 2rem;
                            """,
                        ),
                        # Link to all collections
                        Div(
                            A(
                                'View All Collections →',
                                href='/collections',
                                style="""
                                    display: inline-block;
                                    padding: 0.875rem 2rem;
                                    background: rgba(255, 255, 255, 0.05);
                                    border: 1px solid rgba(255, 255, 255, 0.1);
                                    border-radius: 8px;
                                    color: #fff;
                                    text-decoration: none;
                                    font-size: 0.95rem;
                                    transition: all 0.3s ease;
                                """,
                                onmouseover="this.style.background='rgba(255, 255, 255, 0.1)'; this.style.borderColor='rgba(255, 255, 255, 0.2)'",
                                onmouseout="this.style.background='rgba(255, 255, 255, 0.05)'; this.style.borderColor='rgba(255, 255, 255, 0.1)'",
                            ),
                            style='text-align: center; margin-top: 2rem;',
                        ),
                        cls='container',
                        style='max-width: 1600px; margin: 0 auto; padding: 4rem 2rem 3rem;',
                    ),
                    style='background: rgba(255, 255, 255, 0.01);',
                ),
                # Latest Photos Section (70%)
                Section(
                    Div(
                        Div(
                            H2(
                                'Latest Photos',
                                style='font-size: 2rem; margin-bottom: 0.5rem; font-weight: 200; letter-spacing: 0.05em;',
                            ),
                            P(
                                'Browse and search through my most recent photography',
                                style='color: rgba(255, 255, 255, 0.6); font-size: 1rem; margin-bottom: 3rem;',
                            ),
                            style='text-align: center;',
                        ),
                        # Photo grid with search
                        create_photo_grid(latest_photos, show_search=True),
                        cls='container',
                        style='max-width: 1800px; margin: 0 auto; padding: 4rem 2rem;',
                    ),
                ),
            ),
            # Carousel script
            Script("""
                // Carousel with arrows and auto-rotate on hover
                document.addEventListener('DOMContentLoaded', function() {
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
                                    dot.style.background = i === index ? 'rgba(255, 255, 255, 0.8)' : 'rgba(255, 255, 255, 0.3)';
                                });

                                // Allow next transition after animation completes
                                setTimeout(() => {
                                    isTransitioning = false;
                                }, 250);
                            }, 250); // Half of the transition duration
                        }

                        function nextImage() {
                            if (isTransitioning) return;
                            const prevIndex = currentIndex;
                            currentIndex = (currentIndex + 1) % images.length;
                            showImage(currentIndex);
                        }

                        function prevImage() {
                            if (isTransitioning) return;
                            const prevIndex = currentIndex;
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
                        prevBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            prevImage();
                            stopCarousel();
                        });

                        nextBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            nextImage();
                            stopCarousel();
                        });

                        // Dot click handlers
                        dots.forEach((dot, index) => {
                            dot.addEventListener('click', (e) => {
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
                    });
                });
            """),
            # Load search filter script
            Script(src='/static/js/search-filter.js'),
            # Load lightbox script
            Script(src='/static/js/lightbox.js'),
            create_footer(),
            create_lightbox(),
        ),
    )
