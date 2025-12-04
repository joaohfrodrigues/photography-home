"""Components package - UI components for the photography portfolio"""

# Import from new modular structure
from .pages.about import about_page

# UI components
from .ui.filters import create_filters
from .ui.footer import create_footer
from .ui.head import create_head
from .ui.header import create_header, create_hero
from .ui.lightbox import create_lightbox
from .ui.photo_card import create_photo_container

__all__ = [
    'create_head',
    'create_header',
    'create_hero',
    'create_footer',
    'create_lightbox',
    'create_filters',
    'create_photo_container',
    'about_page',
]
