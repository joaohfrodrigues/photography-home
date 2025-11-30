# Static Content Pages

This directory contains markdown files for static pages that don't require dynamic data.

## Structure

- Each `.md` file represents a page
- Files use YAML frontmatter for metadata (title, description, url)
- Content is written in markdown and rendered to HTML

## Example

```markdown
---
title: 'Page Title'
description: 'Page description for SEO'
url: 'https://joaohfrodrigues.com/page-name'
---

## Section Title

Your content here...
```

## Adding New Pages

1. Create a new `.md` file in this directory
2. Add frontmatter with metadata
3. Write content in markdown
4. Create a corresponding page component in `components/pages/`
5. Add a route in `routes/pages.py`

## Editing Existing Pages

Simply edit the markdown file - no code changes needed!
