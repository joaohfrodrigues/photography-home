"""Tests that ETL transform output is correctly persisted to the database

This test loads real API fixtures, runs `transform_photo`, inserts the
result into a temporary test database, and asserts that the DB row contains
the expected fields (URLs, EXIF, location, user, links, tags).
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import backend.database as db_module
from backend.database import get_db_connection, init_database, insert_photo
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
    """Temporary DB for testing persistence"""
    original = db_module.DB_PATH
    db_module.DB_PATH = tmp_path / 'test_photos.db'
    init_database()
    yield db_module.DB_PATH
    db_module.DB_PATH = original


def test_fixture_photo_persists_all_fields(test_db):
    """Load a comprehensive fixture, transform it and persist to DB,
    then assert DB contains expected canonical fields."""
    fixture = load_fixture('photo_ON9hQ_02Cn4.json')

    # Transform (simulate fetching EXIF already present in fixture)
    transformed = transform_photo(fixture)

    with get_db_connection() as conn:
        insert_photo(conn, transformed)
        conn.commit()

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM photos WHERE id = ?', (transformed['id'],))
        row = cursor.fetchone()

        assert row is not None

        # URLs
        assert row['url_raw'] == transformed['url_raw']
        assert row['url_full'] == transformed['url_full']
        assert row['url_regular'] == transformed['url_regular']
        assert row['url_small'] == transformed['url_small']
        assert row['url_thumb'] == transformed['url_thumb']

        # Photographer
        assert row['photographer_name'] == transformed['photographer_name']
        assert row['photographer_username'] == transformed['photographer_username']
        assert row['photographer_url'] == transformed['photographer_url']

        # EXIF
        assert row['exif_make'] == transformed['exif_make']
        assert row['exif_model'] == transformed['exif_model']
        assert row['exif_exposure_time'] == transformed['exif_exposure_time']
        assert row['exif_aperture'] == transformed['exif_aperture']
        assert row['exif_focal_length'] == transformed['exif_focal_length']
        assert row['exif_iso'] == transformed['exif_iso']

        # Location
        assert row['location_name'] == transformed['location_name']
        assert row['location_city'] == transformed['location_city']
        assert row['location_country'] == transformed['location_country']
        assert row['location_latitude'] == transformed['location_latitude']
        assert row['location_longitude'] == transformed['location_longitude']

        # Links
        assert row['unsplash_url'] == transformed['unsplash_url']
        assert row['download_location'] == transformed['download_location']

        # Tags stored as JSON and match
        tags = json.loads(row['tags']) if row['tags'] else []
        assert tags == transformed['tags']
