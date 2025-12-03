"""Tests that the DB service returns correct structures for the UI.

These tests insert fixtures into a temporary DB (via ETL transform helpers)
and then exercise `backend.db_service` functions that the UI uses to fetch
photos, collections, and statistics.
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import backend.database as db_module
from backend import db_service
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


def test_db_service_returns_ui_shapes(test_db):
    # Load fixtures
    photo_a = load_fixture('photo_ON9hQ_02Cn4.json')
    photo_b = load_fixture('user_photo_with_stats.json')
    photo_c = load_fixture('collection_photo.json')
    collection = load_fixture('collection.json')

    # Transform photos
    t_a = transform_photo(photo_a)
    t_b = transform_photo(photo_b)
    t_c = transform_photo(photo_c)

    # Prepare collection payload
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

    with get_db_connection() as conn:
        # Insert collection and photos
        insert_collection(conn, collection_data)
        insert_photo(conn, t_a)
        insert_photo(conn, t_b)
        insert_photo(conn, t_c)

        # Link photo_c to the collection
        link_photo_to_collection(
            conn, t_c['id'], collection_data['id'], t_c.get('created_at', '2024-01-01T00:00:00Z')
        )
        conn.commit()

    # get_all_collections should include our collection with cover_photo.url
    cols = db_service.get_all_collections()
    assert any(c['id'] == collection_data['id'] for c in cols)
    col = next(c for c in cols if c['id'] == collection_data['id'])
    assert 'cover_photo' in col and 'url' in col['cover_photo']

    # get_collection_photos should return the linked photo
    photos_in_col, has_more = db_service.get_collection_photos(collection_data['id'])
    assert len(photos_in_col) == 1
    assert photos_in_col[0]['id'] == t_c['id']

    # get_latest_photos should return photos in expected shape (basic check)
    latest, has_more = db_service.get_latest_photos(page=1, per_page=10)
    assert isinstance(latest, list)
    if latest:
        p = latest[0]
        # UI expects these keys
        for key in ('id', 'url', 'title'):
            assert key in p

    # get_photo_by_id should return full photo dict and numeric stats
    # For each fixture, verify DB preserves the numeric values present in the
    # original JSON fixtures (or 0 when not present). This ensures we are
    # testing against the source-of-truth fixtures, not defaults from the ETL.
    fixtures = (photo_a, photo_b, photo_c)
    transformed = (t_a, t_b, t_c)
    for src, t in zip(fixtures, transformed, strict=False):
        fetched = db_service.get_photo_by_id(t['id'])
        assert fetched is not None
        # identity and user mapping
        assert fetched['id'] == t['id']
        assert fetched['user']['name'] == t.get('photographer_name')

        # Expected numeric values are taken from the original fixture
        expected_views = (src.get('statistics') or {}).get('views', {}).get('total', 0)
        expected_downloads = (src.get('statistics') or {}).get('downloads', {}).get('total', 0)

        assert fetched['views'] == expected_views
        assert fetched['downloads'] == expected_downloads
        # Also assert the nested statistics shape matches the top-level values
        assert fetched['statistics']['views']['total'] == expected_views
        assert fetched['statistics']['downloads']['total'] == expected_downloads

    # get_database_stats should reflect inserted counts
    stats = db_service.get_database_stats()
    assert stats['total_photos'] >= 3
    assert stats['total_collections'] >= 1

    # get_collection_stats should include our collection and total_photos >=1
    cstats = db_service.get_collection_stats()
    assert collection_data['id'] in cstats
    assert cstats[collection_data['id']]['total_photos'] >= 1
