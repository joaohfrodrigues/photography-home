# Backend Architecture

This backend uses a local SQLite database to store all photo metadata with proper
relational structure, eliminating the need for repeated API calls to Unsplash.

## Structure

```text
backend/
├── __init__.py
├── database.py      # Database schema and operations
├── db_service.py    # Query layer for reading data
└── etl.py           # ETL script to sync from Unsplash

data/
└── photos.db        # SQLite database (committed to git)
```

## Database Schema

### Tables

**photos** (46 fields)

- Photo details: id, title, description, dimensions, colors
- Statistics: views, downloads, likes
- EXIF data: camera make/model, exposure, aperture, ISO, focal length
- Location: name, city, country, coordinates (lat/long)
- Photographer: name, username, profile URL
- URLs: raw, full, regular, small, thumb
- Timestamps: created_at, updated_at, last_synced_at

**collections** (9 fields)

- Collection metadata: id, title, description
- Statistics: total_photos
- Timestamps: published_at, updated_at, last_synced_at
- Cover photo: cover_photo_id, cover_photo_url

**photo_collections** (Junction table)

- photo_id (FK → photos.id)
- collection_id (FK → collections.id)
- added_at timestamp
- Composite primary key (photo_id, collection_id)

### Indexes

- FTS5 virtual table for full-text search across photos
- Composite index on (photo_id, collection_id) in junction table
- Individual indexes on foreign keys

## Usage

### Initial Setup

1. Run ETL to populate database:

```bash
# Sync all photos (production)
python backend/etl.py

# Test mode (only 5 photos per collection)
python backend/etl.py --test

# Limit photos per collection
python backend/etl.py --max-photos 10
```

## ETL Pipeline

### Sync Strategy (Optimized)

The ETL minimizes API calls while fetching complete data:

1. **Fetch user photos with statistics** (5 API calls)
    - Gets all photos with view/download counts
    - No EXIF or location data at this stage

2. **Fetch EXIF for featured photos** (2 API calls)
    - Strategic fetching for only 2 photos
    - Gets complete EXIF + location data

3. **Fetch collections metadata** (1 API call)
    - Gets all user collections

4. **Link photos to collections** (8 API calls)
    - Fetches collection photos for linking
    - Creates many-to-many relationships

**Total: 16 API calls** per sync (well within 50/hour limit)

### Transform Functions

- `transform_photo(photo, fetch_exif, access_key)` - Converts API data to database schema
- `sync_photos(access_key, username, max_photos)` - Main ETL orchestration

### Development

The application automatically reads from the database:

- No API calls needed after initial sync
- Fast local queries
- Full EXIF data pre-fetched
- Full-text search available

### Testing

```bash
# Run tests
PYTHONPATH=. pytest tests/test_database.py tests/test_db_service.py -v

# Check database stats
python -c "from backend.db_service import get_database_stats; print(get_database_stats())"
```

### GitHub Actions

The ETL runs daily via GitHub Actions:

- Syncs latest photos from Unsplash
- Updates statistics (views/downloads)
- Commits updated database to git
- Workflow file: `.github/workflows/sync-photos.yaml`

## Benefits

✅ **No Rate Limits** - All data pre-fetched daily  
✅ **Fast Queries** - Local SQLite with proper indexes  
✅ **Offline Development** - Work without API access  
✅ **Complete EXIF** - Strategic fetching for featured photos  
✅ **Full-Text Search** - FTS5 virtual table  
✅ **Relational Data** - Proper many-to-many for collections

## API Endpoints (implemented)

- `GET /api/photo-details/{id}` - Photo details (EXIF included)
- `GET /api/trigger-download` - Compliance (uses Unsplash API)

## Query Layer (`db_service.py`)

- `get_latest_photos(order, page, limit)` - Paginated photos with sorting
- `get_all_collections()` - All collections with cover photos
- `get_collection_photos(collection_id, page, limit)` - Photos in collection
- `get_photo_by_id(photo_id)` - Single photo details
- `get_database_stats()` - Database statistics

## Running Tests

```bash
# Run all tests
PYTHONPATH=. pytest -v

# Database tests only
PYTHONPATH=. pytest tests/test_database.py -v

# Service layer tests
PYTHONPATH=. pytest tests/test_db_service.py -v

# ETL transformation tests
PYTHONPATH=. pytest tests/test_etl_transform.py -v
```

Current status: **28/28 tests passing** ✅
