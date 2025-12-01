"""ETL script to sync photos from a provider to local database"""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import (
    get_db_connection,
    init_database,
    insert_collection,
    insert_photo,
    link_photo_to_collection,
)
from backend.providers.base import BaseProvider
from backend.providers.unsplash import UnsplashProvider
from services.unsplash import UnsplashClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def transform_photo(
    photo: dict, fetch_exif: bool = False, provider: BaseProvider | None = None
) -> dict:
    """Transform API photo data to our database schema

    Args:
        photo: Photo data from the provider
        fetch_exif: Whether to fetch full EXIF data (if supported by provider)
        provider: The data provider instance (required if fetch_exif=True)
    """
    # Extract statistics. Providers may either supply a flattened integer
    # `views`/`downloads` at the top-level (our service transforms) or a
    # nested `statistics` object (raw Unsplash API). Prefer flattened
    # top-level values when present to avoid losing popularity data.
    views = photo.get('views')
    downloads = photo.get('downloads')
    if views is None:
        stats = photo.get('statistics', {})
        views = stats.get('views', {}).get('total', 0) if stats else 0
    if downloads is None:
        stats = photo.get('statistics', {})
        downloads = stats.get('downloads', {}).get('total', 0) if stats else 0

    # Provider may return either raw Unsplash API shape (with `urls` dict)
    # or a flattened canonical shape (with `url_regular`, `url_raw`, ...).
    # Prefer flattened keys, then fall back to nested `urls`.
    def _url(field: str) -> str:
        # field is one of: 'raw','full','regular','small','thumb'
        flat = photo.get(f'url_{field}')
        if flat:
            return flat
        urls = photo.get('urls') or {}
        return urls.get(field, '')

    # Fetch complete photo details if EXIF requested and not present
    # This part is provider-specific; for now, we assume Unsplash-like behavior
    if (
        fetch_exif
        and not photo.get('exif', {}).get('make')
        and isinstance(provider, UnsplashProvider)
    ):
        try:
            logger.debug(f'Fetching EXIF for photo {photo["id"]}')
            photo_detail = provider.client.fetch_photo_details(photo['id'])
            if photo_detail:
                photo['exif'] = photo_detail.get('exif', {})
                # Ensure nested urls in detail are flattened if necessary
                if photo_detail.get('urls'):
                    photo.setdefault('url_raw', photo_detail['urls'].get('raw', ''))
                    photo.setdefault('url_full', photo_detail['urls'].get('full', ''))
                    photo.setdefault('url_regular', photo_detail['urls'].get('regular', ''))
                    photo.setdefault('url_small', photo_detail['urls'].get('small', ''))
                    photo.setdefault('url_thumb', photo_detail['urls'].get('thumb', ''))
        except Exception as e:
            logger.warning(f'Failed to fetch EXIF for {photo["id"]}: {e}')

    # Extract location, EXIF, user, and tags
    location = photo.get('location', {}) or {}
    exif = photo.get('exif', {}) or {}
    user = photo.get('user', {}) or {}
    tags = [tag.get('title', '') for tag in photo.get('tags', []) if tag.get('title')]

    transformed = {
        'id': photo['id'],
        'title': photo.get('title')
        or photo.get('alt_description')
        or f'Untitled Photo {photo["id"]}',
        'description': photo.get('description', ''),
        'alt_description': photo.get('alt_description', ''),
        'created_at': photo.get('created_at', ''),
        'updated_at': photo.get('updated_at', ''),
        'width': photo.get('width', 0),
        'height': photo.get('height', 0),
        'color': photo.get('color', '#000000'),
        'blur_hash': photo.get('blur_hash', ''),
        'views': views,
        'downloads': downloads,
        'likes': photo.get('likes', 0),
        'url_raw': photo.get('url_raw') or _url('raw'),
        'url_full': photo.get('url_full') or _url('full'),
        'url_regular': photo.get('url_regular') or _url('regular'),
        'url_small': photo.get('url_small') or _url('small'),
        'url_thumb': photo.get('url_thumb') or _url('thumb'),
        'photographer_name': user.get('name', 'Unknown'),
        'photographer_username': user.get('username', ''),
        'photographer_url': f'https://unsplash.com/@{user.get("username", "")}'
        if user.get('username')
        else '',
        'photographer_avatar': photo.get('photographer_avatar')
        or (user.get('profile_image') or {}).get('large', ''),
        'location_name': location.get('name'),
        'location_city': location.get('city'),
        'location_country': location.get('country'),
        'location_latitude': location.get('position', {}).get('latitude'),
        'location_longitude': location.get('position', {}).get('longitude'),
        'exif_make': exif.get('make'),
        'exif_model': exif.get('model'),
        'exif_exposure_time': exif.get('exposure_time'),
        'exif_aperture': exif.get('aperture'),
        'exif_focal_length': exif.get('focal_length'),
        'exif_iso': str(exif.get('iso')) if exif.get('iso') else None,
        'tags': tags,
        'unsplash_url': photo.get('links', {}).get('html', ''),
        'download_location': photo.get('links', {}).get('download_location', ''),
        'last_synced_at': datetime.now(timezone.utc).isoformat(),
    }

    return transformed


def sync_data(provider: BaseProvider, username: str, max_photos: int | None = None):
    """Main ETL function to sync data from a provider to the database"""
    logger.info('=' * 60)
    logger.info(f'Starting data sync from provider: {type(provider).__name__}')
    logger.info('=' * 60)

    # Initialize database
    init_database()

    total_photos_synced = 0
    total_collections_synced = 0

    with get_db_connection() as conn:
        # Sync all photos from the user profile first
        # These often have more details like statistics
        logger.info(f'\nSyncing all photos for user "{username}"')
        photo_ids = set()
        user_photos_generator = provider.get_user_photos(username)

        # Limit photos if max_photos is set
        user_photos_to_sync = (
            list(user_photos_generator)[:max_photos] if max_photos else list(user_photos_generator)
        )

        for idx, photo in enumerate(user_photos_to_sync):
            try:
                # Fetch EXIF for a few photos for testing
                fetch_exif = idx < 2
                photo_data = transform_photo(photo, fetch_exif=fetch_exif, provider=provider)
                insert_photo(conn, photo_data)
                photo_ids.add(photo['id'])
                total_photos_synced += 1
            except Exception as e:
                logger.error(f'Error syncing user photo {photo.get("id")}: {e}')

        conn.commit()
        logger.info(f'Committed {len(user_photos_to_sync)} user photos')

        # Sync collections and link photos
        logger.info('\nSyncing collections')
        collections_generator = provider.get_collections()
        for collection in collections_generator:
            try:
                # Insert collection metadata
                collection_data = {
                    'id': collection['id'],
                    'title': collection['title'],
                    'description': collection.get('description', ''),
                    'total_photos': collection.get('total_photos', 0),
                    'published_at': collection.get('published_at'),
                    'updated_at': collection.get('updated_at'),
                    'cover_photo_id': (
                        collection.get('cover_photo', {}).get('id')
                        if collection.get('cover_photo')
                        else None
                    ),
                    # Support provider shapes that either include a nested `urls`
                    # dict (original API) or a flattened `cover_photo` with
                    # `url`/`url_raw`/`url_small` keys (our service transforms).
                    'cover_photo_url': (
                        # Prefer flattened `url` if provided by the service
                        (collection.get('cover_photo') or {}).get('url')
                        or (collection.get('cover_photo') or {}).get('url_regular')
                        or (collection.get('cover_photo') or {}).get('url_raw')
                        # Fallback to nested `urls.regular` from raw API fixture
                        or (collection.get('cover_photo', {}).get('urls', {}) or {}).get('regular')
                    ),
                    'last_synced_at': datetime.now(timezone.utc).isoformat(),
                }
                insert_collection(conn, collection_data)
                total_collections_synced += 1

                # Link photos to the collection
                logger.info(f'Linking photos for collection: {collection["title"]}')
                collection_photos_generator = provider.get_photos_in_collection(collection['id'])

                photos_in_collection_to_sync = (
                    list(collection_photos_generator)[:max_photos]
                    if max_photos
                    else list(collection_photos_generator)
                )

                for photo in photos_in_collection_to_sync:
                    # If photo hasn't been synced yet, sync it now
                    if photo['id'] not in photo_ids:
                        try:
                            photo_data = transform_photo(photo, provider=provider)
                            insert_photo(conn, photo_data)
                            photo_ids.add(photo['id'])
                            total_photos_synced += 1
                        except Exception as e:
                            logger.error(f'Error syncing collection photo {photo.get("id")}: {e}')

                    # Link photo to collection
                    link_photo_to_collection(
                        conn,
                        photo['id'],
                        collection['id'],
                        photo.get('created_at', datetime.now(timezone.utc).isoformat()),
                    )
                conn.commit()
                logger.info(
                    f'Committed {total_collections_synced} collections and linked {len(photos_in_collection_to_sync)} photos'
                )
            except Exception as e:
                logger.error(f'Error syncing collection {collection.get("id")}: {e}')
                conn.rollback()

    logger.info('=' * 60)
    logger.info('Sync completed!')
    logger.info(f'Collections synced: {total_collections_synced}')
    logger.info(f'Total unique photos processed: {total_photos_synced}')
    logger.info('=' * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Sync photos from a provider to local database')
    parser.add_argument(
        '--max-photos',
        type=int,
        default=None,
        help='Maximum photos per user/collection (for testing, default: all)',
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: sync only 5 photos per user/collection',
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    access_key = os.getenv('UNSPLASH_ACCESS_KEY')
    username = os.getenv('UNSPLASH_USERNAME', 'joaohfrodrigues')

    if not access_key:
        logger.error('UNSPLASH_ACCESS_KEY not found in environment')
        sys.exit(1)

    # Initialize the provider
    unsplash_client = UnsplashClient(access_key, username)
    provider = UnsplashProvider(unsplash_client)

    max_photos = 5 if args.test else args.max_photos

    try:
        sync_data(provider, username, max_photos)
    except Exception as e:
        logger.error(f'Sync failed: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
