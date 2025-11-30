"""API routes for photo operations"""

import logging

from fasthtml.common import *

from backend.db_service import get_photo_by_id
from services import trigger_download

logger = logging.getLogger(__name__)


def register_api_routes(rt):
    """Register all API routes

    Note: Photo listing endpoints removed - use server-side pagination instead:
    - GET / with ?q=search&order=popular&page=1
    - GET /collection/{id} with ?q=search&page=1
    """

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
