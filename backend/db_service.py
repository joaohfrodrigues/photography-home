"""Database service layer for reading photo data"""

import json
import logging
from typing import Any

from backend.database import get_db_connection

logger = logging.getLogger(__name__)


def _row_to_dict(row) -> dict[str, Any]:
    """Convert SQLite Row to dictionary with proper data types"""
    data = dict(row)

    # Parse JSON fields
    if data.get('tags'):
        try:
            data['tags'] = json.loads(data['tags'])
        except (json.JSONDecodeError, TypeError):
            data['tags'] = []
    else:
        data['tags'] = []

    # Restructure for backward compatibility with existing components
    result = {
        'id': data['id'],
        'url': data['url_regular'],
        'url_raw': data['url_raw'],
        'url_regular': data['url_regular'],
        'url_thumb': data['url_small'],
        'title': data['title'] or 'Untitled',
        'description': data['description'] or '',
        'alt_description': data['alt_description'] or '',
        'views': data['views'] or 0,
        'downloads': data['downloads'] or 0,
        'likes': data['likes'] or 0,
        'width': data['width'] or 1,
        'height': data['height'] or 1,
        'created_at': data['created_at'] or '',
        'updated_at': data['updated_at'] or '',
        'color': data['color'] or '#000000',
        'blur_hash': data['blur_hash'] or '',
        'exif': {
            'make': data['exif_make'],
            'model': data['exif_model'],
            'exposure_time': data['exif_exposure_time'],
            'aperture': data['exif_aperture'],
            'focal_length': data['exif_focal_length'],
            'iso': data['exif_iso'],
        },
        'location': {
            'name': data['location_name'],
            'city': data['location_city'],
            'country': data['location_country'],
        },
        'tags': data['tags'],
        'user': {
            'name': data['photographer_name'] or 'Unknown',
            'username': data['photographer_username'] or '',
            'profile_url': data['photographer_url'] or '',
        },
        'links': {
            'html': data['unsplash_url'] or '',
            'download_location': data['download_location'] or '',
        },
        'statistics': {
            'views': {'total': data['views'] or 0},
            'downloads': {'total': data['downloads'] or 0},
        },
    }

    return result


def get_latest_photos(
    page: int = 1, per_page: int = 30, order_by: str = 'popular'
) -> tuple[list[dict], bool]:
    """
    Get latest photos with pagination and ordering.

    Args:
        page: Page number (1-indexed)
        per_page: Photos per page
        order_by: 'popular' (views), 'latest' (created_at), or 'oldest'

    Returns:
        Tuple of (photos list, has_more boolean)
    """
    offset = (page - 1) * per_page

    # Determine order by clause
    # Build order clause - whitelist to prevent SQL injection
    if order_by == 'latest':
        order_clause = 'created_at DESC'
    elif order_by == 'oldest':
        order_clause = 'created_at ASC'
    else:  # popular
        order_clause = 'views DESC, created_at DESC'

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get photos - order_clause is from whitelisted values only
        cursor.execute(  # nosec B608 - order_clause is from whitelisted values
            f"""
            SELECT * FROM photos
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
        """,
            (per_page + 1, offset),  # Fetch one extra to check if there's more
        )

        rows = cursor.fetchall()

        # Check if there are more results
        has_more = len(rows) > per_page
        photos = [_row_to_dict(row) for row in rows[:per_page]]

        logger.info(
            f'Fetched {len(photos)} photos (page {page}, order: {order_by}, has_more: {has_more})'
        )

        return photos, has_more


def get_collection_photos(
    collection_id: str, page: int = 1, per_page: int = 30
) -> tuple[list[dict], bool]:
    """
    Get photos from a specific collection.

    Returns:
        Tuple of (photos list, has_more boolean)
    """
    offset = (page - 1) * per_page

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT p.* FROM photos p
            JOIN photo_collections pc ON p.id = pc.photo_id
            WHERE pc.collection_id = ?
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """,
            (collection_id, per_page + 1, offset),
        )

        rows = cursor.fetchall()

        has_more = len(rows) > per_page
        photos = [_row_to_dict(row) for row in rows[:per_page]]

        logger.info(
            f'Fetched {len(photos)} photos for collection {collection_id} (page {page}, has_more: {has_more})'
        )

        return photos, has_more


def get_all_collections() -> list[dict]:
    """Get all collections with metadata"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.id,
                c.title,
                c.description,
                c.total_photos,
                c.updated_at,
                c.published_at,
                c.cover_photo_url
            FROM collections c
            ORDER BY c.updated_at DESC
        """)

        rows = cursor.fetchall()

        collections = []
        for row in rows:
            collections.append(
                {
                    'id': row['id'],
                    'title': row['title'],
                    'description': row['description'] or '',
                    'total_photos': row['total_photos'],
                    'updated_at': row['updated_at'],
                    'published_at': row['published_at'],
                    'cover_photo': {'url': row['cover_photo_url']},
                }
            )

        logger.info(f'Fetched {len(collections)} collections')
        return collections


def search_photos(query: str, limit: int = 100) -> list[dict]:
    """
    Search photos using full-text search.

    Args:
        query: Search query
        limit: Maximum results to return

    Returns:
        List of matching photos
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Use FTS5 for search
        cursor.execute(
            """
            SELECT p.* FROM photos p
            JOIN photos_fts fts ON p.rowid = fts.rowid
            WHERE photos_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """,
            (query, limit),
        )

        rows = cursor.fetchall()
        photos = [_row_to_dict(row) for row in rows]

        logger.info(f"Search '{query}' returned {len(photos)} results")
        return photos


def get_photo_by_id(photo_id: str) -> dict | None:
    """Get a single photo by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM photos WHERE id = ?', (photo_id,))
        row = cursor.fetchone()

        if row:
            return _row_to_dict(row)
        return None


def get_database_stats() -> dict:
    """Get database statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Total photos
        cursor.execute('SELECT COUNT(*) FROM photos')
        total_photos = cursor.fetchone()[0]

        # Total collections
        cursor.execute('SELECT COUNT(*) FROM collections')
        total_collections = cursor.fetchone()[0]

        # Total views and downloads
        cursor.execute('SELECT SUM(views), SUM(downloads) FROM photos')
        row = cursor.fetchone()
        total_views = row[0] or 0
        total_downloads = row[1] or 0

        return {
            'total_photos': total_photos,
            'total_collections': total_collections,
            'total_views': total_views,
            'total_downloads': total_downloads,
        }
