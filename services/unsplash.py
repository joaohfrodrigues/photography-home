"""Unsplash API integration and caching.

Provides an `UnsplashClient` class that encapsulates Unsplash API calls,
in-memory caching, and error handling. Module-level wrapper functions call a
default client for backward compatibility.
"""

import logging

import requests

logger = logging.getLogger(__name__)


class UnsplashClient:
    """Client that encapsulates Unsplash API calls and simple in-memory caching.

    Args:
        access_key: Unsplash API access key (Client ID). If falsy, API calls are
            skipped and fallback data is returned where applicable.
        username: Unsplash username to fetch user-specific endpoints.
        fetch_mode: 'batch' (default) or 'details' - controls whether to fetch
            full photo details (EXIF, location) for each photo.
    """

    def __init__(self, access_key: str = None, username: str = None, fetch_mode: str = 'batch'):
        self.access_key = access_key
        self.username = username
        self.fetch_mode = fetch_mode
        self.base_url = 'https://api.unsplash.com'
        self.headers = {'Authorization': f'Client-ID {self.access_key}'} if self.access_key else {}

        # This client is intentionally stateless for simplicity. The ETL runs
        # once per day and downstream systems should be responsible for any
        # caching or rate-limiting concerns. Keeping the client stateless
        # avoids cross-run state and keeps provider implementations simple.

    def _get_fallback_photos(self) -> list[dict]:
        logger.warning('No Unsplash API key configured. Using placeholder images.')
        return [
            {
                'url': f'https://picsum.photos/800/600?random={i}',
                'title': f'Sample {i + 1}',
                'description': '',
            }
            for i in range(6)
        ]

    def _transform_photo_data(self, photos: list[dict]) -> list[dict]:
        """Transform photo data from API response to our canonical format.

        Note: This does NOT fetch additional details - use enrich_photo_with_details
        for that. This keeps listing fast and allows ETL to decide what to enrich.
        """
        photo_data = []
        for photo in photos:
            statistics = photo.get('statistics', {})
            views = statistics.get('views', {}).get('total', 0) if statistics else 0
            downloads = statistics.get('downloads', {}).get('total', 0) if statistics else 0

            photo_data.append(
                {
                    'id': photo['id'],
                    'url': photo.get('urls', {}).get('full', ''),
                    'url_full': photo.get('urls', {}).get('full', ''),
                    'url_raw': photo.get('urls', {}).get('raw', ''),
                    'url_regular': photo.get('urls', {}).get('regular', ''),
                    'url_small': photo.get('urls', {}).get('small', ''),
                    'url_thumb': photo.get('urls', {}).get('thumb', ''),
                    'title': photo.get('alt_description') or 'Untitled',
                    'description': photo.get('description', ''),
                    'alt_description': photo.get('alt_description', ''),
                    'views': views,
                    'downloads': downloads,
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
                        # Preserve nested position object (latitude/longitude)
                        'position': photo.get('location', {}).get('position')
                        if photo.get('location')
                        else None,
                    },
                    'tags': [tag.get('title', '') for tag in photo.get('tags', [])],
                    'user': {
                        'name': photo.get('user', {}).get('name', 'Unknown'),
                        'username': photo.get('user', {}).get('username', ''),
                        'portfolio_url': photo.get('user', {}).get('portfolio_url', ''),
                        'profile_url': (
                            f"https://unsplash.com/@{photo.get('user', {}).get('username', '')}"
                            if photo.get('user', {}).get('username')
                            else ''
                        ),
                    },
                    'links': {
                        'html': photo.get('links', {}).get('html', ''),
                        'download': photo.get('links', {}).get('download', ''),
                        'download_location': photo.get('links', {}).get('download_location', ''),
                    },
                }
            )
        return photo_data

    def enrich_photo_with_details(self, photo: dict) -> dict:
        """Fetch and merge full photo details (EXIF, location) into a photo dict.

        Call this explicitly for photos that need detailed metadata. Returns the
        enriched photo dict (modifies in-place and returns for convenience).

        Args:
            photo: Photo dict from listing APIs (must have 'id' key)

        Returns:
            The same photo dict, enriched with EXIF and location if available
        """
        if not photo.get('exif', {}).get('make'):  # Only fetch if EXIF not already present
            try:
                photo_id = photo.get('id')
                if photo_id:
                    logger.info(f'Enriching photo {photo_id} with detailed metadata')
                    details = self.fetch_photo_details(photo_id)
                    if details:
                        # Merge details into photo (prefer detail values)
                        photo.update(
                            {
                                'exif': details.get('exif', {}),
                                'location': details.get('location') or photo.get('location'),
                            }
                        )
            except Exception as e:
                logger.warning(f'Failed to enrich photo {photo.get("id")} with details: {e}')
        return photo

    # ----- Public methods -----
    def fetch_photos(self) -> list[dict]:
        """Fetch photos from the configured user's account (stateless).

        Returns a transformed list of photos. If no access key is configured,
        returns fallback placeholder images.
        """
        if not self.access_key or not self.username:
            return self._get_fallback_photos()

        try:
            logger.info(f'Fetching photos for Unsplash user: {self.username}')
            response = requests.get(
                f'{self.base_url}/users/{self.username}/photos',
                headers=self.headers,
                params={'per_page': 30, 'order_by': 'latest', 'stats': 'true'},
                timeout=10,
            )
            response.raise_for_status()
            photos = response.json()
            logger.info(f'Successfully fetched {len(photos)} photos from Unsplash')
            return self._transform_photo_data(photos)
        except (requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
            error_type = 'timed out' if isinstance(e, requests.exceptions.Timeout) else 'failed'
            logger.error(f'Unsplash API request {error_type}: {e}')
        except Exception as e:
            logger.error(f'Unexpected error fetching Unsplash photos: {e}', exc_info=True)
        return []

    def fetch_user_collections(self) -> list[dict]:
        """Fetch all collections for the configured user (stateless)."""
        if not self.access_key or not self.username:
            logger.warning('No Unsplash API key - cannot fetch collections')
            return []

        logger.info(f'Fetching collections for user: {self.username}')
        try:
            response = requests.get(
                f'{self.base_url}/users/{self.username}/collections',
                headers=self.headers,
                timeout=10,
            )
            response.raise_for_status()
            collections = response.json()
            collection_data = [
                {
                    'id': c['id'],
                    'title': c['title'],
                    'description': c.get('description', ''),
                    'total_photos': c.get('total_photos', 0),
                    'cover_photo': {
                        'url': c.get('cover_photo', {}).get('urls', {}).get('regular', ''),
                        'url_raw': c.get('cover_photo', {}).get('urls', {}).get('raw', ''),
                        'url_small': c.get('cover_photo', {}).get('urls', {}).get('small', ''),
                        'color': c.get('cover_photo', {}).get('color', '#ccc'),
                    },
                    'published_at': c.get('published_at', ''),
                    'updated_at': c.get('updated_at', ''),
                    'featured': i < 2,
                }
                for i, c in enumerate(collections)
            ]
            return collection_data
        except Exception as e:
            logger.error(f'Error fetching collections: {e}', exc_info=True)
            return []

    def fetch_latest_user_photos(
        self, page: int = 1, per_page: int = 30, order_by: str = 'popular'
    ) -> tuple[list[dict], bool]:
        """Fetch a single page of user photos and return (photos, has_more)."""
        if not self.access_key or not self.username:
            logger.warning('No Unsplash API key - cannot fetch latest photos')
            return [], False

        logger.info(f'Fetching user photos (order: {order_by}), page {page}')
        try:
            response = requests.get(
                f'{self.base_url}/users/{self.username}/photos',
                headers=self.headers,
                params={'page': page, 'per_page': per_page, 'order_by': order_by, 'stats': 'true'},
                timeout=10,
            )
            response.raise_for_status()
            photos = response.json()
            photo_data = self._transform_photo_data(photos)
            link_header = response.headers.get('Link', '')
            has_more = 'rel="next"' in link_header
            if not link_header:
                has_more = len(photos) == per_page
            return photo_data, has_more
        except Exception as e:
            logger.error(f'Error fetching latest photos: {e}', exc_info=True)
            return [], False

    def fetch_collection_photos(
        self, collection_id: str, page: int = 1, per_page: int = 30
    ) -> tuple[list[dict], bool]:
        """Fetch a single page of photos from a collection and return (photos, has_more)."""
        if not self.access_key:
            logger.warning('No Unsplash API key - cannot fetch collection photos')
            return [], False

        logger.info(f'Fetching collection {collection_id}, page {page}')
        try:
            response = requests.get(
                f'{self.base_url}/collections/{collection_id}/photos',
                headers=self.headers,
                params={'page': page, 'per_page': per_page, 'order_by': 'latest'},
                timeout=10,
            )
            response.raise_for_status()
            photos = response.json()
            photo_data = self._transform_photo_data(photos)
            link_header = response.headers.get('Link', '')
            has_more = 'rel="next"' in link_header
            if not link_header:
                has_more = len(photos) == per_page
            return photo_data, has_more
        except Exception as e:
            logger.error(f'Error fetching collection photos: {e}', exc_info=True)
            return [], False

    def fetch_photo_details(self, photo_id: str) -> dict:
        if not self.access_key:
            logger.warning('No Unsplash API key - cannot fetch photo details')
            return {}

        logger.info(f'Fetching details for photo {photo_id} from Unsplash API')
        url = f'{self.base_url}/photos/{photo_id}'
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'Error fetching photo details: {e}', exc_info=True)
            return {}
