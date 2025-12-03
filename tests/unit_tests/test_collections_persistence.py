"""Tests for persisting collections and linking photos to collections."""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import backend.database as db_module
from backend.database import (
    get_db_connection,
    init_database,
    insert_collection,
    insert_photo,
    link_photo_to_collection,
)
from backend.etl import transform_photo

FIXTURES_DIR = Path(__file__).parent / 'fixtures'


def load_fixture(filename):
    filepath = FIXTURES_DIR / filename
    if not filepath.exists():
        pytest.skip(f'Fixture {filename} not found. Run tests/fixtures/fetch_test_data.py first.')
    with open(filepath) as f:
        return json.load(f)


@pytest.fixture
def test_db(tmp_path):
    original = db_module.DB_PATH
    db_module.DB_PATH = tmp_path / 'test_photos.db'
    init_database()
    yield db_module.DB_PATH
    db_module.DB_PATH = original


def test_collection_and_photo_link_persisted(test_db):
    """Insert a collection and a photo from fixtures, link them, and verify persistence."""
    collection = load_fixture('collection.json')
    photo = load_fixture('collection_photo.json')

    # Build collection data similar to ETL
    collection_data = {
        'id': collection['id'],
        'title': collection['title'],
        'description': collection.get('description', ''),
        'total_photos': collection.get('total_photos', 0),
        'published_at': collection.get('published_at'),
        'updated_at': collection.get('updated_at'),
        'cover_photo_id': collection.get('cover_photo', {}).get('id')
        if collection.get('cover_photo')
        else None,
        'cover_photo_url': collection.get('cover_photo', {}).get('urls', {}).get('regular')
        if collection.get('cover_photo')
        else None,
        'last_synced_at': '2024-01-01T00:00:00Z',
    }

    transformed_photo = transform_photo(photo)

    with get_db_connection() as conn:
        # Insert collection and photo
        insert_collection(conn, collection_data)
        insert_photo(conn, transformed_photo)

        # Link the photo to the collection
        link_photo_to_collection(
            conn,
            transformed_photo['id'],
            collection_data['id'],
            transformed_photo.get('created_at', '2024-01-01T00:00:00Z'),
        )
        conn.commit()

        cursor = conn.cursor()

        # Verify collection exists
        cursor.execute('SELECT * FROM collections WHERE id = ?', (collection_data['id'],))
        col_row = cursor.fetchone()
        assert col_row is not None
        assert col_row['title'] == collection_data['title']
        assert col_row['total_photos'] == collection_data['total_photos']
        assert col_row['cover_photo_id'] == collection_data['cover_photo_id']
        assert col_row['cover_photo_url'] == collection_data['cover_photo_url']

        # Verify photo exists
        cursor.execute('SELECT * FROM photos WHERE id = ?', (transformed_photo['id'],))
        photo_row = cursor.fetchone()
        assert photo_row is not None

        # Verify link exists in junction table
        cursor.execute(
            'SELECT COUNT(*) FROM photo_collections WHERE photo_id = ? AND collection_id = ?',
            (transformed_photo['id'], collection_data['id']),
        )
        assert cursor.fetchone()[0] == 1
