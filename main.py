"""Photography portfolio website built with FastHTML"""
import logging
from fasthtml.common import *
from config import logger
from services import fetch_unsplash_photos, trigger_download, fetch_photo_details
from components import create_head, create_hero, create_gallery, create_footer, create_lightbox

# Initialize FastHTML app
app, rt = fast_app(
    pico=False
)

# Mount static files directory
from starlette.staticfiles import StaticFiles
app.mount('/static', StaticFiles(directory='static'), name='static')


@rt('/')
def get():
    """Homepage route"""
    logger.info("Homepage accessed - fetching photos")
    photos = fetch_unsplash_photos()
    logger.info(f"Rendering gallery with {len(photos)} photos")
    
    return Html(
        create_head(),
        Body(
            create_hero(),
            create_gallery(photos),
            create_footer(),
            create_lightbox()
        )
    )


@rt('/api/trigger-download')
def get(photo_id: str = '', download_location: str = ''):
    """API endpoint to trigger Unsplash download event"""
    logger.info(f"Download triggered for photo: {photo_id}")
    success = trigger_download(download_location)
    return {'success': success, 'photo_id': photo_id}


@rt('/api/photo-details/{photo_id}')
def get(photo_id: str):
    """API endpoint to fetch detailed photo information including EXIF"""
    logger.info(f"Fetching details for photo: {photo_id}")
    details = fetch_photo_details(photo_id)
    if details:
        return details
    else:
        return {'error': 'Failed to fetch photo details'}, 500


if __name__ == '__main__':
    logger.info("Starting FastHTML photography portfolio server")
    logger.info("="*50)
    serve()

