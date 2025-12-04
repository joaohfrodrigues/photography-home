"""Photo grid component with masonry layout"""

from fasthtml.common import *

from .photo_card import create_photo_container


def create_photo_grid(photos, show_search=True, current_order='popular', search_query=''):
    """Create a masonry photo grid with optional search bar

    Args:
        photos: List of photo dicts
        show_search: Whether to show search bar
        current_order: Current sort order
        search_query: Current search query
    """
    return create_photo_container(
        photos,
        title=None,
        show_filters=False,
        show_search=show_search,
        show_count=True,
        current_order=current_order,
        search_query=search_query,
    )
