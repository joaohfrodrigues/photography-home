"""Unsplash API integration and caching"""
import requests
import time
import logging
from config import UNSPLASH_ACCESS_KEY, UNSPLASH_USERNAME, CACHE_DURATION_MINUTES, EXIF_LAZY_LOADING

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
        logger.debug(f"Cache hit - age: {cache_age:.1f}s / {CACHE_DURATION_MINUTES*60}s")
    else:
        logger.debug(f"Cache expired - age: {cache_age:.1f}s")
    
    return cache_valid


def fetch_unsplash_photos():
    """Fetch photos from your Unsplash account with caching"""
    # Check cache first
    if is_cache_valid():
        logger.info("Using cached Unsplash photos")
        return _photo_cache['data']
    
    logger.info("Cache miss - fetching fresh data from Unsplash")
    
    if not UNSPLASH_ACCESS_KEY:
        logger.warning("No Unsplash API key configured. Using placeholder images.")
        fallback_data = [
            {'url': f'https://picsum.photos/800/600?random={i}', 'title': f'Sample {i+1}', 'description': ''}
            for i in range(6)
        ]
        return fallback_data
    
    try:
        logger.info(f"Fetching photos for Unsplash user: {UNSPLASH_USERNAME}")
        headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
        
        # Use the /users/{username}/photos endpoint with stats to get EXIF data
        # Note: EXIF data is only included if it exists on the original upload
        response = requests.get(
            f'https://api.unsplash.com/users/{UNSPLASH_USERNAME}/photos',
            headers=headers,
            params={
                'per_page': 30, 
                'order_by': 'latest',
                'stats': 'true',  # Include statistics which helps with EXIF
            },
            timeout=10
        )
        
        if response.status_code == 200:
            photos = response.json()
            logger.info(f"Successfully fetched {len(photos)} photos from Unsplash")
            
            # EXIF loading strategy based on configuration
            if EXIF_LAZY_LOADING:
                logger.info("EXIF lazy loading enabled - EXIF will be fetched on-demand when viewing photos")
            else:
                logger.info("EXIF lazy loading disabled - no EXIF data will be loaded")
            
            # Log EXIF data availability with details
            exif_count = sum(1 for photo in photos if photo.get('exif'))
            logger.info(f"Photos with EXIF data in initial response: {exif_count}/{len(photos)}")
            
            # Debug: Log first photo's EXIF to see what we're getting
            if photos and photos[0].get('exif'):
                logger.debug(f"Sample EXIF data: {photos[0].get('exif')}")
            else:
                logger.warning("First photo has no EXIF data - checking raw response")
                if photos:
                    logger.debug(f"First photo keys: {list(photos[0].keys())}")
            
            logger.debug(f"Photo titles: {[p.get('description') or p.get('alt_description') for p in photos[:5]]}")
            
            photo_data = [
                {
                    'id': photo['id'],
                    'url': photo['urls']['full'],  # Higher quality than 'regular'
                    'url_raw': photo['urls']['raw'],  # Original Unsplash URL for hotlinking
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
                    # EXIF data
                    'exif': {
                        'make': photo.get('exif', {}).get('make', 'Unknown'),
                        'model': photo.get('exif', {}).get('model', 'Unknown'),
                        'exposure_time': photo.get('exif', {}).get('exposure_time', 'N/A'),
                        'aperture': photo.get('exif', {}).get('aperture', 'N/A'),
                        'focal_length': photo.get('exif', {}).get('focal_length', 'N/A'),
                        'iso': photo.get('exif', {}).get('iso', 'N/A'),
                    },
                    # Location
                    'location': {
                        'name': photo.get('location', {}).get('name') if photo.get('location') else None,
                        'city': photo.get('location', {}).get('city') if photo.get('location') else None,
                        'country': photo.get('location', {}).get('country') if photo.get('location') else None,
                    },
                    # Tags
                    'tags': [tag.get('title', '') for tag in photo.get('tags', [])],
                    # User info (photographer)
                    'user': {
                        'name': photo.get('user', {}).get('name', 'Unknown'),
                        'username': photo.get('user', {}).get('username', ''),
                        'portfolio_url': photo.get('user', {}).get('portfolio_url', ''),
                        'profile_url': f"https://unsplash.com/@{photo.get('user', {}).get('username', '')}" if photo.get('user', {}).get('username') else '',
                    },
                    # Links (required for Unsplash attribution)
                    'links': {
                        'html': photo.get('links', {}).get('html', ''),  # Link to photo on Unsplash
                        'download': photo.get('links', {}).get('download', ''),  # Download endpoint
                        'download_location': photo.get('links', {}).get('download_location', ''),  # Track download
                    }
                }
                for i, photo in enumerate(photos)
            ]
            
            # Update cache
            _photo_cache['data'] = photo_data
            _photo_cache['timestamp'] = time.time()
            logger.info(f"Cached {len(photo_data)} photos for {CACHE_DURATION_MINUTES} minutes")
            
            return photo_data
        else:
            logger.error(f"Unsplash API error: {response.status_code} - {response.text}")
            if _photo_cache['data']:
                logger.warning("Returning stale cache due to API error")
                return _photo_cache['data']
            return []
    except requests.exceptions.Timeout:
        logger.error("Unsplash API request timed out")
        if _photo_cache['data']:
            logger.warning("Returning stale cache due to timeout")
            return _photo_cache['data']
        return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Unsplash API request failed: {e}")
        if _photo_cache['data']:
            logger.warning("Returning stale cache due to request error")
            return _photo_cache['data']
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching Unsplash photos: {e}", exc_info=True)
        if _photo_cache['data']:
            logger.warning("Returning stale cache due to unexpected error")
            return _photo_cache['data']
        return []
