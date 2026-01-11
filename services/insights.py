"""Insights and analytics service for dataset visualization"""

import logging
from collections import Counter

import pycountry

from backend.db_service import (
    get_all_collections,
    get_collection_photos,
)

logger = logging.getLogger(__name__)


def _extract_tags(photos: list) -> Counter:
    """Extract and count tags from photos.

    Args:
        photos: List of photo dictionaries

    Returns:
        Counter of tag titles
    """
    tags = Counter()
    total_photos_with_tags = 0

    for photo in photos:
        photo_tags = photo.get('tags', [])
        if not isinstance(photo_tags, list):
            continue

        if photo_tags:  # Only count if photo has tags
            total_photos_with_tags += 1

        for tag in photo_tags:
            tag_title = _extract_tag_title(tag)
            if tag_title:
                tags[tag_title] += 1

    logger.info(
        f'Extracted {len(tags)} unique tags from {total_photos_with_tags} photos with tags out of {len(photos)} total photos'
    )
    return tags


def _extract_tag_title(tag: dict | str) -> str:
    """Extract tag title from tag object or string.

    Args:
        tag: Tag as dictionary with 'title' key or as string

    Returns:
        Tag title string, or empty string if not found
    """
    if isinstance(tag, dict):
        return tag.get('title', '')
    if isinstance(tag, str):
        return tag
    return ''


def _get_country_code(country_name: str) -> str:
    """
    Get ISO 3166-1 alpha-3 country code for a country name using pycountry.

    Args:
        country_name: Country name to look up

    Returns:
        ISO 3-letter country code, or the original country name if not found
    """
    if not country_name:
        return country_name

    country_name_stripped = country_name.strip()

    if not pycountry:
        logger.warning('pycountry not installed, returning country name as-is')
        return country_name_stripped

    country_code = None

    try:
        # Try fuzzy search first (handles variations like "UK" for "United Kingdom")
        country = pycountry.countries.search_fuzzy(country_name_stripped)
        if country:
            country_code = country[0].alpha_3
    except (LookupError, AttributeError):
        pass

    if country_code is None:
        try:
            # Try exact name match
            for country in pycountry.countries:
                if country.name.lower() == country_name_stripped.lower():
                    country_code = country.alpha_3
                    break
                # Check official name variations
                if (
                    hasattr(country, 'official_name')
                    and country.official_name.lower() == country_name_stripped.lower()
                ):
                    country_code = country.alpha_3
                    break
                # Check common name if available
                if (
                    hasattr(country, 'common_name')
                    and country.common_name.lower() == country_name_stripped.lower()
                ):
                    country_code = country.alpha_3
                    break
        except (AttributeError, TypeError):
            pass

    # Return code if found, otherwise return original country name for fallback rendering
    if country_code is None:
        logger.debug(
            f'Country code not found for "{country_name_stripped}", '
            'using country name as fallback'
        )
        return country_name_stripped

    return country_code


def _get_all_photos_data() -> list:
    """Fetch all photos from all collections for analysis."""
    photos = []
    collections = get_all_collections()

    for collection in collections:
        collection_id = collection['id']
        page = 1

        while True:
            collection_photos, has_more = get_collection_photos(
                collection_id, page=page, per_page=100
            )
            photos.extend(collection_photos)

            if not has_more:
                break
            page += 1

    return photos


def get_dataset_stats() -> dict:
    """Get comprehensive dataset statistics.

    Returns:
        Dictionary containing aggregated statistics about photos, collections,
        engagement metrics, locations, and tags.
    """
    collections = get_all_collections()
    photos = _get_all_photos_data()

    # Calculate stats
    total_collections = len(collections)
    total_photos = len(photos)

    total_views = sum(p.get('views', 0) for p in photos)
    total_downloads = sum(p.get('downloads', 0) for p in photos)
    total_likes = sum(p.get('likes', 0) for p in photos)

    avg_views = total_views / total_photos if total_photos > 0 else 0
    avg_downloads = total_downloads / total_photos if total_photos > 0 else 0
    avg_likes = total_likes / total_photos if total_photos > 0 else 0

    # Get location data
    locations = Counter()
    for photo in photos:
        location = photo.get('location', {})
        city = location.get('city', '')
        country = location.get('country', '')
        if city and country:
            locations[f'{city}, {country}'] += 1
        elif country:
            locations[country] += 1

    # Get tag data
    tags = _extract_tags(photos)

    # Aggregate unique location count
    total_locations = len(locations)

    return {
        'total_collections': total_collections,
        'total_photos': total_photos,
        'total_views': total_views,
        'total_downloads': total_downloads,
        'total_likes': total_likes,
        'avg_views': round(avg_views, 0),
        'avg_downloads': round(avg_downloads, 2),
        'avg_likes': round(avg_likes, 1),
        'total_locations': total_locations,
        'top_locations': dict(locations.most_common(10)),
        'top_tags': dict(tags.most_common(15)),
        'photos': photos,
    }


def build_country_metrics(stats: dict) -> list[dict]:
    """Aggregate country-level metrics for photos, views, downloads.

    Returns a list of dicts: {name, code, photos, views, downloads}
    where `code` is ISO alpha-3 when resolvable.
    """
    locations = stats.get('top_locations', {})
    photos_list = stats.get('photos', [])

    # Seed with photo counts from top_locations
    country_data: dict[str, dict] = {}
    for location_name, count in locations.items():
        country = None
        if ',' in location_name:
            parts = location_name.split(',')
            country = parts[-1].strip()
        else:
            country = location_name
        if not country:
            continue
        country_data.setdefault(country, {'photos': 0, 'views': 0, 'downloads': 0})
        country_data[country]['photos'] += count

    # Accumulate views/downloads by country from per-photo data
    for photo in photos_list:
        location = photo.get('location', {}) or {}
        country = location.get('country', '') or ''
        if not country:
            continue
        country_data.setdefault(country, {'photos': 0, 'views': 0, 'downloads': 0})
        country_data[country]['views'] += photo.get('views', 0)
        country_data[country]['downloads'] += photo.get('downloads', 0)

    # Build list with codes
    result: list[dict] = []
    for country, metrics in country_data.items():
        result.append(
            {
                'name': country,
                'code': _get_country_code(country) or country,
                'photos': metrics.get('photos', 0),
                'views': metrics.get('views', 0),
                'downloads': metrics.get('downloads', 0),
            }
        )

    return result
