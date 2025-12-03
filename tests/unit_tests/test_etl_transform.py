"""Tests for ETL transform functions using real API fixtures"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.etl import transform_photo

# Load fixtures
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


def load_fixture(filename):
    """Load a JSON fixture file"""
    filepath = FIXTURES_DIR / filename
    if not filepath.exists():
        pytest.skip(f'Fixture {filename} not found. Run tests/fixtures/fetch_test_data.py first.')
    with open(filepath) as f:
        return json.load(f)


@pytest.fixture
def collection_photo():
    """Photo from collection endpoint (no EXIF, no stats)"""
    return load_fixture('collection_photo.json')


@pytest.fixture
def user_photo_with_stats():
    """Photo from user photos endpoint with statistics"""
    return load_fixture('user_photo_with_stats.json')


@pytest.fixture
def photo_with_exif():
    """Photo from individual photo endpoint with EXIF"""
    return load_fixture('photo_with_exif.json')


@pytest.fixture
def photo_with_exif_and_location():
    """Photo ON9hQ_02Cn4 with comprehensive EXIF and location data"""
    return load_fixture('photo_ON9hQ_02Cn4.json')


@pytest.fixture
def collection_data():
    """Collection metadata"""
    return load_fixture('collection.json')


class TestTransformPhoto:
    """Test photo transformation with real API data"""

    def test_transform_collection_photo(self, collection_photo):
        """Test transforming a photo from collection endpoint (no EXIF, no stats)"""
        result = transform_photo(collection_photo)

        # Basic fields
        assert result['id'] == collection_photo['id']
        assert result['width'] == collection_photo['width']
        assert result['height'] == collection_photo['height']
        assert result['color'] == collection_photo['color']
        assert result['blur_hash'] == collection_photo['blur_hash']

        # URLs
        assert result['url_raw'] == collection_photo['urls']['raw']
        assert result['url_full'] == collection_photo['urls']['full']
        assert result['url_regular'] == collection_photo['urls']['regular']
        assert result['url_small'] == collection_photo['urls']['small']
        assert result['url_thumb'] == collection_photo['urls']['thumb']

        # Photographer
        assert result['photographer_name'] == collection_photo['user']['name']
        assert result['photographer_username'] == collection_photo['user']['username']

        # Statistics should be 0 (not available from collection endpoint)
        assert result['views'] == 0
        assert result['downloads'] == 0

        # EXIF should be None (not requested)
        assert result['exif_make'] is None
        assert result['exif_model'] is None

    def test_transform_user_photo_with_stats(self, user_photo_with_stats):
        """Test transforming a photo from user photos endpoint with statistics"""
        result = transform_photo(user_photo_with_stats)

        # Statistics should be populated
        stats = user_photo_with_stats.get('statistics', {})
        expected_views = stats.get('views', {}).get('total', 0)
        expected_downloads = stats.get('downloads', {}).get('total', 0)

        assert result['views'] == expected_views
        assert result['downloads'] == expected_downloads
        assert result['views'] > 0  # Should have real view count
        assert result['downloads'] >= 0  # Should have real download count

        # EXIF should still be None (not available from user photos endpoint)
        assert result['exif_make'] is None
        assert result['exif_model'] is None

    def test_transform_photo_with_exif(self, photo_with_exif):
        """Test transforming a photo from individual photo endpoint with EXIF"""
        result = transform_photo(photo_with_exif)

        # EXIF should be populated (already in the data)
        exif = photo_with_exif.get('exif', {})
        if exif:
            assert result['exif_make'] == exif.get('make')
            assert result['exif_model'] == exif.get('model')
            assert result['exif_exposure_time'] == exif.get('exposure_time')
            assert result['exif_aperture'] == exif.get('aperture')
            assert result['exif_focal_length'] == exif.get('focal_length')
            if exif.get('iso'):
                assert result['exif_iso'] == str(exif['iso'])

    def test_transform_with_location(self, photo_with_exif):
        """Test location data transformation"""
        result = transform_photo(photo_with_exif)

        location = photo_with_exif.get('location', {})
        if location:
            assert result['location_name'] == location.get('name')
            assert result['location_city'] == location.get('city')
            assert result['location_country'] == location.get('country')

            position = location.get('position', {})
            if position:
                assert result['location_latitude'] == position.get('latitude')
                assert result['location_longitude'] == position.get('longitude')

    def test_transform_with_tags(self, photo_with_exif):
        """Test tags transformation"""
        result = transform_photo(photo_with_exif)

        tags = photo_with_exif.get('tags', [])
        expected_tags = [tag.get('title', '') for tag in tags if tag.get('title')]

        assert result['tags'] == expected_tags
        if tags:
            assert len(result['tags']) > 0

    def test_transform_creates_title(self, collection_photo):
        """Test that transform creates a title from description or alt_description"""
        result = transform_photo(collection_photo)

        # Should have a title (either description, alt_description, or fallback)
        assert result['title']
        assert len(result['title']) > 0

    def test_transform_has_sync_timestamp(self, collection_photo):
        """Test that transform adds last_synced_at timestamp"""
        result = transform_photo(collection_photo)

        assert 'last_synced_at' in result
        assert result['last_synced_at']
        # Should be ISO format timestamp
        assert 'T' in result['last_synced_at']
        assert 'Z' in result['last_synced_at'] or '+' in result['last_synced_at']


class TestEXIFRetrieval:
    """Test EXIF data retrieval and transformation"""

    def test_exif_data_from_individual_endpoint(self, photo_with_exif_and_location):
        """Test that EXIF data is correctly extracted from individual photo endpoint"""
        result = transform_photo(photo_with_exif_and_location)

        # Verify EXIF data is populated
        assert result['exif_make'] == 'SONY'
        assert result['exif_model'] == 'ILCE-6600'
        assert result['exif_exposure_time'] == '1/250'
        assert result['exif_aperture'] == '5.6'
        assert result['exif_focal_length'] == '73.0'
        assert result['exif_iso'] == '100'

    def test_exif_not_in_user_photos_endpoint(self, user_photo_with_stats):
        """Test that EXIF data is NOT available from user photos endpoint"""
        result = transform_photo(user_photo_with_stats)

        # EXIF should be None (not available from user photos endpoint)
        assert result['exif_make'] is None
        assert result['exif_model'] is None
        assert result['exif_exposure_time'] is None
        assert result['exif_aperture'] is None
        assert result['exif_focal_length'] is None
        assert result['exif_iso'] is None


class TestLocationRetrieval:
    """Test location data retrieval and transformation"""

    def test_location_data_from_individual_endpoint(self, photo_with_exif_and_location):
        """Test that location data is correctly extracted from individual photo endpoint"""
        result = transform_photo(photo_with_exif_and_location)

        # Verify location data is populated
        assert result['location_name'] == 'Test Island, Test Region, Test Country'
        assert result['location_city'] is None  # This photo doesn't have city
        assert result['location_country'] == 'Test Country'

        # Verify coordinates
        assert result['location_latitude'] == 38.458049
        assert result['location_longitude'] == -28.322816

    def test_location_not_in_user_photos_endpoint(self, user_photo_with_stats):
        """Test that location data is NOT available from user photos endpoint"""
        result = transform_photo(user_photo_with_stats)

        # Location should be None (not available from user photos endpoint)
        assert result['location_name'] is None
        assert result['location_city'] is None
        assert result['location_country'] is None
        assert result['location_latitude'] is None
        assert result['location_longitude'] is None

    def test_location_coordinates_are_floats(self, photo_with_exif_and_location):
        """Test that coordinates are stored as floats"""
        result = transform_photo(photo_with_exif_and_location)

        # Coordinates should be float type
        assert isinstance(result['location_latitude'], float)
        assert isinstance(result['location_longitude'], float)

        # Should be valid coordinate ranges
        assert -90 <= result['location_latitude'] <= 90
        assert -180 <= result['location_longitude'] <= 180


class TestCollectionData:
    """Test collection data structure"""

    def test_collection_has_required_fields(self, collection_data):
        """Test that collection fixture has all required fields"""
        assert 'id' in collection_data
        assert 'title' in collection_data
        assert 'total_photos' in collection_data
        assert 'updated_at' in collection_data
        assert 'published_at' in collection_data

        # Cover photo
        assert 'cover_photo' in collection_data
        if collection_data['cover_photo']:
            assert 'id' in collection_data['cover_photo']
            assert 'urls' in collection_data['cover_photo']

    def test_collection_title_is_string(self, collection_data):
        """Test collection title is a non-empty string"""
        assert isinstance(collection_data['title'], str)
        assert len(collection_data['title']) > 0

    def test_collection_total_photos_is_positive(self, collection_data):
        """Test collection has positive photo count"""
        assert isinstance(collection_data['total_photos'], int)
        assert collection_data['total_photos'] > 0
