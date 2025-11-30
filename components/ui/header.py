"""Header component"""

from fasthtml.common import *


def create_navbar(current_page='home'):
    """Create a fixed navigation bar that's always visible at the top"""
    home_active = 'opacity: 1; font-weight: 500;' if current_page == 'home' else 'opacity: 0.8;'
    collections_active = (
        'opacity: 1; font-weight: 500;' if current_page == 'collections' else 'opacity: 0.8;'
    )
    about_active = 'opacity: 1; font-weight: 500;' if current_page == 'about' else 'opacity: 0.8;'

    return Nav(
        Div(
            Span('JOÃO RODRIGUES', cls='navbar-title'),
            Div(
                A(
                    'Home',
                    href='/',
                    style=f'color: #fff; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; transition: opacity 0.3s; {home_active}',
                ),
                A(
                    'Collections',
                    href='/collections',
                    style=f'color: #fff; text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; transition: opacity 0.3s; {collections_active}',
                ),
                A(
                    'About',
                    href='/about',
                    style=f'color: #fff; text-decoration: none; font-size: 0.9rem; transition: opacity 0.3s; {about_active}',
                ),
                cls='navbar-links',
            ),
            cls='navbar-content',
        ),
        cls='navbar',
        id='navbar',
    )


def create_header(current_page='home'):
    """Create the hero section (no longer contains navigation)"""
    return Header(
        Div(
            H1('JOÃO RODRIGUES'),
            P(
                'Photography, Data and Development',
                style='margin-bottom: 1rem; color: #888; letter-spacing: 0.2rem; text-transform: uppercase;',
            ),
            cls='hero-content',
        ),
        cls='hero',
        id='hero',
    )


def create_hero():
    """Create the hero section with scroll indicator for gallery page"""
    return Div(
        create_header(current_page='home'), Div(cls='scroll-indicator'), style='position: relative;'
    )
