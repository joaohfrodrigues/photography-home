"""Page layout components"""
from fasthtml.common import *


def create_head():
    """Create the HTML head section"""
    return Head(
        Title('João Rodrigues | Photography'),
        Meta(name='viewport', content='width=device-width, initial-scale=1'),
        Meta(name='description', content='Photography portfolio by João Rodrigues'),
        Meta(charset='utf-8'),
        Link(rel='stylesheet', href='/static/styles.css'),
        Script(src='/static/lightbox.js', type='text/javascript')
    )


def create_hero():
    """Create the hero section"""
    return Div(
        Div(
            H1('JOÃO RODRIGUES'),
            P('Photography'),
            cls='hero-content'
        ),
        Div(cls='scroll-indicator'),
        cls='hero',
        id='hero'
    )


def create_filters(photos):
    """Create filter controls"""
    # Extract unique values for filters
    tags = set()
    years = set()
    colors = set()
    
    for photo in photos:
        # Tags
        for tag in photo.get('tags', []):
            tags.add(tag)
        # Years
        created = photo.get('created_at', '')
        if created:
            year = created[:4]
            years.add(year)
        # Colors
        color = photo.get('color', '')
        if color:
            colors.add(color)
    
    tags = sorted(tags)
    years = sorted(years, reverse=True)
    
    return Div(
        Div(
            # Search
            Div(
                Input(
                    type='text',
                    id='search-input',
                    placeholder='🔍 Search photos, tags, or locations...',
                    cls='filter-input',
                    oninput='applyFilters()'
                ),
                cls='filter-group search-group'
            ),
            
            # Compact filters row
            Div(
                # Sort
                Div(
                    Select(
                        Option('Sort: Latest', value='latest', selected=True),
                        Option('Sort: Oldest', value='oldest'),
                        Option('Sort: Popular', value='popular'),
                        id='sort-select',
                        cls='filter-select',
                        onchange='applyFilters()'
                    ),
                    cls='filter-group-inline'
                ),
                
                # Year filter
                Div(
                    Select(
                        Option('Year: All', value='all', selected=True),
                        *[Option(f'{year}', value=year) for year in years],
                        id='year-select',
                        cls='filter-select',
                        onchange='applyFilters()'
                    ),
                    cls='filter-group-inline'
                ) if years else None,
                
                # Tag filter
                Div(
                    Select(
                        Option('Tag: All', value='all', selected=True),
                        *[Option(f'#{tag}', value=tag) for tag in tags[:15]],
                        id='tag-select',
                        cls='filter-select',
                        onchange='applyFilters()'
                    ),
                    cls='filter-group-inline'
                ) if tags else None,
                
                # Grid size
                Div(
                    Select(
                        Option('1 col', value='1'),
                        Option('2 cols', value='2'),
                        Option('3 cols', value='3', selected=True),
                        id='grid-select',
                        cls='filter-select',
                        onchange='changeGridSize()'
                    ),
                    cls='filter-group-inline'
                ),
                
                # Reset (icon only on desktop, text on mobile)
                Div(
                    Button(
                        Span('✕', cls='reset-icon'),
                        Span('Reset', cls='reset-text'),
                        onclick='resetFilters()', 
                        cls='filter-reset',
                        title='Reset all filters'
                    ),
                    cls='filter-group-inline'
                ),
                
                cls='filters-row'
            ),
            
            cls='filters-container'
        ),
        
        # Results count
        Div(
            Span('', id='results-count', cls='results-count'),
            cls='results-info'
        ),
        
        cls='filters-wrapper'
    )


def create_gallery(photos):
    """Create the gallery section"""
    import os
    from services import get_optimized_url
    from datetime import datetime
    from config import EXIF_LAZY_LOADING
    
    gallery_items = []
    
    if photos:
        for i, photo in enumerate(photos):
            # Use raw Unsplash URL for hotlinking (required for API compliance)
            # Only use Cloudinary if specifically needed for optimization
            img_src = photo.get('url_raw', photo['url'])
            
            # Calculate aspect ratio
            width = photo.get('width', 1)
            height = photo.get('height', 1)
            aspect_ratio = width / height
            
            # Format camera info (only if lazy loading is enabled, otherwise skip EXIF)
            if EXIF_LAZY_LOADING:
                camera_full = 'Loading...'  # Will be loaded on-demand
            else:
                camera_full = 'N/A'  # EXIF disabled
            
            # Format location
            location_data = photo.get('location', {})
            location_parts = [
                location_data.get('name'),
                location_data.get('city'),
                location_data.get('country')
            ]
            location_str = ', '.join([p for p in location_parts if p]) or ''
            
            # Format tags
            tags = photo.get('tags', [])
            tags_html = ''.join([f'<span class="lightbox-tag">{tag}</span>' for tag in tags[:10]]) if tags else ''
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
            photographer_username = photo.get('user', {}).get('username', '')
            photographer_url = photo.get('user', {}).get('profile_url', '')
            photo_unsplash_url = photo.get('links', {}).get('html', '')
            
            gallery_items.append(
                Div(
                    Img(
                        src=img_src,
                        alt=photo['title'],
                        loading='lazy'
                    ),
                    Div(photo['title'], cls='photo-title'),
                    # Attribution overlay (visible on hover)
                    Div(
                        Span('Photo by '),
                        A(photographer_name, 
                          href=photographer_url, 
                          target='_blank',
                          rel='noopener noreferrer',
                          style='color: #fff; text-decoration: underline;'),
                        Span(' on '),
                        A('Unsplash',
                          href='https://unsplash.com',
                          target='_blank',
                          rel='noopener noreferrer',
                          style='color: #fff; text-decoration: underline;'),
                        cls='photo-attribution'
                    ),
                    cls='gallery-item',
                    style=f'aspect-ratio: {aspect_ratio:.3f};',
                    **{
                        'data-index': i,
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
                        'data-dimensions': f"{width} × {height}",
                        'data-photographer': photographer_name,
                        'data-photographer-url': photographer_url,
                        'data-unsplash-url': photo_unsplash_url,
                        'data-lazy-exif': 'true' if EXIF_LAZY_LOADING else 'false',
                    }
                )
            )
    else:
        gallery_items.append(
            Div(
                P('No photos found. Please check your Unsplash configuration.'),
                cls='text-center'
            )
        )
    
    return Div(
        H2('PORTFOLIO', cls='section-title'),
        create_filters(photos),
        Div(*gallery_items, cls='gallery-grid', id='gallery-grid'),
        cls='gallery',
        id='gallery'
    )


def create_lightbox():
    """Create the lightbox modal"""
    return Div(
        Div(
            Button('×', cls='lightbox-close', onclick='closeLightbox()'),
            Button('‹', cls='lightbox-nav lightbox-prev', onclick='navigateLightbox(-1)'),
            Button('›', cls='lightbox-nav lightbox-next', onclick='navigateLightbox(1)'),
            Div(
                Div(
                    Img(src='', alt='', id='lightbox-img', cls='lightbox-image'),
                    cls='lightbox-image-container'
                ),
                Div(
                    H2('', id='lightbox-title', cls='lightbox-title'),
                    P('', id='lightbox-description', cls='lightbox-description'),
                    
                    # Basic Info
                    Div(
                        Div(cls='lightbox-section-title', innerText='Details'),
                        Div(
                            Span('Date', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-created'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item'
                        ),
                        Div(
                            Span('Size', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-dimensions'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item'
                        ),
                        Div(
                            Span('Location', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-location'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            style='display: none;'
                        ),
                        cls='lightbox-meta'
                    ),
                    
                    # Camera Info
                    Div(
                        Div(cls='lightbox-section-title', innerText='Camera Settings'),
                        Div(
                            Span('Camera', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-camera'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='camera-item'
                        ),
                        Div(
                            Span('Shutter', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-exposure'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='exposure-item'
                        ),
                        Div(
                            Span('Aperture', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-aperture'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='aperture-item'
                        ),
                        Div(
                            Span('Focal', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-focal'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='focal-item'
                        ),
                        Div(
                            Span('ISO', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-iso'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item',
                            id='iso-item'
                        ),
                        id='camera-section',
                        cls='lightbox-meta',
                        style='display: block;'
                    ),
                    
                    # Tags
                    Div(
                        Div(cls='lightbox-section-title', innerText='Tags'),
                        Div(
                            Span('Keywords', cls='lightbox-meta-label'),
                            Div(Span('', id='meta-tags', cls='lightbox-tags'), cls='lightbox-meta-content'),
                            cls='lightbox-meta-item'
                        ),
                        cls='lightbox-meta'
                    ),
                    
                    # Photo Index
                    Div(
                        Div(
                            Span('Photo ', cls='lightbox-meta-label'),
                            Span('', id='lightbox-index'),
                            cls='lightbox-meta-item'
                        ),
                        cls='lightbox-meta'
                    ),
                    
                    # Unsplash Attribution (required)
                    Div(
                        Div(cls='lightbox-section-title', innerText='Attribution'),
                        Div(
                            P(
                                Span('Photo by '),
                                A('', 
                                  id='photographer-link',
                                  href='#',
                                  target='_blank',
                                  rel='noopener noreferrer',
                                  style='color: #aaa; text-decoration: underline;'),
                                Span(' on '),
                                A('Unsplash',
                                  href='https://unsplash.com',
                                  target='_blank',
                                  rel='noopener noreferrer',
                                  style='color: #aaa; text-decoration: underline;'),
                                style='font-size: 0.85rem; color: #666; margin: 0;'
                            ),
                            Div(
                                A('View on Unsplash →',
                                  id='unsplash-link',
                                  href='#',
                                  target='_blank',
                                  rel='noopener noreferrer',
                                  style='color: #888; text-decoration: none; font-size: 0.85rem; display: inline-block; margin-top: 0.5rem;'),
                            ),
                            cls='lightbox-meta-item',
                            style='display: block;'
                        ),
                        cls='lightbox-meta'
                    ),
                    cls='lightbox-details'
                ),
                cls='lightbox-content'
            ),
            cls='lightbox',
            id='lightbox',
            onclick='event.target.id === "lightbox" && closeLightbox()'
        )
    )


def create_footer():
    """Create the footer section"""
    return Footer(
        P('© 2025 João Rodrigues. All rights reserved.'),
        P(A('Contact', href='mailto:contact@joaohfrodrigues.com'))
    )
