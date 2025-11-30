"""Photo grid component with masonry layout"""

from fasthtml.common import *

from .photo_card import create_photo_container


def create_photo_grid(photos, show_search=True):
    """Create a masonry photo grid with optional search bar"""
    return create_photo_container(
        photos,
        layout='grid',
        title=None,
        show_filters=False,
        show_search=show_search,
        show_count=True,
    )
