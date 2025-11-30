"""Routes package - centralized route registration"""

from .api import register_api_routes
from .pages import register_page_routes

__all__ = ['register_page_routes', 'register_api_routes']
