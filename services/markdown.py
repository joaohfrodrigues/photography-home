"""Markdown rendering service for static pages"""

import re
from pathlib import Path

import markdown


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith('---\n'):
        return {}, content

    parts = content.split('---\n', 2)
    if len(parts) < 3:
        return {}, content

    # Simple key: value parsing
    frontmatter = {}
    for line in parts[1].strip().split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip().strip('"').strip("'")

    return frontmatter, parts[2].strip()


def add_external_link_attributes(html_content: str) -> str:
    """Add target='_blank' and rel='noopener noreferrer' to external links."""

    # Match <a href="..."> tags and add attributes if they're external links
    def replace_link(match):
        href = match.group(1)
        # Check if it's an external link (http/https) or mailto
        if href.startswith(('http://', 'https://', 'mailto:')):
            return f'<a href="{href}" target="_blank" rel="noopener noreferrer">'
        return match.group(0)

    return re.sub(r'<a href="([^"]+)">', replace_link, html_content)


def load_markdown_page(page_name: str) -> tuple[dict, str]:
    """
    Load a markdown page from content/pages directory.

    Args:
        page_name: Name of the page (without .md extension)

    Returns:
        Tuple of (metadata dict, HTML content)
    """
    content_dir = Path(__file__).parent.parent / 'content' / 'pages'
    page_path = content_dir / f'{page_name}.md'

    if not page_path.exists():
        msg = f'Page not found: {page_name}'
        raise FileNotFoundError(msg)

    with open(page_path, encoding='utf-8') as f:
        content = f.read()

    metadata, markdown_content = parse_frontmatter(content)
    html_content = markdown.markdown(markdown_content)
    html_content = add_external_link_attributes(html_content)

    return metadata, html_content


def load_blog_article(article_slug: str) -> tuple[dict, str]:
    """
    Load a blog article from content/blog directory (supports nested folders).

    Args:
        article_slug: The slug of the article (e.g., 'home-server-part-1-foundation')

    Returns:
        Tuple of (metadata dict, HTML content)
    """
    content_dir = Path(__file__).parent.parent / 'content' / 'blog'

    # Search for the article recursively by matching slug in frontmatter
    for article_path in content_dir.rglob('*.md'):
        with open(article_path, encoding='utf-8') as f:
            content = f.read()

        metadata, markdown_content = parse_frontmatter(content)

        # Match by slug in frontmatter, or fallback to filename stem
        if metadata.get('slug') == article_slug or article_path.stem == article_slug:
            html_content = markdown.markdown(markdown_content)
            html_content = add_external_link_attributes(html_content)
            return metadata, html_content

    msg = f'Blog article not found: {article_slug}'
    raise FileNotFoundError(msg)


def get_series_articles(series_name: str, *, include_drafts: bool = False) -> list[dict]:
    """
    Get all articles in a specific series, ordered by part number.

    Args:
        series_name: The name of the series (e.g., 'Home Server Setup')

    Returns:
        List of article metadata dicts for the series, ordered by part
    """
    all_articles = get_all_blog_articles(include_drafts=include_drafts)
    series_articles = [a for a in all_articles if a.get('series') == series_name]

    # Sort by part number if available
    series_articles.sort(key=lambda x: int(x.get('part', 999)))

    return series_articles


def get_all_blog_articles(*, include_drafts: bool = False) -> list[dict]:
    """
    Get all blog articles from content/blog directory (including nested folders).

    Returns:
        List of article metadata dicts (slug, title, description, date, series, part, total_parts)
        sorted by date in descending order
    """
    content_dir = Path(__file__).parent.parent / 'content' / 'blog'
    articles = []

    # Recursively find all markdown files
    for page_path in sorted(content_dir.rglob('*.md'), reverse=True):
        with open(page_path, encoding='utf-8') as f:
            content = f.read()

        metadata, _ = parse_frontmatter(content)

        draft_flag = str(metadata.get('draft', '')).strip().lower() in {
            'true',
            '1',
            'yes',
            'y',
            'on',
        }

        if draft_flag and not include_drafts:
            continue

        # Only include files with a title (indicating they're articles)
        if metadata.get('title'):
            article = {
                'slug': metadata.get('slug', page_path.stem),
                'title': metadata.get('title', ''),
                'description': metadata.get('description', ''),
                'date': metadata.get('date', ''),
                'series': metadata.get('series'),
                'part': metadata.get('part'),
                'total_parts': metadata.get('total_parts'),
                'draft': draft_flag,
            }
            articles.append(article)

    # Sort by date (descending) - convert date string to comparable format
    articles.sort(key=lambda x: x['date'], reverse=True)
    return articles
