"""Footer component with Vercel Web Analytics"""

from fasthtml.common import *

from components.ui.analytics import create_analytics


def create_footer():
    """Create the footer section with Vercel Web Analytics"""
    return Footer(
        Div(
            P('© 2025 João Rodrigues. All rights reserved.'),
            P(
                A(
                    'Instagram',
                    href='https://instagram.com/__joaor__',
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
        # Vercel Web Analytics
        *create_analytics(),
    )
