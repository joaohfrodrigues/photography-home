"""Search and filter bar component for photo gallery"""

from fasthtml.common import *


def create_search_bar():
    """Create a centered search bar for the photo gallery"""
    return Div(
        Input(
            type='text',
            id='photo-search',
            placeholder='Search photos by title, tags, or location...',
            style="""
                width: 100%;
                max-width: 600px;
                padding: 1rem 1.5rem;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                color: #fff;
                font-size: 1rem;
                outline: none;
                transition: all 0.3s ease;
                text-align: center;
            """,
            onkeyup='filterPhotos()',
            onfocus="this.style.background='rgba(255, 255, 255, 0.12)'; this.style.borderColor='rgba(255, 255, 255, 0.25)'",
            onblur="this.style.background='rgba(255, 255, 255, 0.08)'; this.style.borderColor='rgba(255, 255, 255, 0.15)'",
        ),
        cls='search-filter-bar',
        style="""
            display: flex;
            justify-content: center;
            margin-bottom: 3rem;
        """,
    )
