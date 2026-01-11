"""Test script to fetch and analyze Unsplash API response"""

import json

import requests

from config import UNSPLASH_ACCESS_KEY, UNSPLASH_USERNAME


def _print_photo_analysis(photo, title='First Photo Analysis'):
    """Print analysis of a single photo"""
    print(f'\n--- {title} ---')
    print(f'ID: {photo.get("id")}')
    print(f'Description: {photo.get("description")}')
    if 'alt_description' in photo:
        print(f'Alt Description: {photo.get("alt_description")}')
    if 'keys' in dir(photo):
        print(f'\nAvailable keys: {list(photo.keys())}')
    print(f'\nEXIF data present: {photo.get("exif") is not None}')
    if photo.get('exif'):
        print(f'EXIF content: {json.dumps(photo.get("exif"), indent=2)}')
    else:
        print('EXIF content: None or empty')

    # Print tags if available
    if 'tags' in photo:
        tags = photo.get('tags')
        print(f'\nTags: {tags}')
        if tags:
            print(f'Number of tags: {len(tags)}')
            if isinstance(tags, list) and tags and isinstance(tags[0], dict):
                print(f'First tag structure: {json.dumps(tags[0], indent=2)}')
    else:
        print('\nTags: Not available in this endpoint')


def _test_user_photos(headers):
    """Test the user photos endpoint"""
    print('\n[TEST 1] /users/{username}/photos endpoint (current implementation)')
    response = requests.get(
        f'https://api.unsplash.com/users/{UNSPLASH_USERNAME}/photos',
        headers=headers,
        params={'per_page': 3, 'order_by': 'latest', 'stats': 'true'},
        timeout=10,
    )

    if response.status_code != 200:
        print(f'✗ Error: {response.status_code}')
        print(f'Response: {response.text}')
        return None

    photos = response.json()
    print(f'✓ Success! Got {len(photos)} photos')

    if photos:
        _print_photo_analysis(photos[0])
    return photos


def _test_single_photo(photo_id, headers):
    """Test the single photo endpoint"""
    print('\n[TEST 2] /photos/{id} endpoint (individual photo - should have EXIF)')
    response = requests.get(
        f'https://api.unsplash.com/photos/{photo_id}', headers=headers, timeout=10
    )

    if response.status_code != 200:
        print(f'✗ Error: {response.status_code}')
        print(f'Response: {response.text}')
        return

    photo_detail = response.json()
    print(f'✓ Success! Got photo details for {photo_id}')

    _print_photo_analysis(photo_detail, 'Single Photo Analysis')


def test_user_photos_endpoint():
    """Test the /users/{username}/photos endpoint and save response"""
    print(f'Fetching photos for user: {UNSPLASH_USERNAME}')
    print(f'Using API key: {UNSPLASH_ACCESS_KEY[:10]}...' if UNSPLASH_ACCESS_KEY else 'No API key')
    print('=' * 80)

    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}

    # Test 1: User photos endpoint
    photos = _test_user_photos(headers)

    # Test 2: Individual photo endpoint
    if photos:
        print('\n' + '=' * 80)
        _test_single_photo(photos[0]['id'], headers)

    print('\n' + '=' * 80)
    print('\n✓ Test complete!')


if __name__ == '__main__':
    test_user_photos_endpoint()
