"""API routes for photo operations"""

import logging

from fasthtml.common import *

from backend.db_service import get_collection_photos, get_latest_photos, get_photo_by_id
from services import trigger_download

logger = logging.getLogger(__name__)


def register_api_routes(rt):
    """Register all API routes"""

    @rt('/api/latest-photos')
    def get(order: str = 'popular', page: int = 1):
        """API endpoint to fetch latest user photos with ordering"""
        logger.info(f'Fetching latest photos from DB (order: {order}, page: {page})')
        per_page = 30  # Load 30 photos per page for better efficiency
        photos, has_more = get_latest_photos(page=page, per_page=per_page, order_by=order)

        logger.info(f'Returning {len(photos)} photos from DB, has_more={has_more}')
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
        logger.info(f'Fetching details for photo from DB: {photo_id}')
        details = get_photo_by_id(photo_id)
        if details:
            return details
        else:
            return {'error': 'Photo not found'}, 404

    @rt('/api/collection/{collection_id}/photos')
    def get(collection_id: str, page: int = 1):
        """API endpoint to fetch photos from a collection (for infinite scroll)"""
        logger.info(f'Fetching photos for collection from DB: {collection_id}, page {page}')
        per_page = 30
        photos, has_more = get_collection_photos(collection_id, page=page, per_page=per_page)

        logger.info(f'Returning {len(photos)} photos from DB, has_more={has_more}')
        return {'photos': photos, 'has_more': has_more}
