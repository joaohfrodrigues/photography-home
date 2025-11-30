"""Search and filter bar component for photo gallery"""

from fasthtml.common import *


def create_search_bar():
    """Create a centered search bar with ordering selector for the photo gallery"""
    return Div(
        # Search input
        Input(
            type='text',
            id='photo-search',
            placeholder='Search photos by title, tags, or location...',
            style="""
                width: 100%;
                max-width: 500px;
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
        # Order by selector
        Select(
            Option('Popular', value='popular', selected=True),
            Option('Latest', value='latest'),
            Option('Oldest', value='oldest'),
            id='photo-order',
            onchange='changePhotoOrder()',
            style="""
                padding: 1rem 1.5rem;
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 12px;
                color: #fff;
                font-size: 1rem;
                cursor: pointer;
                outline: none;
                transition: all 0.3s ease;
                min-width: 140px;
            """,
            onfocus="this.style.background='rgba(255, 255, 255, 0.12)'; this.style.borderColor='rgba(255, 255, 255, 0.25)'",
            onblur="this.style.background='rgba(255, 255, 255, 0.08)'; this.style.borderColor='rgba(255, 255, 255, 0.15)'",
        ),
        cls='search-filter-bar',
        style="""
            display: flex;
            gap: 1rem;
            justify-content: center;
            align-items: center;
            margin-bottom: 3rem;
            flex-wrap: wrap;
        """,
    )
