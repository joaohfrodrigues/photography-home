"""Unified photo card and container components for gallery and grid layouts"""

from fasthtml.common import *

from components.ui.filters import create_filters
from components.ui.search_bar import create_search_bar
from config import DEFAULT_EXIF_VALUES


def _format_location(location_data):
    """Extract and format location from location dict."""
    if not location_data:
        return ''
    parts = []
    if location_data.get('name'):
        parts.append(location_data['name'])
    else:
        if location_data.get('city'):
            parts.append(location_data['city'])
        if location_data.get('country'):
            parts.append(location_data['country'])
    return ', '.join(parts)


def _format_exif(exif):
    """Extract and format EXIF data with defaults."""
    exif = exif or {}
    make = exif.get('make') or DEFAULT_EXIF_VALUES['make']
    model = exif.get('model') or DEFAULT_EXIF_VALUES['model']
    camera = f'{make} {model}'.strip() if make or model else DEFAULT_EXIF_VALUES['make']
    exposure = exif.get('exposure_time') or DEFAULT_EXIF_VALUES['exposure_time']
    aperture = (
        f"f/{exif.get('aperture')}" if exif.get('aperture') else DEFAULT_EXIF_VALUES['aperture']
    )
    focal = (
        f"{exif.get('focal_length')}mm"
        if exif.get('focal_length')
        else DEFAULT_EXIF_VALUES['focal_length']
    )
    iso = str(exif.get('iso')) if exif.get('iso') else DEFAULT_EXIF_VALUES['iso']
    return camera, exposure, aperture, focal, iso


def _create_attribution():
    """Create reusable attribution overlay."""
    return Div(
        Span('Photo by '),
        A(
            '...',  # Placeholder - filled by caller
            href='#',
            target='_blank',
            rel='noopener noreferrer',
        ),
        Span(' on '),
        A(
            'Unsplash',
            href='https://unsplash.com',
            target='_blank',
            rel='noopener noreferrer',
        ),
        cls='photo-attribution',
    )


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

    # Extract and format data
    year = photo.get('created_at', '')[:4] if photo.get('created_at') else ''
    location = _format_location(photo.get('location'))
    tags = photo.get('tags', [])
    tags_html = (
        ''.join([f'<span class="lightbox-tag">{tag}</span>' for tag in tags[:10]]) if tags else ''
    )
    tags_str = ', '.join(tags)

    # Photographer info
    photographer_name = photo.get('user', {}).get('name', 'Unknown')
    photographer_url = photo.get('user', {}).get('profile_url', '')
    photo_unsplash_url = photo.get('links', {}).get('html', '')

    # EXIF data with defaults for display
    camera, exposure, aperture, focal, iso = _format_exif(photo.get('exif'))

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
        'data-camera': camera,
        'data-exposure': exposure,
        'data-aperture': aperture,
        'data-focal': focal,
        'data-iso': iso,
        'data-views': str(photo.get('views', 0)),
        'data-downloads': str(photo.get('downloads', 0)),
        'data-dimensions': f'{width} × {height}',
        'data-photographer': photographer_name,
        'data-photographer-url': photographer_url,
        'data-unsplash-url': photo_unsplash_url,
        'data-lazy-exif': 'false',
        'data-lightbox-url': photo.get('url_raw', photo.get('url_regular', photo.get('url', ''))),
    }

    # Image source and layout-specific styling
    img_src = photo.get('url_regular', photo['url'])
    is_gallery = layout == 'gallery'

    if is_gallery:
        img_loading = 'lazy'
        css_class = 'gallery-item'
        style = f'aspect-ratio: {aspect_ratio:.3f};'
        img_style = None
    else:
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
        img_style = """
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: block;
            transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        """

    # Build photo image
    img = Img(
        src=img_src,
        alt=photo['title'],
        loading=img_loading,
        style=img_style,
    )

    # Build attribution
    attribution = Div(
        Span('Photo by '),
        A(
            photographer_name,
            href=photographer_url,
            target='_blank',
            rel='noopener noreferrer',
        ),
        Span(' on '),
        A(
            'Unsplash',
            href='https://unsplash.com',
            target='_blank',
            rel='noopener noreferrer',
        ),
        cls='photo-attribution',
    )

    # Return unified structure
    return Div(
        img,
        Div(photo['title'], cls='photo-title'),
        attribution,
        cls=css_class,
        style=style,
        **data_attrs,
    )


def create_photo_container(
    photos,
    layout='gallery',
    title=None,
    show_filters=False,
    show_search=False,
    show_count=True,
    current_order='popular',
    search_query='',
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
        current_order: Current sort order for search bar
        search_query: Current search query for search bar

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
        return Div(
            H2(title, cls='section-title') if title else None,
            create_filters(photos) if show_filters else None,
            Div(*photo_items, cls='gallery-grid', id='gallery-grid'),
            cls='gallery',
            id='gallery',
        )
    else:
        # Grid layout for homepage - use explicit columns
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
            create_search_bar(current_order=current_order, search_query=search_query)
            if show_search
            else None,
            # Results count
            Div(
                Span(
                    f'{len(photos)} photos',
                    id='results-count',
                    style='color: var(--text-secondary); font-size: 0.9rem;',
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
                        border-top-color: var(--text-primary);
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
