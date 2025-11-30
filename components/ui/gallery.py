"""Gallery component"""

from fasthtml.common import *

from .filters import create_filters


def create_gallery(photos):
    """Create the gallery section with photo grid"""
    from config import EXIF_LAZY_LOADING

    gallery_items = []

    if photos:
        for i, photo in enumerate(photos):
            # Use raw Unsplash URL for hotlinking (required for API compliance)
            img_src = photo.get('url_raw', photo['url'])

            # Calculate aspect ratio
            width = photo.get('width', 1)
            height = photo.get('height', 1)
            aspect_ratio = width / height

            # Format camera info
            camera_full = 'Loading...' if EXIF_LAZY_LOADING else 'N/A'

            # Format location
            location_data = photo.get('location', {})
            location_parts = [
                location_data.get('name'),
                location_data.get('city'),
                location_data.get('country'),
            ]
            location_str = ', '.join([p for p in location_parts if p]) or ''

            # Format tags
            tags = photo.get('tags', [])
            tags_html = (
                ''.join([f'<span class="lightbox-tag">{tag}</span>' for tag in tags[:10]])
                if tags
                else ''
            )
            tags_str = ','.join(tags[:10]) if tags else ''

            # Extract year from created_at
            year = photo.get('created_at', '')[:4] if photo.get('created_at') else ''

            # Determine orientation
            orientation = 'square'
            if width > height * 1.1:
                orientation = 'landscape'
            elif height > width * 1.1:
                orientation = 'portrait'

            # Photographer info for attribution
            photographer_name = photo.get('user', {}).get('name', 'Unknown')
            photographer_url = photo.get('user', {}).get('profile_url', '')
            photo_unsplash_url = photo.get('links', {}).get('html', '')

            gallery_items.append(
                Div(
                    Img(src=img_src, alt=photo['title'], loading='lazy'),
                    Div(photo['title'], cls='photo-title'),
                    # Attribution overlay (visible on hover)
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
                    cls='gallery-item',
                    style=f'aspect-ratio: {aspect_ratio:.3f};',
                    **{
                        'data-index': i,
                        'data-photo-id': photo.get('id', ''),
                        'data-download-location': photo.get('links', {}).get(
                            'download_location', ''
                        ),
                        'data-description': photo.get('description', ''),
                        'data-title': photo['title'].lower(),
                        'data-tags': tags_html,
                        'data-tags-text': tags_str.lower(),
                        'data-created': photo.get('created_at', ''),
                        'data-year': year,
                        'data-orientation': orientation,
                        'data-color': photo.get('color', ''),
                        'data-location': location_str,
                        'data-camera': camera_full,
                        'data-exposure': 'N/A' if not EXIF_LAZY_LOADING else 'Loading...',
                        'data-aperture': 'N/A' if not EXIF_LAZY_LOADING else 'Loading...',
                        'data-focal': 'N/A' if not EXIF_LAZY_LOADING else 'Loading...',
                        'data-iso': 'N/A' if not EXIF_LAZY_LOADING else 'Loading...',
                        'data-likes': photo.get('likes', 0),
                        'data-dimensions': f'{width} × {height}',
                        'data-photographer': photographer_name,
                        'data-photographer-url': photographer_url,
                        'data-unsplash-url': photo_unsplash_url,
                        'data-lazy-exif': 'true' if EXIF_LAZY_LOADING else 'false',
                    },
                )
            )
    else:
        gallery_items.append(
            Div(P('No photos found. Please check your Unsplash configuration.'), cls='text-center')
        )

    return Div(
        H2('PORTFOLIO', cls='section-title'),
        create_filters(photos),
        Div(*gallery_items, cls='gallery-grid', id='gallery-grid'),
        cls='gallery',
        id='gallery',
    )
