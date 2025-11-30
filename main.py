"""Photography portfolio website built with FastHTML

A professional photography portfolio featuring:
- Dynamic photo gallery from Unsplash
- Advanced filtering and search
- Responsive lightbox viewer
- Full Unsplash API compliance
"""

from fasthtml.common import fast_app
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.staticfiles import StaticFiles

from config import logger
from routes import register_api_routes, register_page_routes


class CacheControlMiddleware(BaseHTTPMiddleware):
    """Add cache control headers to static assets"""

    async def dispatch(self, request, call_next):
        response = await call_next(request)

        # Add cache headers for static files
        if request.url.path.startswith('/static/'):
            # Cache static assets for 7 days
            response.headers['Cache-Control'] = 'public, max-age=604800, immutable'
        elif request.url.path.startswith('/api/'):
            # API responses shouldn't be cached by browser
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        else:
            # HTML pages - short cache with validation
            response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'

        return response


def create_app():
    """Initialize and configure the FastHTML application"""
    # Initialize FastHTML app
    app, rt = fast_app(pico=False)

    # Add cache control middleware
    app.add_middleware(CacheControlMiddleware)

    # Mount static files directory
    app.mount('/static', StaticFiles(directory='static'), name='static')

    # Register routes
    register_page_routes(rt, app)
    register_api_routes(rt)

    logger.info('Application initialized successfully')
    return app, rt


# Create app instance
app, rt = create_app()


if __name__ == '__main__':
    import uvicorn

    logger.info('Starting development server on http://localhost:5001')
    uvicorn.run('main:app', host='0.0.0.0', port=5001, reload=True)  # nosec B104
