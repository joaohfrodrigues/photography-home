"""Photography portfolio website built with FastHTML

A professional photography portfolio featuring:
- Dynamic photo gallery from Unsplash
- Advanced filtering and search
- Responsive lightbox viewer
- Full Unsplash API compliance
"""

from fasthtml.common import fast_app
from starlette.staticfiles import StaticFiles

from config import logger
from routes import register_api_routes, register_page_routes


def create_app():
    """Initialize and configure the FastHTML application"""
    # Initialize FastHTML app
    app, rt = fast_app(pico=False)

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
