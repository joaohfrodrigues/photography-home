"""Tests for database service layer"""

import pytest

import backend.database as db_module
from backend.database import (
    get_db_connection,
    init_database,
    insert_collection,
    insert_photo,
    link_photo_to_collection,
)
from backend.db_service import (
    get_all_collections,
    get_collection_photos,
    get_database_stats,
    get_latest_photos,
    get_photo_by_id,
)


@pytest.fixture
def test_db_with_data(tmp_path):
    """Create a test database with sample data"""
    original_path = db_module.DB_PATH
    db_module.DB_PATH = tmp_path / 'test_photos.db'

    # Initialize database
    init_database()

    # Insert test collections
    test_collections = [
        {
            'id': 'col1',
            'title': 'Collection 1',
            'description': 'Test collection 1',
            'total_photos': 5,
            'updated_at': '2024-01-05T00:00:00Z',
            'published_at': '2024-01-01T00:00:00Z',
        },
        {
            'id': 'col2',
            'title': 'Collection 2',
            'description': 'Test collection 2',
            'total_photos': 5,
            'updated_at': '2024-01-10T00:00:00Z',
            'published_at': '2024-01-01T00:00:00Z',
        },
    ]

    # Insert test photos
    test_photos = [
        {
            'id': f'photo{i}',
            'title': f'Photo {i}',
            'description': f'Description {i}',
            'created_at': f'2024-01-{i + 1:02d}T00:00:00Z',
            'updated_at': f'2024-01-{i + 1:02d}T00:00:00Z',
            'views': (10 - i) * 100,  # Descending views
            'downloads': i * 10,
            'width': 1920,
            'height': 1080,
            'url_regular': f'https://example.com/photo{i}.jpg',
            'photographer_name': f'Photographer {i}',
            'tags': [f'tag{i}', 'common'],
        }
        for i in range(10)
    ]

    with get_db_connection() as conn:
        # Insert collections
        for collection in test_collections:
            insert_collection(conn, collection)

        # Insert photos
        for photo in test_photos:
            insert_photo(conn, photo)

        # Link photos to collections
        for i in range(10):
            collection_id = 'col1' if i < 5 else 'col2'
            link_photo_to_collection(
                conn, f'photo{i}', collection_id, f'2024-01-{i + 1:02d}T00:00:00Z'
            )

        conn.commit()

    yield db_module.DB_PATH

    # Cleanup
    db_module.DB_PATH = original_path


def test_get_latest_photos(test_db_with_data):
    """Test fetching latest photos with pagination"""
    # Get first page
    photos, has_more = get_latest_photos(page=1, per_page=5, order_by='latest')

    assert len(photos) == 5
    assert has_more is True
    assert photos[0]['title'] == 'Photo 9'  # Most recent

    # Get second page
    photos, has_more = get_latest_photos(page=2, per_page=5, order_by='latest')

    assert len(photos) == 5
    assert has_more is False


def test_get_latest_photos_popular(test_db_with_data):
    """Test fetching photos ordered by popularity"""
    photos, has_more = get_latest_photos(page=1, per_page=5, order_by='popular')

    assert len(photos) == 5
    assert photos[0]['title'] == 'Photo 0'  # Most views (1000)
    assert photos[1]['title'] == 'Photo 1'  # Second most (900)


def test_get_collection_photos(test_db_with_data):
    """Test fetching photos from a specific collection"""
    photos, has_more = get_collection_photos('col1', page=1, per_page=10)

    assert len(photos) == 5
    assert has_more is False
    assert all(p['id'].startswith('photo') and int(p['id'][5:]) < 5 for p in photos)


def test_get_all_collections(test_db_with_data):
    """Test fetching all collections"""
    collections = get_all_collections()

    assert len(collections) == 2
    assert collections[0]['id'] == 'col2'  # Most recently updated
    assert collections[0]['title'] == 'Collection 2'
    assert collections[0]['total_photos'] == 5
    assert collections[1]['id'] == 'col1'


def test_get_photo_by_id(test_db_with_data):
    """Test fetching a single photo by ID"""
    photo = get_photo_by_id('photo5')

    assert photo is not None
    assert photo['id'] == 'photo5'
    assert photo['title'] == 'Photo 5'
    assert 'exif' in photo
    assert 'location' in photo
    assert 'user' in photo


def test_get_photo_by_id_not_found(test_db_with_data):
    """Test fetching non-existent photo returns None"""
    photo = get_photo_by_id('nonexistent')
    assert photo is None


def test_get_database_stats(test_db_with_data):
    """Test getting database statistics"""
    stats = get_database_stats()

    assert stats['total_photos'] == 10
    assert stats['total_collections'] == 2
    assert stats['total_views'] == 5500  # Sum of all views
    assert stats['total_downloads'] == 450  # Sum of all downloads


def test_row_to_dict_structure(test_db_with_data):
    """Test that returned photo dict has correct structure"""
    photo = get_photo_by_id('photo0')

    # Check top-level keys
    assert 'id' in photo
    assert 'title' in photo
    assert 'url' in photo
    assert 'views' in photo

    # Check nested objects
    assert isinstance(photo['exif'], dict)
    assert isinstance(photo['location'], dict)
    assert isinstance(photo['user'], dict)
    assert isinstance(photo['links'], dict)
    assert isinstance(photo['tags'], list)

    # Check statistics structure for backward compatibility
    assert 'statistics' in photo
    assert photo['statistics']['views']['total'] == photo['views']
