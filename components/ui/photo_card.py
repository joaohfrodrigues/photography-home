"""Unified photo card and container components for gallery and grid layouts"""

from fasthtml.common import *


def distribute_to_columns(photos, num_columns=3):
    """
    Distribute photos to columns using height-aware algorithm.
    Always appends to the shortest column for balanced layout.

    Args:
        photos: List of photo dicts with width/height
        num_columns: Number of columns (default 3)

    Returns:
        List of lists, where each inner list is a column of photos
    """
    columns = [[] for _ in range(num_columns)]
    column_heights = [0.0] * num_columns

    for photo in photos:
        # Calculate aspect ratio (height in relative units)
        width = photo.get('width', 1)
        height = photo.get('height', 1)
        aspect_ratio = width / height if height > 0 else 1

        # Height in relative units (assuming width=1)
        photo_height = 1.0 / aspect_ratio if aspect_ratio > 0 else 1.0

        # Find shortest column
        shortest_idx = column_heights.index(min(column_heights))

        # Add photo to shortest column
        columns[shortest_idx].append(photo)
        column_heights[shortest_idx] += photo_height

    return columns


def create_photo_item(photo, index=0, layout='gallery'):
    """
    Create a unified photo item that works for both gallery and grid layouts.

    Args:
        photo: Photo dict with all photo data
        index: Photo index for animations and data-index
        layout: 'gallery' for collection pages, 'grid' for homepage masonry

    Returns:
        Div element with appropriate structure for the layout
    """
    from config import EXIF_LAZY_LOADING

    # Calculate dimensions and orientation
    width = photo.get('width', 1)
    height = photo.get('height', 1)
    aspect_ratio = width / height if height > 0 else 1

    if aspect_ratio > 1.2:
        orientation = 'landscape'
    elif aspect_ratio < 0.8:
        orientation = 'portrait'
    else:
        orientation = 'square'

    # Extract year
    year = photo.get('created_at', '')[:4] if photo.get('created_at') else ''

    # Format location
    location_parts = []
    if photo.get('location'):
        location_data = photo['location']
        if location_data.get('name'):
            location_parts.append(location_data['name'])
        elif location_data.get('city') or location_data.get('country'):
            if location_data.get('city'):
                location_parts.append(location_data['city'])
            if location_data.get('country'):
                location_parts.append(location_data['country'])
    location = ', '.join(location_parts)

    # Format tags
    tags = photo.get('tags', [])
    tags_html = (
        ''.join([f'<span class="lightbox-tag">{tag}</span>' for tag in tags[:10]]) if tags else ''
    )
    tags_str = ', '.join(tags)

    # Photographer info
    photographer_name = photo.get('user', {}).get('name', 'Unknown')
    photographer_url = photo.get('user', {}).get('profile_url', '')
    photo_unsplash_url = photo.get('links', {}).get('html', '')

    # EXIF data
    camera_full = 'Loading...' if EXIF_LAZY_LOADING else 'N/A'
    exif_placeholder = 'Loading...' if EXIF_LAZY_LOADING else 'N/A'

    # Common data attributes
    data_attrs = {
        'data-index': str(index),
        'data-photo-id': photo.get('id', ''),
        'data-download-location': photo.get('links', {}).get('download_location', ''),
        'data-description': photo.get('description', ''),
        'data-title': photo['title'].lower(),
        'data-tags': tags_html,
        'data-tags-text': tags_str.lower(),
        'data-created': photo.get('created_at', ''),
        'data-year': year,
        'data-orientation': orientation,
        'data-color': photo.get('color', ''),
        'data-location': location,
        'data-camera': camera_full,
        'data-exposure': exif_placeholder,
        'data-aperture': exif_placeholder,
        'data-focal': exif_placeholder,
        'data-iso': exif_placeholder,
        'data-views': str(photo.get('views', 0)),
        'data-downloads': str(photo.get('downloads', 0)),
        'data-dimensions': f'{width} × {height}',
        'data-photographer': photographer_name,
        'data-photographer-url': photographer_url,
        'data-unsplash-url': photo_unsplash_url,
        'data-lazy-exif': 'true' if EXIF_LAZY_LOADING else 'false',
        'data-lightbox-url': photo.get('url_raw', photo.get('url_regular', photo.get('url', ''))),
    }

    # Choose image URL based on layout
    if layout == 'gallery':
        img_src = photo.get('url_regular', photo['url'])
        img_loading = 'lazy'
        css_class = 'gallery-item'
        style = f'aspect-ratio: {aspect_ratio:.3f};'
    else:  # grid layout for homepage
        img_src = photo.get('url_regular', photo['url'])  # Regular quality for display
        img_loading = 'lazy' if index > 8 else 'eager'
        css_class = 'photo-card gallery-item'
        style = f"""
            position: relative;
            width: 100%;
            overflow: hidden;
            border-radius: 8px;
            background: #1a1a1a;
            opacity: 0;
            animation: fadeInScale 0.5s ease-out forwards;
            animation-delay: {min(index * 0.05, 1)}s;
            cursor: pointer;
            aspect-ratio: {aspect_ratio:.3f};
        """

    # Build the photo item
    if layout == 'gallery':
        # Gallery layout (collection pages)
        return Div(
            Img(src=img_src, alt=photo['title'], loading=img_loading),
            Div(photo['title'], cls='photo-title'),
            # Attribution overlay
            Div(
                Span('Photo by '),
                A(
                    photographer_name,
                    href=photographer_url,
                    target='_blank',
                    rel='noopener noreferrer',
                    style='color: #fff; text-decoration: underline;',
                ),
                Span(' on '),
                A(
                    'Unsplash',
                    href='https://unsplash.com',
                    target='_blank',
                    rel='noopener noreferrer',
                    style='color: #fff; text-decoration: underline;',
                ),
                cls='photo-attribution',
            ),
            cls=css_class,
            style=style,
            **data_attrs,
        )
    else:
        # Grid layout (homepage masonry)
        views = photo.get('views', 0)
        downloads = photo.get('downloads', 0)

        return Div(
            Img(
                src=img_src,
                alt=photo['title'],
                loading=img_loading,
                style="""
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                    transition: transform 0.3s ease;
                """,
            ),
            # Hidden title element for lightbox
            Div(photo['title'], cls='photo-title', style='display: none;'),
            # Overlay with title and info
            Div(
                H3(
                    photo['title'],
                    style='font-size: 1.1rem; margin-bottom: 0.5rem; font-weight: 300;',
                ),
                P(
                    location,
                    style='font-size: 0.85rem; color: rgba(255, 255, 255, 0.7); margin-bottom: 0.25rem;',
                )
                if location
                else None,
                P(
                    f'Tags: {tags_str[:50]}...' if len(tags_str) > 50 else f'Tags: {tags_str}',
                    style='font-size: 0.75rem; color: rgba(255, 255, 255, 0.6);',
                )
                if tags_str
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
            # Stats overlay (views and downloads)
            Div(
                Div(
                    Span('👁️', style='opacity: 0.8;'),
                    Span(f'{views:,}' if views > 0 else '—', style='margin-left: 4px;'),
                    cls='stat-item',
                )
                if views > 0
                else None,
                Div(
                    Span('⬇️', style='opacity: 0.8;'),
                    Span(f'{downloads:,}' if downloads > 0 else '—', style='margin-left: 4px;'),
                    cls='stat-item',
                )
                if downloads > 0
                else None,
                cls='photo-stats',
            )
            if (views > 0 or downloads > 0)
            else None,
            cls=css_class,
            style=style,
            onmouseover="this.querySelector('.photo-overlay').style.opacity='1'; this.querySelector('img').style.transform='scale(1.05)'",
            onmouseout="this.querySelector('.photo-overlay').style.opacity='0'; this.querySelector('img').style.transform='scale(1)'",
            **data_attrs,
        )


def create_photo_container(
    photos, layout='gallery', title=None, show_filters=False, show_search=False, show_count=True
):
    """
    Create a unified photo container that works for both gallery and grid layouts.

    Args:
        photos: List of photo dicts
        layout: 'gallery' for collection pages, 'grid' for homepage masonry
        title: Optional section title (e.g., 'PORTFOLIO')
        show_filters: Whether to show filter controls
        show_search: Whether to show search bar
        show_count: Whether to show results count

    Returns:
        Div element with complete photo container structure
    """
    photo_items = []

    if photos:
        for i, photo in enumerate(photos):
            photo_items.append(create_photo_item(photo, index=i, layout=layout))
    else:
        photo_items.append(
            Div(P('No photos found. Please check your Unsplash configuration.'), cls='text-center')
        )

    # Build container based on layout
    if layout == 'gallery':
        # Gallery layout for collection pages
        from .filters import create_filters

        return Div(
            H2(title, cls='section-title') if title else None,
            create_filters(photos) if show_filters else None,
            Div(*photo_items, cls='gallery-grid', id='gallery-grid'),
            cls='gallery',
            id='gallery',
        )
    else:
        # Grid layout for homepage - use explicit columns
        from components.ui.search_bar import create_search_bar

        # Distribute photos to 3 columns using height-aware algorithm
        columns = distribute_to_columns(photos, num_columns=3)

        # Create column divs
        column_divs = []
        for col_idx, column_photos in enumerate(columns):
            column_items = []
            for photo in column_photos:
                # Find original index for animation timing
                original_idx = photos.index(photo)
                column_items.append(create_photo_item(photo, index=original_idx, layout='grid'))

            column_divs.append(
                Div(
                    *column_items,
                    cls='masonry-column',
                    id=f'col-{col_idx}',
                    style="""
                        flex: 1;
                        display: flex;
                        flex-direction: column;
                        gap: 1.5rem;
                    """,
                )
            )

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
            )
            if show_count
            else None,
            # Masonry grid with explicit columns
            Div(
                *column_divs,
                cls='photo-grid',
                style="""
                    display: flex;
                    flex-direction: row;
                    gap: 1.5rem;
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
