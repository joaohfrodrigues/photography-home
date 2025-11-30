"""Main gallery page component - displays all photos"""

from fasthtml.common import *

from components.ui.collection import create_collection
from components.ui.footer import create_footer
from components.ui.head import create_head
from components.ui.header import create_hero, create_navbar
from components.ui.lightbox import create_lightbox


def gallery_page(photos):
    """Render the main gallery page with all photos"""
    return Html(
        create_head(),
        Body(
            create_navbar(current_page='home'),
            create_hero(),
            create_collection(photos),
            create_footer(),
            create_lightbox(),
        ),
    )
