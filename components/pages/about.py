"""About page component"""

from fasthtml.common import *

from components.ui.footer import create_footer
from components.ui.head import create_head
from components.ui.header import create_navbar
from services.markdown import load_markdown_page


def about_page():
    """Render the About page from markdown content"""
    # Load markdown content
    metadata, html_content = load_markdown_page('about')

    return Html(
        create_head(
            title=metadata.get('title', 'About | João Rodrigues'),
            description=metadata.get(
                'description', 'Data Engineer and hobbyist photographer based in Lisbon, Portugal'
            ),
            current_url=metadata.get('url', 'https://joaohfrodrigues.com/about'),
        ),
        Body(
            create_navbar(current_page='about'),
            # Content
            Main(
                Section(
                    Div(
                        H1(
                            'About Me',
                            style='font-size: 2.5rem; margin-bottom: 2.5rem; text-align: center;',
                        ),
                        Div(
                            NotStr(html_content),  # Render HTML content from markdown
                            cls='markdown-content',
                            style="""
                                font-family: 'Noto Sans', 'Helvetica Neue', Arial, sans-serif;
                                font-size: 1.1rem;
                                line-height: 1.8;
                                color: #ccc;
                            """,
                        ),
                        cls='container',
                        style='max-width: 800px; margin: 0 auto; padding: 8rem 2rem 4rem;',
                    ),
                    style='min-height: 50vh;',
                ),
            ),
            # Use shared footer component
            create_footer(),
        ),
    )
