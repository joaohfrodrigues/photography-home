"""Collection badge utilities - shared across pages"""

from datetime import datetime, timedelta, timezone

from fasthtml.common import Div

from config import FEATURED_COLLECTION_IDS


def is_newly_published(date_str, days=14):
    """Check if a collection was published within the last N days (default 14)"""
    if not date_str:
        return False
    try:
        published = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        return (now - published) < timedelta(days=days)
    except (ValueError, AttributeError):
        return False


def get_collection_badges(collection, collection_stats, all_collections):
    """Determine which badges to show for a collection

    Args:
        collection: Collection data dict with id, published_at, total_photos
        collection_stats: Dict mapping collection_id -> stats dict with total_views, etc.
        all_collections: List of all collection dicts (for comparison)

    Returns:
        List of badge dicts with 'text', 'emoji', and 'color' keys
    """
    badges = []
    collection_id = collection['id']

    # ⭐ Editor's Pick
    if collection_id in FEATURED_COLLECTION_IDS:
        badges.append(
            {
                'text': "Editor's Pick",
                'emoji': '⭐',
                'color': 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            }
        )

    # ✨ New Collection
    if is_newly_published(collection.get('published_at', '')):
        badges.append(
            {
                'text': 'New Collection',
                'emoji': '✨',
                'color': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            }
        )

    # 🔥 Most Popular (by total views)
    if collection_stats:
        max_views = max(
            (stats.get('total_views', 0) for stats in collection_stats.values()), default=0
        )
        current_views = collection_stats.get(collection_id, {}).get('total_views', 0)
        if current_views > 0 and current_views == max_views and max_views >= 1000:
            badges.append(
                {
                    'text': 'Most Popular',
                    'emoji': '🔥',
                    'color': 'linear-gradient(135deg, #f85032 0%, #e73827 100%)',
                }
            )

    # 📸 Largest Collection (by photo count)
    max_photos = max((c.get('total_photos', 0) for c in all_collections), default=0)
    current_photos = collection.get('total_photos', 0)
    if current_photos > 0 and current_photos == max_photos and current_photos >= 30:
        badges.append(
            {
                'text': f'{current_photos} Photos',
                'emoji': '📸',
                'color': 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
            }
        )

    return badges


def render_badges(badges):
    """Render badge HTML elements from badge list

    Args:
        badges: List of badge dicts from get_collection_badges()

    Returns:
        List of Div elements for unpacking with *
    """
    return [
        Div(
            f'{badge["emoji"]} {badge["text"]}',
            cls='collection-badge',
            style=f"""
            position: absolute;
            top: {12 + (i * 40)}px;
            left: 12px;
            background: {badge['color']};
            color: white;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            z-index: 2;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        """,
        )
        for i, badge in enumerate(badges or [])
    ]
