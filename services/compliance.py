"""Unsplash API compliance utilities"""

import logging

import requests

from config import UNSPLASH_ACCESS_KEY

logger = logging.getLogger(__name__)


def trigger_download(download_location):
    """
    Trigger Unsplash download event (required for API compliance)
    Must be called when a user views/downloads a photo
    """
    if not download_location or not UNSPLASH_ACCESS_KEY:
        logger.warning('Cannot trigger download - missing download_location or API key')
        return False

    try:
        headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
        response = requests.get(download_location, headers=headers, timeout=5)

        if response.status_code == 200:
            logger.info('Successfully triggered download event for photo')
            return True
        else:
            logger.error(f'Failed to trigger download: {response.status_code}')
            return False
    except Exception as e:
        logger.error(f'Error triggering download: {e}')
        return False
