"""ETL script to sync photos from Unsplash to local database"""

import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def get_unsplash_headers(access_key: str) -> dict:
    """Get headers for Unsplash API requests"""
    return {
        'Authorization': f'Client-ID {access_key}',
        'Accept-Version': 'v1',
    }


def fetch_user_collections(access_key: str, username: str) -> list[dict]:
    """Fetch all collections for a user"""
    logger.info(f'Fetching collections for user: {username}')

    headers = get_unsplash_headers(access_key)
    collections = []
    page = 1

    while True:
        url = f'https://api.unsplash.com/users/{username}/collections'
        params = {'page': page, 'per_page': 30}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if not data:
            break

        collections.extend(data)
        logger.info(f'Fetched {len(data)} collections (page {page})')
        page += 1

    logger.info(f'Total collections fetched: {len(collections)}')
    return collections


def fetch_collection_photos(
    access_key: str, collection_id: str, max_photos: int | None = None
) -> list[dict]:
    """Fetch all photos from a collection"""
    logger.info(f'Fetching photos for collection: {collection_id}')

    headers = get_unsplash_headers(access_key)
    photos = []
    page = 1

    while True:
        if max_photos and len(photos) >= max_photos:
            photos = photos[:max_photos]
            break

        url = f'https://api.unsplash.com/collections/{collection_id}/photos'
        params = {'page': page, 'per_page': 30}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if not data:
            break

        photos.extend(data)
        logger.info(f'Fetched {len(data)} photos from collection (page {page})')
        page += 1

    logger.info(f'Total photos fetched for collection {collection_id}: {len(photos)}')
    return photos


def fetch_user_photos(access_key: str, username: str, max_photos: int | None = None) -> list[dict]:
    """Fetch user's photos (not in collections)"""
    logger.info(f'Fetching user photos for: {username}')

    headers = get_unsplash_headers(access_key)
    photos = []
    page = 1

    while True:
        if max_photos and len(photos) >= max_photos:
            photos = photos[:max_photos]
            break

        url = f'https://api.unsplash.com/users/{username}/photos'
        params = {'page': page, 'per_page': 30, 'stats': 'true'}

        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        if not data:
            break

        photos.extend(data)
        logger.info(f'Fetched {len(data)} user photos (page {page})')
        page += 1

    logger.info(f'Total user photos fetched: {len(photos)}')
    return photos


def transform_photo(photo: dict, fetch_exif: bool = False, access_key: str | None = None) -> dict:
    """Transform Unsplash API photo data to our database schema

    Args:
        photo: Photo data from Unsplash API
        fetch_exif: Whether to fetch full EXIF data via individual photo endpoint
        access_key: Unsplash API key (required if fetch_exif=True)
    """
    # Extract statistics
    stats = photo.get('statistics', {})
    views = stats.get('views', {}).get('total', 0) if stats else 0
    downloads = stats.get('downloads', {}).get('total', 0) if stats else 0

    # Fetch complete photo details if EXIF requested and not present
    if fetch_exif and not photo.get('exif', {}).get('make') and access_key:
        try:
            logger.debug(f'Fetching EXIF for photo {photo["id"]}')
            headers = get_unsplash_headers(access_key)
            response = requests.get(
                f'https://api.unsplash.com/photos/{photo["id"]}', headers=headers, timeout=10
            )
            if response.ok:
                photo_detail = response.json()
                # Merge EXIF data
                photo['exif'] = photo_detail.get('exif', {})
        except Exception as e:
            logger.warning(f'Failed to fetch EXIF for {photo["id"]}: {e}')

    # Extract location
    location = photo.get('location', {}) or {}

    # Extract EXIF
    exif = photo.get('exif', {}) or {}

    # Extract user info
    user = photo.get('user', {}) or {}

    # Extract tags
    tags = [tag.get('title', '') for tag in photo.get('tags', []) if tag.get('title')]

    transformed = {
        'id': photo['id'],
        'title': photo.get('description')
        or photo.get('alt_description')
        or f'Photo by {user.get("name", "Unknown")}',
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
        'url_raw': photo.get('urls', {}).get('raw', ''),
        'url_full': photo.get('urls', {}).get('full', ''),
        'url_regular': photo.get('urls', {}).get('regular', ''),
        'url_small': photo.get('urls', {}).get('small', ''),
        'url_thumb': photo.get('urls', {}).get('thumb', ''),
        'photographer_name': user.get('name', 'Unknown'),
        'photographer_username': user.get('username', ''),
        'photographer_url': f'https://unsplash.com/@{user.get("username", "")}'
        if user.get('username')
        else '',
        'photographer_avatar': user.get('profile_image', {}).get('large', ''),
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


def sync_photos(access_key: str, username: str, max_photos: int | None = None):
    """Main ETL function to sync photos from Unsplash to database"""
    logger.info('=' * 60)
    logger.info('Starting photo sync from Unsplash')
    logger.info('=' * 60)

    # Initialize database
    init_database()

    # Fetch collections
    collections = fetch_user_collections(access_key, username)

    total_photos_synced = 0
    total_collections_synced = 0

    with get_db_connection() as conn:
        # First, sync user photos with statistics and selective EXIF
        logger.info('\nSyncing user photos with statistics')
        user_photos = fetch_user_photos(access_key, username, max_photos)

        # Create a set of photo IDs for quick lookup
        photo_ids = set()

        for idx, photo in enumerate(user_photos):
            try:
                # Fetch EXIF for featured photos (first 2 for testing)
                fetch_exif = idx < 2
                photo_data = transform_photo(photo, fetch_exif=fetch_exif, access_key=access_key)
                insert_photo(conn, photo_data)
                photo_ids.add(photo['id'])
                total_photos_synced += 1
            except Exception as e:
                logger.error(f'Error syncing user photo {photo.get("id")}: {e}')

        conn.commit()
        logger.info(f'Committed {len(user_photos)} user photos (with statistics)')

        # Then sync collections and link existing photos
        for collection in collections:
            # Insert collection metadata
            collection_data = {
                'id': collection['id'],
                'title': collection['title'],
                'description': collection.get('description', ''),
                'total_photos': collection.get('total_photos', 0),
                'published_at': collection.get('published_at'),
                'updated_at': collection.get('updated_at'),
                'cover_photo_id': collection.get('cover_photo', {}).get('id')
                if collection.get('cover_photo')
                else None,
                'cover_photo_url': collection.get('cover_photo', {}).get('urls', {}).get('regular')
                if collection.get('cover_photo')
                else None,
                'last_synced_at': datetime.now(timezone.utc).isoformat(),
            }
            insert_collection(conn, collection_data)
            total_collections_synced += 1

            logger.info(f'\nLinking photos to collection: {collection["title"]}')

            # Fetch collection photos only to get photo IDs and link them
            photos = fetch_collection_photos(access_key, collection['id'], max_photos)

            for photo in photos:
                try:
                    # Link photo to collection
                    link_photo_to_collection(
                        conn,
                        photo['id'],
                        collection['id'],
                        photo.get('created_at', datetime.now(timezone.utc).isoformat()),
                    )
                except Exception as e:
                    logger.error(f'Error linking photo {photo.get("id")} to collection: {e}')

            conn.commit()
            logger.info(f'Linked {len(photos)} photos to collection {collection["title"]}')

        # Sync user photos (has statistics!)
        logger.info('\nSyncing user photos with statistics')
        user_photos = fetch_user_photos(access_key, username, max_photos)

        for idx, photo in enumerate(user_photos):
            try:
                # Fetch EXIF for featured photos (first 2 for testing)
                fetch_exif = idx < 2
                photo_data = transform_photo(photo, fetch_exif=fetch_exif, access_key=access_key)
                insert_photo(conn, photo_data)
                total_photos_synced += 1
            except Exception as e:
                logger.error(f'Error syncing user photo {photo.get("id")}: {e}')

        conn.commit()
        logger.info(f'Committed {len(user_photos)} user photos (with statistics)')

    logger.info('=' * 60)
    logger.info('Sync completed!')
    logger.info(f'Collections synced: {total_collections_synced}')
    logger.info(f'Photos processed: {total_photos_synced}')
    logger.info('=' * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Sync photos from Unsplash to local database')
    parser.add_argument(
        '--max-photos',
        type=int,
        default=None,
        help='Maximum photos per collection (for testing, default: all)',
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode: sync only 5 photos per collection',
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    access_key = os.getenv('UNSPLASH_ACCESS_KEY')
    username = os.getenv('UNSPLASH_USERNAME', 'joaohfrodrigues')

    if not access_key:
        logger.error('UNSPLASH_ACCESS_KEY not found in environment')
        sys.exit(1)

    max_photos = 5 if args.test else args.max_photos

    try:
        sync_photos(access_key, username, max_photos)
    except requests.exceptions.RequestException as e:
        logger.error(f'API request failed: {e}')
        sys.exit(1)
    except Exception as e:
        logger.error(f'Sync failed: {e}', exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
