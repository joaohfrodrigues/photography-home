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
