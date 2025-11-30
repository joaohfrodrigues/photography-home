"""Configuration and environment setup"""

import logging
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Unsplash configuration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
UNSPLASH_USERNAME = os.getenv('UNSPLASH_USERNAME', 'joaohfrodrigues')
CACHE_DURATION_MINUTES = int(os.getenv('CACHE_DURATION_MINUTES', '30'))

# EXIF loading strategy
EXIF_LAZY_LOADING = os.getenv('EXIF_LAZY_LOADING', 'false').lower() == 'true'

# Log configuration status
logger.info(f'Unsplash configured: {bool(UNSPLASH_ACCESS_KEY)}')
logger.info(f'Unsplash username: {UNSPLASH_USERNAME}')
logger.info(f'Cache duration: {CACHE_DURATION_MINUTES} minutes')
logger.info(f'EXIF lazy loading: {EXIF_LAZY_LOADING}')
