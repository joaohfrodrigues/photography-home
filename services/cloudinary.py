"""Cloudinary image optimization"""
import logging
from cloudinary.utils import cloudinary_url

logger = logging.getLogger(__name__)


def get_optimized_url(public_id, width=1600, height=1200, crop='limit'):
    """Generate optimized Cloudinary URL"""
    # If it's already a full URL (from Unsplash), use Cloudinary fetch
    if public_id.startswith('http'):
        logger.debug(f"Using Cloudinary fetch for external URL: {public_id[:50]}...")
        url, _ = cloudinary_url(
            public_id,
            type='fetch',
            width=width,
            height=height,
            crop=crop,  # 'limit' preserves aspect ratio and doesn't crop
            quality='auto:best',  # Higher quality
            fetch_format='auto'
        )
        return url
    else:
        logger.debug(f"Using Cloudinary asset: {public_id}")
        url, _ = cloudinary_url(
            public_id,
            width=width,
            height=height,
            crop=crop,
            quality='auto:best',
            fetch_format='auto'
        )
        return url
