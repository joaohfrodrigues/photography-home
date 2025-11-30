"""Gallery filters component"""

from fasthtml.common import *


def create_filters(_photos=None):
    """Create search bar for the gallery"""
    return Div(
        Div(
            # Search only
            Div(
                Input(
                    type='text',
                    id='search-input',
                    placeholder='🔍 Search photos, tags, or locations...',
                    cls='filter-input',
                    oninput='debouncedFilter()',
                ),
                cls='filter-group search-group',
            ),
            cls='filters-container',
        ),
        # Results count
        Div(Span('', id='results-count', cls='results-count'), cls='results-info'),
        cls='filters-wrapper',
    )
