"""API routes for photo operations"""

import logging

from fasthtml.common import *

from services import (
    fetch_collection_photos,
    fetch_latest_user_photos,
    fetch_photo_details,
    trigger_download,
)

logger = logging.getLogger(__name__)


def register_api_routes(rt):
    """Register all API routes"""

    @rt('/api/latest-photos')
    def get(order: str = 'popular', page: int = 1):
        """API endpoint to fetch latest user photos with ordering"""
        logger.info(f'Fetching latest photos (order: {order}, page: {page})')
        per_page = 30  # Load 30 photos per page for better efficiency
        photos, has_more = fetch_latest_user_photos(page=page, per_page=per_page, order_by=order)

        if photos is None:
            logger.error('Failed to fetch latest photos')
            return {'error': 'Failed to fetch photos'}, 500

        logger.info(f'Returning {len(photos)} photos, has_more={has_more}')
        return {'photos': photos, 'has_more': has_more}

    @rt('/api/trigger-download')
    def get(photo_id: str = '', download_location: str = ''):
        """API endpoint to trigger Unsplash download event"""
        logger.info(f'Download triggered for photo: {photo_id}')
        success = trigger_download(download_location)
        return {'success': success, 'photo_id': photo_id}

    @rt('/api/photo-details/{photo_id}')
    def get(photo_id: str):
        """API endpoint to fetch detailed photo information including EXIF"""
        logger.info(f'Fetching details for photo: {photo_id}')
        details = fetch_photo_details(photo_id)
        if details:
            return details
        else:
            return {'error': 'Failed to fetch photo details'}, 500

    @rt('/api/collection/{collection_id}/photos')
    def get(collection_id: str, page: int = 1):
        """API endpoint to fetch photos from a collection (for infinite scroll)"""
        logger.info(f'Fetching photos for collection {collection_id}, page {page}')
        per_page = 30
        photos, has_more = fetch_collection_photos(collection_id, page=page, per_page=per_page)

        if photos is None:
            logger.error(f'Failed to fetch photos for collection {collection_id}')
            return {'error': 'Failed to fetch photos'}, 500

        logger.info(f'Returning {len(photos)} photos, has_more={has_more}')
        return {'photos': photos, 'has_more': has_more}
