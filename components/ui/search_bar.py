"""Search and filter bar component for photo gallery"""

from fasthtml.common import *


def create_search_bar():
    """Create a search and filter bar for the photo gallery"""
    return Div(
        # Search input
        Div(
            Input(
                type='text',
                id='photo-search',
                placeholder='Search photos by title, tags, or location...',
                style="""
                    width: 100%;
                    padding: 1rem 1.5rem;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    font-size: 1rem;
                    outline: none;
                    transition: all 0.3s ease;
                """,
                onkeyup='filterPhotos()',
                onfocus="this.style.background='rgba(255, 255, 255, 0.08)'; this.style.borderColor='rgba(255, 255, 255, 0.2)'",
                onblur="this.style.background='rgba(255, 255, 255, 0.05)'; this.style.borderColor='rgba(255, 255, 255, 0.1)'",
            ),
            style='flex: 1; max-width: 600px;',
        ),
        # Filter buttons
        Div(
            # Year filter
            Select(
                Option('All Years', value='all', selected=True),
                Option('2024', value='2024'),
                Option('2023', value='2023'),
                Option('2022', value='2022'),
                id='year-filter',
                onchange='filterPhotos()',
                style="""
                    padding: 0.75rem 1rem;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    font-size: 0.9rem;
                    cursor: pointer;
                    outline: none;
                    transition: all 0.3s ease;
                """,
                onfocus="this.style.background='rgba(255, 255, 255, 0.08)'",
                onblur="this.style.background='rgba(255, 255, 255, 0.05)'",
            ),
            # Orientation filter
            Select(
                Option('All Orientations', value='all', selected=True),
                Option('Landscape', value='landscape'),
                Option('Portrait', value='portrait'),
                Option('Square', value='square'),
                id='orientation-filter',
                onchange='filterPhotos()',
                style="""
                    padding: 0.75rem 1rem;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: #fff;
                    font-size: 0.9rem;
                    cursor: pointer;
                    outline: none;
                    transition: all 0.3s ease;
                """,
                onfocus="this.style.background='rgba(255, 255, 255, 0.08)'",
                onblur="this.style.background='rgba(255, 255, 255, 0.05)'",
            ),
            # Clear filters button
            Button(
                'Clear Filters',
                id='clear-filters',
                onclick='clearFilters()',
                style="""
                    padding: 0.75rem 1.5rem;
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    border-radius: 8px;
                    color: #fff;
                    font-size: 0.9rem;
                    cursor: pointer;
                    transition: all 0.3s ease;
                """,
                onmouseover="this.style.background='rgba(255, 255, 255, 0.15)'",
                onmouseout="this.style.background='rgba(255, 255, 255, 0.1)'",
            ),
            style='display: flex; gap: 1rem; flex-wrap: wrap;',
        ),
        cls='search-filter-bar',
        style="""
            display: flex;
            gap: 1.5rem;
            align-items: center;
            margin-bottom: 3rem;
            flex-wrap: wrap;
            padding: 1.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        """,
    )
