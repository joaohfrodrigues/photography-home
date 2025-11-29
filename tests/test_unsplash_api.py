"""Test script to fetch and analyze Unsplash API response"""
import json
import requests
from config import UNSPLASH_ACCESS_KEY, UNSPLASH_USERNAME

def test_user_photos_endpoint():
    """Test the /users/{username}/photos endpoint and save response"""
    print(f"Fetching photos for user: {UNSPLASH_USERNAME}")
    print(f"Using API key: {UNSPLASH_ACCESS_KEY[:10]}..." if UNSPLASH_ACCESS_KEY else "No API key")
    print("="*80)
    
    headers = {'Authorization': f'Client-ID {UNSPLASH_ACCESS_KEY}'}
    
    # Test 1: Basic endpoint (what we're currently using)
    print("\n[TEST 1] /users/{username}/photos endpoint (current implementation)")
    response1 = requests.get(
        f'https://api.unsplash.com/users/{UNSPLASH_USERNAME}/photos',
        headers=headers,
        params={
            'per_page': 3,  # Just get 3 for testing
            'order_by': 'latest',
            'stats': 'true',
        },
        timeout=10
    )
    
    if response1.status_code == 200:
        photos1 = response1.json()
        print(f"✓ Success! Got {len(photos1)} photos")
        
        # Save full response
        with open('test_output_user_photos.json', 'w') as f:
            json.dump(photos1, f, indent=2)
        print("✓ Saved to: test_output_user_photos.json")
        
        # Analyze first photo
        if photos1:
            photo = photos1[0]
            print(f"\n--- First Photo Analysis ---")
            print(f"ID: {photo.get('id')}")
            print(f"Description: {photo.get('description')}")
            print(f"Alt Description: {photo.get('alt_description')}")
            print(f"\nAvailable keys: {list(photo.keys())}")
            print(f"\nEXIF data present: {photo.get('exif') is not None}")
            if photo.get('exif'):
                print(f"EXIF content: {json.dumps(photo.get('exif'), indent=2)}")
            else:
                print("EXIF content: None or empty")
    else:
        print(f"✗ Error: {response1.status_code}")
        print(f"Response: {response1.text}")
    
    # Test 2: Individual photo endpoint (known to have EXIF)
    print("\n" + "="*80)
    print("\n[TEST 2] /photos/{id} endpoint (individual photo - should have EXIF)")
    
    if response1.status_code == 200 and photos1:
        photo_id = photos1[0]['id']
        response2 = requests.get(
            f'https://api.unsplash.com/photos/{photo_id}',
            headers=headers,
            timeout=10
        )
        
        if response2.status_code == 200:
            photo_detail = response2.json()
            print(f"✓ Success! Got photo details for {photo_id}")
            
            # Save individual photo response
            with open('test_output_single_photo.json', 'w') as f:
                json.dump(photo_detail, f, indent=2)
            print("✓ Saved to: test_output_single_photo.json")
            
            print(f"\n--- Single Photo Analysis ---")
            print(f"ID: {photo_detail.get('id')}")
            print(f"Description: {photo_detail.get('description')}")
            print(f"\nEXIF data present: {photo_detail.get('exif') is not None}")
            if photo_detail.get('exif'):
                print(f"EXIF content: {json.dumps(photo_detail.get('exif'), indent=2)}")
            else:
                print("EXIF content: None or empty")
        else:
            print(f"✗ Error: {response2.status_code}")
            print(f"Response: {response2.text}")
    
    print("\n" + "="*80)
    print("\n✓ Test complete! Check the JSON files for full API responses.")
    print("\nFiles created:")
    print("  - test_output_user_photos.json (list endpoint)")
    print("  - test_output_single_photo.json (individual photo endpoint)")

if __name__ == '__main__':
    test_user_photos_endpoint()
