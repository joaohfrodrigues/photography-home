"""Collection detail page component"""

from fasthtml.common import *

from components.ui.footer import create_footer
from components.ui.head import create_head
from components.ui.header import create_navbar
from components.ui.lightbox import create_lightbox
from config import EXIF_LAZY_LOADING
from services import fetch_collection_photos, fetch_user_collections


def create_collection_gallery_item(photo, index):
    """Create a single gallery item for collection view"""
    # Use raw Unsplash URL
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
        ''.join([f'<span class="lightbox-tag">{tag}</span>' for tag in tags[:10]]) if tags else ''
    )
    tags_str = ','.join(tags[:10]) if tags else ''

    # Extract year
    year = photo.get('created_at', '')[:4] if photo.get('created_at') else ''

    # Determine orientation
    orientation = 'square'
    if width > height * 1.1:
        orientation = 'landscape'
    elif height > width * 1.1:
        orientation = 'portrait'

    # Photographer info
    photographer_name = photo.get('user', {}).get('name', 'Unknown')
    photographer_url = photo.get('user', {}).get('profile_url', '')
    photo_unsplash_url = photo.get('links', {}).get('html', '')

    return Div(
        Img(src=img_src, alt=photo['title'], loading='lazy'),
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
        cls='gallery-item',
        style=f'aspect-ratio: {aspect_ratio:.3f};',
        **{
            'data-index': index,
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


def collection_detail_page(collection_id: str, page: int = 1):
    """Render a collection detail page with infinite scroll support"""
    # Get collection info
    collections = fetch_user_collections()
    collection = next((c for c in collections if c['id'] == collection_id), None)

    if not collection:
        # Collection not found
        return Html(
            create_head(title='Collection Not Found'),
            Body(
                create_navbar(current_page='collections'),
                Main(
                    Section(
                        Div(
                            H1('Collection Not Found', style='text-align: center;'),
                            P(
                                'The requested collection could not be found.',
                                style='text-align: center; color: #888;',
                            ),
                            A(
                                '← Back to Collections',
                                href='/collections',
                                style='display: block; text-align: center; margin-top: 2rem; color: #fff;',
                            ),
                            style='padding: 8rem 2rem 4rem;',
                        )
                    )
                ),
                create_footer(),
            ),
        )

    # Fetch photos for this collection
    photos, has_more = fetch_collection_photos(collection_id, page=page, per_page=30)

    gallery_items = [create_collection_gallery_item(photo, i) for i, photo in enumerate(photos)]

    return Html(
        create_head(
            title=f'{collection["title"]} | João Rodrigues',
            description=collection['description']
            or f'Browse {collection["total_photos"]} photos from {collection["title"]}',
            current_url=f'https://joaohfrodrigues.com/collection/{collection_id}',
        ),
        Body(
            create_navbar(current_page='collections'),
            # Collection header
            Section(
                Div(
                    A(
                        '← All Collections',
                        href='/collections',
                        style="""
                            color: #888;
                            text-decoration: none;
                            font-size: 0.9rem;
                            display: inline-block;
                            margin-bottom: 1rem;
                        """,
                        onmouseover="this.style.color='#fff'",
                        onmouseout="this.style.color='#888'",
                    ),
                    H1(
                        collection['title'],
                        style='font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 200; letter-spacing: 0.05em;',
                    ),
                    P(
                        f'{collection["total_photos"]} photos',
                        style='color: #888; font-size: 1.1rem; margin-bottom: 1rem;',
                    ),
                    P(
                        collection['description'],
                        style='color: #aaa; font-size: 1rem; line-height: 1.6; max-width: 800px;',
                    )
                    if collection['description']
                    else None,
                    cls='container',
                    style='max-width: 1400px; margin: 0 auto; padding: 8rem 2rem 2rem 2rem;',
                )
            ),
            # Gallery
            Main(
                Section(
                    Div(
                        Div(*gallery_items, cls='gallery-grid', id='gallery-grid'),
                        # Load more button (for infinite scroll)
                        Div(
                            Button(
                                'Load More',
                                id='load-more-btn',
                                style="""
                                    padding: 1rem 2rem;
                                    background: rgba(255, 255, 255, 0.1);
                                    border: none;
                                    color: #fff;
                                    border-radius: 6px;
                                    cursor: pointer;
                                    font-size: 1rem;
                                    transition: background 0.3s ease;
                                """,
                                onmouseover="this.style.background='rgba(255, 255, 255, 0.2)'",
                                onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'",
                                **{'data-collection-id': collection_id, 'data-page': str(page + 1)},
                            )
                            if has_more
                            else None,
                            style='text-align: center; padding: 2rem 0;',
                            id='load-more-container',
                        )
                        if has_more
                        else None,
                        cls='gallery',
                        id='gallery',
                    ),
                    cls='container',
                    style='max-width: 1400px; margin: 0 auto; padding: 1rem 2rem 4rem 2rem;',
                ),
            ),
            create_footer(),
            create_lightbox(),
            # Infinite scroll script
            Script(src='/static/js/infinite-scroll.js', defer=True) if has_more else None,
        ),
    )
