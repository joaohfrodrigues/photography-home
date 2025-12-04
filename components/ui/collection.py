"""Collection gallery component"""

from fasthtml.common import *

from .photo_card import create_photo_container


def create_collection(photos):
    """Create the collection gallery section with photo grid"""
    return create_photo_container(
        photos,
        title='PORTFOLIO',
        show_filters=True,
        show_search=False,
        show_count=False,
    )
