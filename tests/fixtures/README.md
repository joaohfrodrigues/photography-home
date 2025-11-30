# Test Fixtures

This directory contains anonymized test data fixtures used in unit tests.

## Fixtures

### Collection Data

- **collection.json** - Sample collection metadata from the collections endpoint
  - Tests: Collection structure, metadata fields
  - Key fields: id, title, total_photos, cover_photo

### Photo Data (Different Endpoints)

- **collection_photo.json** - Photo from `/collections/{id}/photos` endpoint
  - Contains: Basic photo data, NO EXIF, NO statistics
  - Tests: Collection photo transformation without enriched data

- **user_photo_with_stats.json** - Photo from `/users/{username}/photos?stats=true` endpoint
  - Contains: Basic photo data + statistics, NO EXIF, NO location
  - Tests: Statistics extraction (views, downloads)

- **photo_with_exif.json** - Photo from `/photos/{id}` endpoint with EXIF
  - Contains: Complete EXIF data + location
  - Tests: EXIF extraction, location data, camera metadata

- **photo_ON9hQ_02Cn4.json** - Comprehensive photo with all metadata
  - Contains: Complete EXIF + location + all fields
  - Tests: Full data extraction including coordinates

## Data Anonymization

All fixtures contain **anonymized test data**:

- User information: Generic "Test Photographer" instead of real names
- Locations: Generic "Test City, Test Country" instead of real places
- URLs: Placeholder URLs with test identifiers
- IDs: Test identifiers like "test_photo_1" instead of real photo IDs

The data structure and field types match the real Unsplash API responses,
ensuring tests validate actual API behavior while protecting privacy.

## Key Testing Scenarios

### EXIF Data

- ✅ Available from: `/photos/{id}` endpoint only
- ❌ NOT available from: User photos or collection photos endpoints
- Tests verify EXIF is extracted when present and null when not available

### Location Data

- ✅ Available from: `/photos/{id}` endpoint only
- ❌ NOT available from: User photos or collection photos endpoints
- Tests verify location name, country, and coordinates extraction

### Statistics

- ✅ Available from: `/users/{username}/photos?stats=true` endpoint
- ❌ NOT available from: Collection photos endpoint
- Tests verify views and downloads are extracted correctly

## Usage

Tests automatically load fixtures using the `load_fixture()` helper:

```python
@pytest.fixture
def photo_with_exif():
    """Photo from individual photo endpoint with EXIF"""
    return load_fixture('photo_with_exif.json')
```

## Maintaining Fixtures

The fixtures are anonymized test data. If you need to update them:

1. Ensure the JSON structure matches the actual Unsplash API response format
2. Keep personal information anonymized (use "Test Photographer", "Test City", etc.)
3. Preserve the important test data (EXIF structure, location coordinates, statistics)
4. Run tests to verify: `pytest tests/test_etl_transform.py -v`
