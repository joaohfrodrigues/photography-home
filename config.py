"""Configuration and environment setup"""
import os
import logging
from dotenv import load_dotenv
from cloudinary import config as cloudinary_config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

cloudinary_config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET
)

# Unsplash configuration
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')
UNSPLASH_USERNAME = os.getenv('UNSPLASH_USERNAME', 'joaohfrodrigues')
CACHE_DURATION_MINUTES = int(os.getenv('CACHE_DURATION_MINUTES', '30'))

# EXIF loading strategy
EXIF_LAZY_LOADING = os.getenv('EXIF_LAZY_LOADING', 'false').lower() == 'true'

# Log configuration status
logger.info(f"Cloudinary configured: {bool(CLOUDINARY_CLOUD_NAME)}")
logger.info(f"Unsplash configured: {bool(UNSPLASH_ACCESS_KEY)}")
logger.info(f"Unsplash username: {UNSPLASH_USERNAME}")
logger.info(f"Cache duration: {CACHE_DURATION_MINUTES} minutes")
logger.info(f"EXIF lazy loading: {EXIF_LAZY_LOADING}")
