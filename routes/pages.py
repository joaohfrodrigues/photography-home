"""Page routes"""

import logging
from datetime import datetime

from fasthtml.common import *
from starlette.responses import FileResponse, HTMLResponse, Response

from backend.db_service import (
    get_all_collections,
    get_collection_by_id,
    get_collection_by_slug,
    search_photos,
)
from components.pages.about import about_page
from components.pages.collection_detail import collection_detail_page
from components.pages.collections import collections_page
from components.pages.home import home_page

logger = logging.getLogger(__name__)


def ft_to_html(component):
    """Convert FastHTML component tuple to HTML string"""
    return str(component)


def register_page_routes(rt, app):
    """Register all page routes"""

    @rt('/')
    def get_home(order: str = 'popular', page: int = 1, q: str = ''):
        """Home page with optional search, ordering, and pagination"""
        # Use search_photos which handles both search and ordering
        photos, has_more = search_photos(query=q, page=page, per_page=12, order_by=order)

        return home_page(
            latest_photos=photos, order=order, search_query=q, current_page=page, has_more=has_more
        )

    @rt('/collections')
    def get_collections():
        """Collections page"""
        return collections_page()

    @rt('/collection/{identifier}')
    def get_collection_detail(identifier: str, page: int = 1, q: str = ''):
        """Collection detail; accepts slug or legacy id, redirects to slug if needed."""
        collection = get_collection_by_slug(identifier)
        if collection:
            return collection_detail_page(collection['slug'], page=page, search_query=q)

        collection = get_collection_by_id(identifier)
        if collection:
            return Response(
                status_code=301,
                headers={'Location': f"/collection/{collection['slug']}"},
            )

        return HTMLResponse(status_code=404, content='Collection not found')

    @rt('/about')
    def get_about():
        """About page"""
        return about_page()

    @rt('/robots.txt')
    def get_robots():
        """Serve robots.txt"""
        return FileResponse('static/robots.txt', media_type='text/plain')

    @rt('/sitemap.xml')
    def get_sitemap():
        """Generate dynamic sitemap"""
        try:
            collections = get_all_collections()
        except Exception as e:
            logger.error(f'Error fetching collections for sitemap: {e}')
            collections = []
        collection_urls = '\n'.join(
            [
                f"""    <url>
        <loc>https://joaohfrodrigues.com/collection/{c['slug']}</loc>
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
</urlset>"""
        return Response(content=sitemap, media_type='application/xml')

    @rt('/{path:path}.map')
    def get_sourcemap(path: str):
        """Handle missing source map files with 204 No Content"""
        return Response(status_code=204)

    # Custom error pages
    @app.exception_handler(404)
    async def not_found(request, exc):
        """Custom 404 page"""
        logger.warning(f'404 error: {request.url.path}')
        component = Html(
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
        )
        return HTMLResponse(ft_to_html(component), status_code=404)

    @app.exception_handler(500)
    async def server_error(request, exc):
        """Custom 500 page"""
        logger.error(f'500 error: {exc}')
        component = Html(
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
        )
        return HTMLResponse(ft_to_html(component), status_code=500)
