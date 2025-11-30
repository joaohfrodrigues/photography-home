"""Gallery page component"""

from fasthtml.common import *

from components.ui.footer import create_footer
from components.ui.gallery import create_gallery
from components.ui.head import create_head
from components.ui.header import create_hero, create_navbar
from components.ui.lightbox import create_lightbox


def gallery_page(photos):
    """Render the gallery/home page"""
    return Html(
        create_head(),
        Body(
            create_navbar(current_page='home'),
            create_hero(),
            create_gallery(photos),
            create_footer(),
            create_lightbox(),
        ),
    )
