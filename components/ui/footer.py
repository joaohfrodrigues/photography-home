"""Footer component"""

from fasthtml.common import *


def create_footer():
    """Create the footer section"""
    return Footer(
        Div(
            P('© 2025 João Rodrigues. All rights reserved.'),
            P(
                A(
                    'Instagram',
                    href='https://instagram.com/joaohfrodrigues',
                    target='_blank',
                    rel='noopener noreferrer',
                ),
                Span(' • ', style='margin: 0 0.5rem;'),
                A(
                    'Unsplash',
                    href='https://unsplash.com/@joaohfrodrigues',
                    target='_blank',
                    rel='noopener noreferrer',
                ),
                Span(' • ', style='margin: 0 0.5rem;'),
                A(
                    'LinkedIn',
                    href='https://www.linkedin.com/in/joaohfrodrigues/',
                    target='_blank',
                    rel='noopener noreferrer',
                ),
            ),
            cls='footer-content',
        ),
        # Loading overlay for async operations
        Div(
            Div(cls='loading-spinner'),
            Span('Loading...', cls='sr-only'),
            cls='loading-overlay',
            id='loading-overlay',
        ),
    )
