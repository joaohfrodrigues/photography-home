"""Base provider for fetching photo data"""

from abc import ABC, abstractmethod
from collections.abc import Generator
from typing import Any


class BaseProvider(ABC):
    """Abstract base class for data providers"""

    @abstractmethod
    def get_collections(self) -> Generator[dict[str, Any], None, None]:
        """Generator that yields collections"""
        pass

    @abstractmethod
    def get_photos_in_collection(self, collection_id: str) -> Generator[dict[str, Any], None, None]:
        """Generator that yields photos from a specific collection"""
        pass

    @abstractmethod
    def get_user_photos(self, username: str) -> Generator[dict[str, Any], None, None]:
        """Generator that yields all photos for a specific user"""
        pass


# Minimal canonical photo shape keys that providers should supply (ETL
# relies on these). Providers may include additional keys but must at least
# provide the required ones.
REQUIRED_PHOTO_KEYS = [
    'id',
    'url_regular',
    'url_raw',
    'title',
    'created_at',
    'updated_at',
]


def validate_photo_structure(photo: dict, required_keys: list[str] | None = None) -> bool:
    """Lightweight runtime validation for provider photo dicts.

    Returns True when the photo contains the minimal required keys. This is
    intentionally permissive (no heavy type checking) so providers can be
    implemented without a third-party schema dependency. Callers should log
    or raise if strict validation is needed.
    """
    if required_keys is None:
        required_keys = REQUIRED_PHOTO_KEYS

    if not isinstance(photo, dict):
        return False

    return all(k in photo for k in required_keys)
