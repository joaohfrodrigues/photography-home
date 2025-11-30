"""Photo grid component with masonry layout"""

from fasthtml.common import *


def create_photo_card(photo, index=0):
    """Create a photo card for the masonry grid"""
    # Determine orientation for filtering
    aspect_ratio = photo['width'] / photo['height'] if photo['height'] > 0 else 1
    if aspect_ratio > 1.2:
        orientation = 'landscape'
    elif aspect_ratio < 0.8:
        orientation = 'portrait'
    else:
        orientation = 'square'

    # Get year from created_at if available
    year = ''
    if 'created_at' in photo and photo['created_at']:
        year = photo['created_at'][:4]  # Extract year from ISO date

    # Prepare data attributes for filtering
    tags = ', '.join(photo.get('tags', []))
    location_parts = []
    if photo.get('location'):
        if photo['location'].get('city'):
            location_parts.append(photo['location']['city'])
        if photo['location'].get('country'):
            location_parts.append(photo['location']['country'])
    location = ', '.join(location_parts)

    return A(
        Div(
            # Image
            Img(
                src=photo['url_thumb'],
                alt=photo['title'],
                loading='lazy' if index > 8 else 'eager',
                style="""
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    transition: transform 0.3s ease;
                """,
            ),
            # Overlay with title
            Div(
                H3(
                    photo['title'],
                    style='font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 300;',
                ),
                # Location and tags
                P(
                    location if location else 'No location',
                    style='font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem;',
                )
                if location
                else None,
                P(
                    f'Tags: {tags[:50]}...' if len(tags) > 50 else f'Tags: {tags}',
                    style='font-size: 0.75rem; color: rgba(255, 255, 255, 0.6);',
                )
                if tags
                else None,
                cls='photo-overlay',
                style="""
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    padding: 1.5rem;
                    background: linear-gradient(to top, rgba(0, 0, 0, 0.8), transparent);
                    opacity: 0;
                    transition: opacity 0.3s ease;
                """,
            ),
            style="""
                position: relative;
                width: 100%;
                overflow: hidden;
                border-radius: 8px;
                background: #1a1a1a;
            """,
        ),
        href=f'/photo/{photo["id"]}',
        cls='photo-card',
        style=f"""
            display: block;
            text-decoration: none;
            color: #fff;
            margin-bottom: 1.5rem;
            break-inside: avoid;
            opacity: 0;
            animation: fadeInScale 0.5s ease-out forwards;
            animation-delay: {min(index * 0.05, 1)}s;
        """,
        data_index=str(index),
        onmouseover="this.querySelector('.photo-overlay').style.opacity='1'; this.querySelector('img').style.transform='scale(1.05)'",
        onmouseout="this.querySelector('.photo-overlay').style.opacity='0'; this.querySelector('img').style.transform='scale(1)'",
        **{
            'data-title': photo['title'].lower(),
            'data-tags': tags.lower(),
            'data-location': location.lower(),
            'data-year': year,
            'data-orientation': orientation,
        },
    )


def create_photo_grid(photos, show_search=True):
    """Create a masonry photo grid with optional search bar"""
    from components.ui.search_bar import create_search_bar

    return Div(
        # Search bar (if enabled)
        create_search_bar() if show_search else None,
        # Results count
        Div(
            Span(
                f'{len(photos)} photos',
                id='results-count',
                style='color: rgba(255, 255, 255, 0.6); font-size: 0.9rem;',
            ),
            style='margin-bottom: 1.5rem;',
        ),
        # Photo grid
        Div(
            *[create_photo_card(photo, i) for i, photo in enumerate(photos)],
            cls='photo-grid',
            style="""
                column-count: 4;
                column-gap: 1.5rem;
            """,
        ),
        # Loading indicator for infinite scroll
        Div(
            Div(
                style="""
                    width: 40px;
                    height: 40px;
                    border: 3px solid rgba(255, 255, 255, 0.1);
                    border-top-color: #fff;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                """
            ),
            id='loading-indicator',
            style="""
                display: none;
                justify-content: center;
                padding: 3rem 0;
            """,
        ),
        cls='photo-grid-container',
    )
