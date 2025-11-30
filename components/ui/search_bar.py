"""Search and filter bar component for photo gallery"""

from fasthtml.common import *


def create_search_bar(current_order='popular', search_query=''):
    """Create a centered search bar with ordering selector for the photo gallery

    Args:
        current_order: Currently selected order option
        search_query: Current search query value
    """
    return Form(
        # Search input
        Input(
            type='text',
            name='q',
            id='photo-search',
            value=search_query,
            placeholder='Search photos by title, tags, or location...',
            style="""
                width: 100%;
                max-width: 500px;
                padding: 1rem 1.5rem;
                background: var(--card-bg);
                border: 1px solid var(--border-primary);
                border-radius: 12px;
                color: var(--text-primary);
                font-size: 1rem;
                outline: none;
                transition: all 0.3s ease;
                text-align: center;
            """,
            onfocus="this.style.background='var(--card-hover-bg)'; this.style.borderColor='var(--border-primary)'",
            onblur="this.style.background='var(--card-bg)'; this.style.borderColor='var(--border-primary)'",
        ),
        # Order by selector
        Select(
            Option('Popular', value='popular', selected=(current_order == 'popular')),
            Option('Latest', value='latest', selected=(current_order == 'latest')),
            Option('Oldest', value='oldest', selected=(current_order == 'oldest')),
            name='order',
            id='photo-order',
            style="""
                padding: 1rem 1.5rem;
                background: var(--card-bg);
                border: 1px solid var(--border-primary);
                border-radius: 12px;
                color: var(--text-primary);
                font-size: 1rem;
                cursor: pointer;
                outline: none;
                transition: all 0.3s ease;
                min-width: 140px;
            """,
            onfocus="this.style.background='var(--card-hover-bg)'; this.style.borderColor='var(--border-primary)'",
            onblur="this.style.background='var(--card-bg)'; this.style.borderColor='var(--border-primary)'",
        ),
        # Search button
        Button(
            'Search',
            type='submit',
            style="""
                padding: 1rem 2rem;
                background: var(--card-bg);
                border: 1px solid var(--border-primary);
                border-radius: 12px;
                color: var(--text-primary);
                font-size: 1rem;
                cursor: pointer;
                outline: none;
                transition: all 0.3s ease;
            """,
            onmouseover="this.style.background='var(--card-hover-bg)'",
            onmouseout="this.style.background='var(--card-bg)'",
        ),
        method='get',
        action='/',
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
