"""Header component"""

from fasthtml.common import *


def create_navbar(current_page='home'):
    """Create a fixed navigation bar that's always visible at the top"""
    collections_active = (
        'opacity: 1; font-weight: 500;' if current_page == 'collections' else 'opacity: 0.8;'
    )
    about_active = 'opacity: 1; font-weight: 500;' if current_page == 'about' else 'opacity: 0.8;'

    return Nav(
        Div(
            A(
                'JOÃO RODRIGUES',
                href='/',
                cls='navbar-title',
                style='text-decoration: none;',
            ),
            Div(
                A(
                    'Collections',
                    href='/collections',
                    style=f'color: var(--text-primary); text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; transition: opacity 0.3s; {collections_active}',
                ),
                A(
                    'About',
                    href='/about',
                    style=f'color: var(--text-primary); text-decoration: none; margin-right: 1.5rem; font-size: 0.9rem; transition: opacity 0.3s; {about_active}',
                ),
                Button(
                    # Sun icon for light mode
                    NotStr("""
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="theme-icon sun-icon">
                            <circle cx="12" cy="12" r="5"></circle>
                            <line x1="12" y1="1" x2="12" y2="3"></line>
                            <line x1="12" y1="21" x2="12" y2="23"></line>
                            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
                            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
                            <line x1="1" y1="12" x2="3" y2="12"></line>
                            <line x1="21" y1="12" x2="23" y2="12"></line>
                            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
                            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
                        </svg>
                    """),
                    # Moon icon for dark mode
                    NotStr("""
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="theme-icon moon-icon">
                            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
                        </svg>
                    """),
                    id='theme-toggle',
                    cls='theme-toggle-btn',
                    onclick='toggleTheme()',
                    style='background: none; border: none; cursor: pointer; padding: 0.5rem; display: flex; align-items: center; color: var(--text-primary); transition: opacity 0.3s;',
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
                style='margin-bottom: 1rem; color: var(--text-tertiary); letter-spacing: 0.2rem; text-transform: uppercase;',
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
