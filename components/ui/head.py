"""HTML head component with SEO meta tags"""

from fasthtml.common import *


def create_head(
    title='João Rodrigues | Photography',
    description=None,
    current_url='https://joaohfrodrigues.com',
):
    """Create the HTML head section with SEO optimization"""

    if description is None:
        description = 'Professional photography portfolio by João Rodrigues. Explore stunning photographs from around the world, featuring landscapes, portraits, and travel photography.'

    # Structured data for SEO (JSON-LD)
    structured_data = """
    {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "João Rodrigues",
        "url": "https://joaohfrodrigues.com",
        "jobTitle": "Photographer",
        "description": "Professional photographer specializing in landscape, portrait, and travel photography",
        "sameAs": [
            "https://unsplash.com/@joaohfrodrigues",
            "https://instagram.com/joaohfrodrigues"
        ],
        "image": "https://joaohfrodrigues.com/static/favicons/apple-touch-icon.png"
    }
    """

    return Head(
        Title(title),
        Meta(name='viewport', content='width=device-width, initial-scale=1'),
        Meta(name='description', content=description),
        Meta(
            name='keywords',
            content='photography, portfolio, João Rodrigues, photos, landscape, portrait, travel',
        ),
        Meta(name='author', content='João Rodrigues'),
        Meta(charset='utf-8'),
        # Open Graph / Social Media
        Meta(property='og:type', content='website'),
        Meta(property='og:title', content=title),
        Meta(property='og:description', content=description),
        Meta(property='og:url', content=current_url),
        Meta(property='og:site_name', content='João Rodrigues Photography'),
        # Twitter Card
        Meta(name='twitter:card', content='summary_large_image'),
        Meta(name='twitter:title', content=title),
        Meta(name='twitter:description', content=description),
        # Favicons
        Link(rel='icon', type='image/x-icon', href='/static/favicons/favicon.ico'),
        Link(
            rel='icon', type='image/png', sizes='32x32', href='/static/favicons/favicon-32x32.png'
        ),
        Link(
            rel='icon', type='image/png', sizes='16x16', href='/static/favicons/favicon-16x16.png'
        ),
        Link(rel='apple-touch-icon', sizes='180x180', href='/static/favicons/apple-touch-icon.png'),
        # Preload critical resources
        Link(rel='preload', href='/static/css/styles.css', **{'as': 'style'}),
        Link(
            rel='preload',
            href='/static/NotoSans-VariableFont_wdth,wght.ttf',
            **{'as': 'font'},
            type='font/ttf',
            crossorigin='anonymous',
        ),
        # DNS prefetch for external domains
        Link(rel='dns-prefetch', href='https://images.unsplash.com'),
        Link(rel='preconnect', href='https://images.unsplash.com', crossorigin='anonymous'),
        # Stylesheet
        Link(rel='stylesheet', href='/static/css/styles.css'),
        # Structured data
        Script(structured_data, type='application/ld+json'),
        # JavaScript (deferred)
        Script(src='/static/js/lightbox.js', defer=True),
    )
