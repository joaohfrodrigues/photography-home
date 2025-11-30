"""Fetch detailed photo information including EXIF on-demand"""

import logging

import requests

from config import UNSPLASH_ACCESS_KEY

logger = logging.getLogger(__name__)

# Cache for photo details
_details_cache = {}


def fetch_photo_details(photo_id):
    """Fetch detailed photo information including EXIF data"""
    if not UNSPLASH_ACCESS_KEY or not photo_id:
        logger.warning('Cannot fetch photo details - missing API key or photo ID')
        return None

    # Check cache first
    if photo_id in _details_cache:
        logger.debug(f'Using cached details for photo {photo_id}')
        return _details_cache[photo_id]

    try:
        logger.info(f'Fetching detailed info for photo: {photo_id}')
        headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}

        response = requests.get(
            f'https://api.unsplash.com/photos/{photo_id}', headers=headers, timeout=5
        )

        if response.status_code == 200:
            photo = response.json()

            # Extract EXIF data
            exif_data = {
                'make': photo.get('exif', {}).get('make', 'Unknown'),
                'model': photo.get('exif', {}).get('model', 'Unknown'),
                'exposure_time': photo.get('exif', {}).get('exposure_time', 'N/A'),
                'aperture': photo.get('exif', {}).get('aperture', 'N/A'),
                'focal_length': photo.get('exif', {}).get('focal_length', 'N/A'),
                'iso': photo.get('exif', {}).get('iso', 'N/A'),
            }

            logger.info(
                f"Successfully fetched EXIF for {photo_id}: {exif_data.get('make')} {exif_data.get('model')}"
            )

            # Cache the result
            _details_cache[photo_id] = exif_data

            return exif_data
        else:
            logger.error(f'Failed to fetch photo details: {response.status_code}')
            return None

    except Exception as e:
        logger.error(f'Error fetching photo details: {e}')
        return None
