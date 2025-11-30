"""Page routes"""

import logging
from datetime import datetime

from fasthtml.common import *
from starlette.responses import FileResponse, HTMLResponse, Response

from components.pages.about import about_page
from components.pages.collection_detail import collection_detail_page
from components.pages.collections import collections_page
from components.pages.gallery import gallery_page
from components.pages.home import home_page
from services import fetch_unsplash_photos, fetch_user_collections

logger = logging.getLogger(__name__)


def register_page_routes(rt, app):
    """Register all page routes"""

    @rt('/')
    def get(order: str = 'popular'):
        """Homepage with collection previews and latest photos"""
        logger.info(f'Homepage accessed - fetching collection previews (order: {order})')
        collections = fetch_user_collections()
        logger.info(f'Rendering homepage with {len(collections)} collections')
        return home_page(collections, order=order)

    @rt('/collections')
    def get():
        """All collections grid page"""
        logger.info('Collections page accessed')
        collections = fetch_user_collections()
        logger.info(f'Rendering collections page with {len(collections)} collections')
        return collections_page(collections)

    @rt('/collection/{collection_id}')
    def get(collection_id: str):
        """Collection detail page with photo gallery"""
        logger.info(f'Collection detail page accessed: {collection_id}')
        return collection_detail_page(collection_id)

    @rt('/gallery')
    def get():
        """Legacy gallery route - all photos"""
        logger.info('Legacy gallery accessed - fetching photos')
        photos = fetch_unsplash_photos()
        logger.info(f'Rendering gallery with {len(photos)} photos')
        return gallery_page(photos)

    @rt('/about')
    def get():
        """About page route"""
        return about_page()

    @rt('/robots.txt')
    def get():
        """Serve robots.txt"""
        return FileResponse('static/robots.txt', media_type='text/plain')

    @rt('/sitemap.xml')
    def get():
        """Generate dynamic sitemap"""
        # Get collections to include in sitemap
        collections = fetch_user_collections()
        collection_urls = '\n'.join(
            [
                f"""    <url>
        <loc>https://joaohfrodrigues.com/collection/{c['id']}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>"""
                for c in collections
            ]
        )

        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://joaohfrodrigues.com/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>https://joaohfrodrigues.com/collections</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.9</priority>
    </url>
{collection_urls}
    <url>
        <loc>https://joaohfrodrigues.com/about</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
    <url>
        <loc>https://joaohfrodrigues.com/gallery</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.6</priority>
    </url>
</urlset>"""
        return Response(content=sitemap, media_type='application/xml')

    # Custom error pages
    @app.exception_handler(404)
    async def not_found(request, exc):
        """Custom 404 page"""
        logger.warning(f'404 error: {request.url.path}')
        return HTMLResponse(
            Html(
                Head(
                    Meta(charset='UTF-8'),
                    Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
                    Title('404 - Page Not Found'),
                    Link(rel='stylesheet', href='/static/css/styles.css'),
                ),
                Body(
                    Div(
                        H1('404', style='font-size: 6rem; margin-bottom: 1rem;'),
                        P('Page not found', style='font-size: 1.5rem; margin-bottom: 2rem;'),
                        A('← Back to Home', href='/', cls='btn-link'),
                        cls='error-page',
                    )
                ),
            ).render()
        )

    @app.exception_handler(500)
    async def server_error(request, exc):
        """Custom 500 page"""
        logger.error(f'500 error: {exc}')
        return HTMLResponse(
            Html(
                Head(
                    Meta(charset='UTF-8'),
                    Meta(name='viewport', content='width=device-width, initial-scale=1.0'),
                    Title('500 - Server Error'),
                    Link(rel='stylesheet', href='/static/css/styles.css'),
                ),
                Body(
                    Div(
                        H1('500', style='font-size: 6rem; margin-bottom: 1rem;'),
                        P('Something went wrong', style='font-size: 1.5rem; margin-bottom: 2rem;'),
                        A('← Back to Home', href='/', cls='btn-link'),
                        cls='error-page',
                    )
                ),
            ).render()
        )
