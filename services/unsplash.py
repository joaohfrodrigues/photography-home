"""Unsplash API integration and caching"""

import logging
import time

import requests

from config import CACHE_DURATION_MINUTES, EXIF_LAZY_LOADING, UNSPLASH_ACCESS_KEY, UNSPLASH_USERNAME

logger = logging.getLogger(__name__)

# Cache storage
_photo_cache = {'data': None, 'timestamp': None}


def is_cache_valid():
    """Check if the cached data is still valid"""
    if _photo_cache['data'] is None or _photo_cache['timestamp'] is None:
        return False

    cache_age = time.time() - _photo_cache['timestamp']
    cache_valid = cache_age < (CACHE_DURATION_MINUTES * 60)

    if cache_valid:
        logger.debug(f'Cache hit - age: {cache_age:.1f}s / {CACHE_DURATION_MINUTES*60}s')
    else:
        logger.debug(f'Cache expired - age: {cache_age:.1f}s')

    return cache_valid


def _get_fallback_photos():
    """Return placeholder images when no API key is configured"""
    logger.warning('No Unsplash API key configured. Using placeholder images.')
    return [
        {
            'url': f'https://picsum.photos/800/600?random={i}',
            'title': f'Sample {i+1}',
            'description': '',
        }
        for i in range(6)
    ]


def _transform_photo_data(photos):
    """Transform raw Unsplash API response into our photo data structure"""
    photo_data = []
    for i, photo in enumerate(photos):
        photo_data.append(
            {
                'id': photo['id'],
                'url': photo['urls']['full'],
                'url_raw': photo['urls']['raw'],
                'url_regular': photo['urls']['regular'],
                'url_thumb': photo['urls']['small'],
                'title': photo.get('description') or photo.get('alt_description') or f'Photo {i+1}',
                'description': photo.get('description', ''),
                'alt_description': photo.get('alt_description', ''),
                'likes': photo.get('likes', 0),
                'width': photo.get('width', 1),
                'height': photo.get('height', 1),
                'created_at': photo.get('created_at', ''),
                'updated_at': photo.get('updated_at', ''),
                'color': photo.get('color', '#000000'),
                'blur_hash': photo.get('blur_hash', ''),
                'exif': {
                    'make': photo.get('exif', {}).get('make', 'Unknown'),
                    'model': photo.get('exif', {}).get('model', 'Unknown'),
                    'exposure_time': photo.get('exif', {}).get('exposure_time', 'N/A'),
                    'aperture': photo.get('exif', {}).get('aperture', 'N/A'),
                    'focal_length': photo.get('exif', {}).get('focal_length', 'N/A'),
                    'iso': photo.get('exif', {}).get('iso', 'N/A'),
                },
                'location': {
                    'name': photo.get('location', {}).get('name')
                    if photo.get('location')
                    else None,
                    'city': photo.get('location', {}).get('city')
                    if photo.get('location')
                    else None,
                    'country': photo.get('location', {}).get('country')
                    if photo.get('location')
                    else None,
                },
                'tags': [tag.get('title', '') for tag in photo.get('tags', [])],
                'user': {
                    'name': photo.get('user', {}).get('name', 'Unknown'),
                    'username': photo.get('user', {}).get('username', ''),
                    'portfolio_url': photo.get('user', {}).get('portfolio_url', ''),
                    'profile_url': f"https://unsplash.com/@{photo.get('user', {}).get('username', '')}"
                    if photo.get('user', {}).get('username')
                    else '',
                },
                'links': {
                    'html': photo.get('links', {}).get('html', ''),
                    'download': photo.get('links', {}).get('download', ''),
                    'download_location': photo.get('links', {}).get('download_location', ''),
                },
            }
        )
    return photo_data


def _log_exif_info(photos):
    """Log EXIF data availability information"""
    if EXIF_LAZY_LOADING:
        logger.info(
            'EXIF lazy loading enabled - EXIF will be fetched on-demand when viewing photos'
        )
    else:
        logger.info('EXIF lazy loading disabled - no EXIF data will be loaded')

    exif_count = sum(1 for photo in photos if photo.get('exif'))
    logger.info(f'Photos with EXIF data in initial response: {exif_count}/{len(photos)}')

    if photos and photos[0].get('exif'):
        logger.debug(f"Sample EXIF data: {photos[0].get('exif')}")
    else:
        logger.warning('First photo has no EXIF data - checking raw response')
        if photos:
            logger.debug(f'First photo keys: {list(photos[0].keys())}')


def _fetch_from_api():
    """Fetch photos from Unsplash API"""
    logger.info(f'Fetching photos for Unsplash user: {UNSPLASH_USERNAME}')
    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}

    response = requests.get(
        f'https://api.unsplash.com/users/{UNSPLASH_USERNAME}/photos',
        headers=headers,
        params={'per_page': 30, 'order_by': 'latest', 'stats': 'true'},
        timeout=10,
    )

    if response.status_code != 200:
        logger.error(f'Unsplash API error: {response.status_code} - {response.text}')
        return None

    photos = response.json()
    logger.info(f'Successfully fetched {len(photos)} photos from Unsplash')
    _log_exif_info(photos)
    return _transform_photo_data(photos)


def _update_cache(photo_data):
    """Update the photo cache with new data"""
    _photo_cache['data'] = photo_data
    _photo_cache['timestamp'] = time.time()
    logger.info(f'Cached {len(photo_data)} photos for {CACHE_DURATION_MINUTES} minutes')


def _get_cached_or_empty():
    """Return cached data if available, otherwise empty list"""
    if _photo_cache['data']:
        logger.warning('Returning stale cache due to error')
        return _photo_cache['data']
    return []


def fetch_unsplash_photos():
    """Fetch photos from your Unsplash account with caching"""
    # Check cache first
    if is_cache_valid():
        logger.info('Using cached Unsplash photos')
        return _photo_cache['data']

    logger.info('Cache miss - fetching fresh data from Unsplash')

    # Return placeholder if no API key
    if not UNSPLASH_ACCESS_KEY:
        return _get_fallback_photos()

    # Fetch from API with comprehensive error handling
    try:
        photo_data = _fetch_from_api()
        if photo_data is not None:
            _update_cache(photo_data)
            return photo_data
    except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
        error_type = 'timed out' if isinstance(e, requests.exceptions.Timeout) else 'failed'
        logger.error(f'Unsplash API request {error_type}: {e}')
    except Exception as e:
        logger.error(f'Unexpected error fetching Unsplash photos: {e}', exc_info=True)

    # If we get here, something went wrong - return cached data or empty list
    return _get_cached_or_empty()


# Collections cache storage
_collections_cache = {'data': None, 'timestamp': None}
_collection_photos_cache = {}  # Key: f"{collection_id}:page:{page_num}"


def fetch_user_collections():
    """
    Fetch all collections for the configured Unsplash user.
    Results are cached for 24 hours.

    Returns:
        List of collection dictionaries with id, title, description, photo count, cover photo
    """
    # Check cache (24 hour cache for collections)
    if _collections_cache['data'] and _collections_cache['timestamp']:
        cache_age = time.time() - _collections_cache['timestamp']
        if cache_age < (24 * 60 * 60):  # 24 hours
            logger.info('Using cached collections')
            return _collections_cache['data']

    if not UNSPLASH_ACCESS_KEY:
        logger.warning('No Unsplash API key - cannot fetch collections')
        return []

    logger.info(f'Fetching collections for user: {UNSPLASH_USERNAME}')
    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}

    try:
        response = requests.get(
            f'https://api.unsplash.com/users/{UNSPLASH_USERNAME}/collections',
            headers=headers,
            timeout=10,
        )

        if response.status_code != 200:
            logger.error(f'Collections API error: {response.status_code}')
            return _collections_cache.get('data', [])

        collections = response.json()

        # Transform to simplified structure
        collection_data = [
            {
                'id': c['id'],
                'title': c['title'],
                'description': c.get('description', ''),
                'total_photos': c.get('total_photos', 0),
                'cover_photo': {
                    'url': c.get('cover_photo', {}).get('urls', {}).get('regular', ''),
                    'url_small': c.get('cover_photo', {}).get('urls', {}).get('small', ''),
                    'color': c.get('cover_photo', {}).get('color', '#ccc'),
                },
                'published_at': c.get('published_at', ''),
                'updated_at': c.get('updated_at', ''),
            }
            for c in collections
        ]

        # Update cache
        _collections_cache['data'] = collection_data
        _collections_cache['timestamp'] = time.time()
        logger.info(f'Cached {len(collection_data)} collections')

        return collection_data

    except Exception as e:
        logger.error(f'Error fetching collections: {e}', exc_info=True)
        return _collections_cache.get('data', [])


def fetch_collection_photos(collection_id: str, page: int = 1, per_page: int = 30):
    """
    Fetch photos from a specific collection with pagination.
    Results are cached per page for 1 hour.

    Args:
        collection_id: The Unsplash collection ID
        page: Page number (1-indexed)
        per_page: Number of photos per page (max 30)

    Returns:
        Tuple of (photos list, has_more_pages boolean)
    """
    cache_key = f'{collection_id}:page:{page}'

    # Check cache (1 hour cache for collection photos)
    if cache_key in _collection_photos_cache:
        cached_data = _collection_photos_cache[cache_key]
        cache_age = time.time() - cached_data['timestamp']
        if cache_age < (60 * 60):  # 1 hour
            logger.info(f'Using cached photos for {cache_key}')
            return cached_data['photos'], cached_data['has_more']

    if not UNSPLASH_ACCESS_KEY:
        logger.warning('No Unsplash API key - cannot fetch collection photos')
        return [], False

    logger.info(f'Fetching collection {collection_id}, page {page}')
    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}

    try:
        response = requests.get(
            f'https://api.unsplash.com/collections/{collection_id}/photos',
            headers=headers,
            params={'page': page, 'per_page': per_page, 'order_by': 'latest'},
            timeout=10,
        )

        if response.status_code != 200:
            logger.error(f'Collection photos API error: {response.status_code}')
            return [], False

        photos = response.json()
        photo_data = _transform_photo_data(photos)

        # Determine if there are more pages
        # If we got fewer photos than requested, we're on the last page
        has_more = len(photos) == per_page

        # Update cache
        _collection_photos_cache[cache_key] = {
            'photos': photo_data,
            'has_more': has_more,
            'timestamp': time.time(),
        }
        logger.info(f'Cached {len(photo_data)} photos for {cache_key}')

        return photo_data, has_more

    except Exception as e:
        logger.error(f'Error fetching collection photos: {e}', exc_info=True)
        # Return cached data if available
        if cache_key in _collection_photos_cache:
            cached = _collection_photos_cache[cache_key]
            return cached['photos'], cached['has_more']
        return [], False
