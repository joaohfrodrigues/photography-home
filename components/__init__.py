"""Components package - UI components for the photography portfolio"""

# Import from new modular structure
from .pages.about import about_page

# Page components
from .pages.gallery import gallery_page
from .ui.filters import create_filters
from .ui.footer import create_footer
from .ui.gallery import create_gallery
from .ui.head import create_head
from .ui.header import create_header, create_hero
from .ui.lightbox import create_lightbox

__all__ = [
    'create_head',
    'create_header',
    'create_hero',
    'create_footer',
    'create_gallery',
    'create_lightbox',
    'create_filters',
    'gallery_page',
    'about_page',
]
