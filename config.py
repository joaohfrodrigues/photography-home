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

# Which fetch mode to use for Unsplash photo retrieval.
# 'batch' returns up to 30 photos in a single call; 'details' will (for
# testing) request detailed info for a single photo via `/photos/{id}`.
UNSPLASH_FETCH_MODE = os.getenv('UNSPLASH_FETCH_MODE', 'batch')

# When true, provider validation failures raise an exception during ETL runs.
# Defaults to false so development runs log and skip invalid items.
ETL_STRICT_VALIDATION = os.getenv('ETL_STRICT_VALIDATION', 'false').lower() in ('1', 'true', 'yes')

# Collection badges configuration
# Add collection IDs here to mark them as "Editor's Pick"
# To find collection IDs, check: http://localhost:5001/collections or run:
#   sqlite3 data/photos.db "SELECT id, title FROM collections;"
FEATURED_COLLECTION_IDS = [
    # Example: 'GRVDIk0USf4',  # 25' Valencia
    # Example: 'py2j-CBPSoM',  # 24' Gerês
]

# Log configuration status
logger.info(f'Unsplash configured: {bool(UNSPLASH_ACCESS_KEY)}')
logger.info(f'Unsplash username: {UNSPLASH_USERNAME}')
logger.info(f'Cache duration: {CACHE_DURATION_MINUTES} minutes')
logger.info(f'Unsplash fetch mode: {UNSPLASH_FETCH_MODE}')
logger.info(f'ETL strict validation: {ETL_STRICT_VALIDATION}')
