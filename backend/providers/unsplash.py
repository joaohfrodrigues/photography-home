"""Unsplash API provider"""

import logging
from collections.abc import Generator
from typing import Any

from backend.providers.base import validate_photo_structure
from config import ETL_STRICT_VALIDATION, UNSPLASH_FETCH_MODE
from services.unsplash import UnsplashClient

from .base import BaseProvider

logger = logging.getLogger(__name__)


class UnsplashProvider(BaseProvider):
    """Provider for fetching data from the Unsplash API using UnsplashClient.

    Supports a fetch mode controlled by `UNSPLASH_FETCH_MODE` ('batch' or
    'details'). 'batch' yields photos via the client's paginated helper.
    'details' is a test path that fetches a single photo's detailed payload
    using the `/photos/{id}` endpoint.
    """

    def __init__(self, client: UnsplashClient, fetch_mode: str | None = None):
        self.client = client
        self.fetch_mode = fetch_mode or UNSPLASH_FETCH_MODE

    def get_collections(self) -> Generator[dict[str, Any], None, None]:
        """Yield collections for the configured user (uses client's collection endpoint).

        Uses `fetch_user_collections` which returns a list; we yield each item.
        """
        username = getattr(self.client, 'username', None)
        logger.info(f'Fetching collections for user "{username}" from Unsplash')

        try:
            collections = self.client.fetch_user_collections()
            # `fetch_user_collections` returns a list; yield directly.
            yield from collections
        except Exception as e:
            logger.error(f'Error fetching collections: {e}')

    def get_photos_in_collection(self, collection_id: str) -> Generator[dict[str, Any], None, None]:
        """Yield all photos in a collection, paginating via the client's helper."""
        logger.info(f'Fetching photos for collection "{collection_id}" from Unsplash')
        page = 1
        per_page = 30
        while True:
            try:
                photos, has_more = self.client.fetch_collection_photos(
                    collection_id=collection_id, page=page, per_page=per_page
                )
                if not photos:
                    break

                for photo in photos:
                    # Validate provider output shape before yielding
                    if not validate_photo_structure(photo):
                        msg = f"Invalid photo shape from Unsplash provider (missing required keys): {photo.get('id', '<no-id>')}"
                        if ETL_STRICT_VALIDATION:
                            logger.error(msg)
                            raise ValueError(msg)
                        else:
                            logger.warning(msg + ' — skipping')
                            continue
                    yield photo

                if not has_more:
                    break
                page += 1
            except Exception as e:
                logger.error(
                    f'Error fetching photos for collection {collection_id} (page {page}): {e}'
                )
                break

    def get_user_photos(self, username: str) -> Generator[dict[str, Any], None, None]:
        """Yield all photos for a user. The client is expected to be configured
        with a username; this method will use the client's pagination helper.
        """
        logger.info(
            f'Fetching all photos for user "{username}" from Unsplash (mode={self.fetch_mode})'
        )

        # 'details' mode: for testing we fetch a small batch to select one
        # photo id and then request the full `/photos/{id}` payload for that
        # single photo. This lets us validate the photo-details endpoint
        # without pulling lots of pages.
        if self.fetch_mode == 'details':
            logger.info('Using "details" fetch mode — fetching a single detailed photo for testing')
            yield from self._detailed_photo_generator()
            return

        # Default/batch mode: paginate through user photos
        page = 1
        per_page = 30
        while True:
            try:
                photos, has_more = self.client.fetch_latest_user_photos(
                    page=page, per_page=per_page
                )
                if not photos:
                    break

                for photo in photos:
                    # Validate provider output shape before yielding
                    if not validate_photo_structure(photo):
                        msg = f"Invalid photo shape from Unsplash provider (missing required keys): {photo.get('id', '<no-id>')}"
                        if ETL_STRICT_VALIDATION:
                            logger.error(msg)
                            raise ValueError(msg)
                        else:
                            logger.warning(msg + ' — skipping')
                            continue
                    yield photo

                if not has_more:
                    break
                page += 1
            except Exception as e:
                logger.error(f'Error fetching photos for user {username} (page {page}): {e}')
                break

    def _detailed_photo_generator(self) -> Generator[dict[str, Any], None, None]:
        """Internal helper that yields a single detailed photo for testing."""
        try:
            batch = self.client.fetch_photos() or []
            if not batch:
                return
            first = batch[0]
            photo_id = first.get('id')
            if not photo_id:
                return
            details = self.client.fetch_photo_details(photo_id)
            if not details:
                return
            # _transform_photo_data expects a list; try transforming and
            # fall back to raw details if transformation fails.
            try:
                transformed = self.client._transform_photo_data([details])[0]
            except Exception:
                transformed = details
            yield transformed
        except Exception as e:
            logger.error(f'Error fetching detailed photo: {e}')
