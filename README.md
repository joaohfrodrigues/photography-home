# Photography Portfolio - joaohfrodrigues.com

A professional photography portfolio website built with FastHTML, featuring a local SQLite database
synchronized with Unsplash API, advanced filtering, responsive design, and comprehensive SEO
optimization.

Implemented with vibe coding on VSCode and Copilot, alongside inputs from Gemini as well.

## ✨ Features

### Core Functionality

- 📸 **Local Database** - SQLite database with photos synced from Unsplash via ETL pipeline
- 🔍 **Advanced Search** - Full-text search across titles, descriptions, photographer names, tags,
    and locations
- 🏷️ **Collection Management** - Browse photos organized by collections with many-to-many
    relationships
- 🖼️ **Full-Screen Lightbox** - Immersive photo viewing with EXIF data, statistics, and keyboard
    navigation
- 📱 **Responsive Design** - Masonry grid layout that adapts to all screen sizes
- ⚡ **Performance Optimized** - Database queries with proper indexing, resource preloading,
    deferred scripts

### Data Architecture

- 💾 **SQLite Database** - Local database with photos, collections, and junction tables
- 🔄 **ETL Pipeline** - Automated sync from Unsplash API with optimized API calls (16 per sync)
- 📊 **Rich Metadata** - EXIF data, location coordinates, view/download statistics
- 🔗 **Collections** - Proper many-to-many relationships between photos and collections
- 🔎 **Full-Text Search** - FTS5 virtual table for fast content search

### SEO & Discovery

- 🔎 **Comprehensive SEO** - Meta tags, Open Graph, Twitter Cards, JSON-LD structured data
- 🗺️ **Dynamic Sitemap** - Auto-generated XML sitemap for search engines
- 🤖 **Robots.txt** - Proper crawler instructions
- 🎯 **Rich Snippets** - Schema.org Person markup for enhanced search results

### User Experience

- ⏳ **Loading States** - Visual feedback during async operations
- 🎨 **Custom Error Pages** - Styled 404 and 500 error handlers
- ♿ **Accessibility** - Screen reader support, reduced motion support, semantic HTML
- 🔗 **Social Integration** - Footer links to Instagram and Unsplash profiles

### Technical Excellence

- 💾 **Database-Driven** - Fast queries from local SQLite instead of API calls
- 🔄 **Automated ETL** - GitHub Actions workflow syncs data from Unsplash daily
- 📊 **Comprehensive Testing** - Pytest suite with anonymized fixtures
- 🎭 **Strategic EXIF Fetching** - Only fetch detailed metadata for featured photos (2 per sync)
- ✅ **Unsplash Compliance** - Full API guideline adherence (attribution, download tracking)
- 🎯 **CI/CD Pipeline** - Pre-commit linting, pytest, and pip-audit security check

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- An [Unsplash](https://unsplash.com/developers) API account (free tier: 50 requests/hour)
- GitHub account (for automated syncing via Actions)

### Local Development

1. **Clone and install dependencies:**

```bash
git clone https://github.com/joaohfrodrigues/photography-home.git
cd photography-home
pip install .          # runtime deps
pip install '.[dev]'   # add lint/test tools
```

1. **Set up environment variables:**

    Create a `.env` file in the project root:

    ```bash
    UNSPLASH_ACCESS_KEY=your_unsplash_access_key
    UNSPLASH_USERNAME=your_unsplash_username
    ```

    Get your Unsplash API key:
    - Go to <https://unsplash.com/oauth/applications>
    - Create a new application
    - Copy your Access Key

1. **Sync photos from Unsplash:**

```bash
python backend/etl.py
```

This will:

- Fetch your photos and collections from Unsplash
- Extract EXIF data for featured photos
- Store everything in `data/photos.db`
- Use only ~16 API calls (well within the 50/hour limit)

1. **Run the development server:**

```bash
python main.py
```

Visit <http://localhost:5001> to see your site!

## 📸 Database & ETL

### Database Schema

The application uses SQLite with three main tables:

- **photos** - Photo metadata (46 fields including EXIF, location, statistics)
- **collections** - Collection metadata (title, description, dates)
- **photo_collections** - Junction table for many-to-many relationships

### ETL Pipeline

Run the ETL manually:

```bash
python backend/etl.py              # Full sync
python backend/etl.py --test       # Test mode (5 photos per collection)
python backend/etl.py --max-photos 10  # Limit photos per collection
```

The ETL optimizes API usage:

1. Fetches user photos with statistics (5 calls)
2. Fetches EXIF for 2 featured photos (2 calls)
3. Fetches collections metadata (1 call)
4. Links photos to collections (8 calls)

**Total: 16 API calls** per sync (well within 50/hour limit)

### Automated Sync

GitHub Actions workflow (`.github/workflows/etl.yaml`) runs daily to:

- Sync new photos from Unsplash
- Update statistics for existing photos
- Commit the updated database
- Deploy to production

See `backend/README.md` for detailed ETL documentation.

## 🌐 Deploy to Vercel

1. Push your code to GitHub
2. Go to [Vercel](https://vercel.com) and import your repository
3. Add environment variables in the project settings
4. Deploy!

The GitHub Actions workflow will automatically sync new photos daily and redeploy.

## 🎨 Customization

### Update Site Information

Edit the following files:

- `components/ui/header.py` - Site title and navigation
- `components/ui/footer.py` - Social links and footer text
- `content/pages/about.md` - About page content

### Modify Styling

CSS is modularized in `static/css/`:

- `base.css` - Global styles and variables
- `layout.css` - Grid and layout
- `components.css` - UI component styles
- `gallery.css` - Photo gallery specific styles
- `lightbox.css` - Lightbox modal styles
- `filters.css` - Search and filter styles
- `responsive.css` - Media queries
- `animations.css` - Transitions and animations

### Change Gallery Layout

Modify `static/css/gallery.css`:

```css
.gallery-grid {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
}
```

## 🛠️ Tech Stack

- **[FastHTML](https://fastht.ml/)** - Modern Python web framework
- **[SQLite](https://www.sqlite.org/)** - Embedded database with FTS5 full-text search
- **[Unsplash API](https://unsplash.com/developers)** - High-quality photo service with CDN
- **[pytest](https://pytest.org/)** - Testing framework with 29 passing tests
- **[Ruff](https://docs.astral.sh/ruff/)** - Fast Python linter and formatter
- **[Vercel](https://vercel.com)** - Serverless deployment platform
- **[GitHub Actions](https://github.com/features/actions)** - CI/CD for testing and deployment

## 📚 Documentation

### Main Documentation

- **[backend/README.md](./backend/README.md)** - Database schema and ETL pipeline details
- **[tests/fixtures/README.md](./tests/fixtures/README.md)** - Test data and fixture documentation
- **[content/pages/README.md](./content/pages/README.md)** - Managing static content pages

### Additional Guides

- **[data/README.md](./data/README.md)** - Database file information
- **[.github/workflows/dev.yaml](./.github/workflows/dev.yaml)** - CI pipeline (pre-commit, pytest, pip-audit)

## 📁 Project Structure

```text
photography-home/
├── .github/
│   └── workflows/       # CI/CD pipelines
│       ├── dev.yaml    # Linting, testing, type checking
│       └── sync-photos.yaml  # Daily photo sync
├── backend/            # Database and ETL
│   ├── database.py     # Schema and operations
│   ├── db_service.py   # Query layer
│   └── etl.py          # Unsplash sync pipeline
├── components/         # Reusable UI components
│   ├── pages/         # Full page components
│   └── ui/            # Header, footer, gallery, lightbox
├── content/           # Static content
│   └── pages/         # Markdown pages (about.md)
├── data/              # SQLite database
│   └── photos.db      # Local photo database
├── routes/            # API and page routes
├── static/            # Static assets
│   ├── css/          # Modular stylesheets
│   ├── js/           # JavaScript (lightbox, filters)
│   └── favicons/     # Site icons
├── tests/             # Test suite (29 tests)
│   ├── fixtures/     # Anonymized test data
│   ├── test_database.py
│   ├── test_db_service.py
│   └── test_etl_transform.py
├── main.py            # Application entry point
├── config.py          # Configuration
└── requirements.txt   # Dependencies
```

## 🎯 Performance

The site is optimized for speed and user experience:

- **Local Database:** Fast queries from SQLite instead of API calls
- **FTS5 Search:** Full-text search with proper indexing
- **Resource Hints:** DNS prefetch, preconnect, and preload for critical assets
- **Deferred Loading:** JavaScript loaded with `defer` attribute
- **Loading States:** Visual feedback during async operations
- **Optimized Images:** Unsplash CDN with automatic format detection and resizing

## 🔍 SEO Features

The site includes comprehensive SEO optimization:

- **Meta Tags:** Title, description, keywords, author, viewport
- **Open Graph:** Full OG protocol support for social sharing
- **Twitter Cards:** Optimized for Twitter/X link previews
- **JSON-LD:** Structured data with Person schema
- **Sitemap:** Auto-generated XML sitemap at `/sitemap.xml`
- **Robots.txt:** Proper crawler instructions at `/robots.txt`
- **Favicons:** Multiple sizes for all devices
- **Semantic HTML:** Proper heading hierarchy and ARIA attributes

## ♿ Accessibility

- **Screen Reader Support:** ARIA labels and semantic HTML
- **Reduced Motion:** Respects `prefers-reduced-motion` user preference
- **Keyboard Navigation:** Arrow keys for lightbox, Escape to close, Tab navigation
- **Focus Management:** Proper focus states on interactive elements
- **Color Contrast:** WCAG AA compliant contrast ratios
- **Alt Text:** All images have descriptive alternative text

## 🧪 Testing

The project includes a pytest suite covering database schema, service layer queries, ETL transforms, and anonymized fixtures.

Run tests:

```bash
pytest -v                    # All tests
pytest tests/test_etl_transform.py -v  # ETL tests only
```

## 🔐 Security

- **Environment Variables:** API keys stored in `.env` (not committed)
- **Input Sanitization:** All user inputs sanitized
- **Dependency Updates:** Dependabot for automated security updates
- **No Secrets in Code:** All sensitive data in environment variables
- **pip-audit:** Dependency vulnerability scan in CI

## 🚀 Replication steps

1. **Customize Your Portfolio**
    - Update `components/ui/header.py` with your name
    - Edit `content/pages/about.md` with your story
    - Modify `components/ui/footer.py` with your social links

2. **Set Up Automated Syncing**
    - Configure GitHub Actions secrets for UNSPLASH_ACCESS_KEY
    - Enable workflows in your GitHub repository
    - Photos will sync automatically every day

3. **Deploy to Production**
    - Connect your GitHub repo to Vercel
    - Add environment variables in Vercel dashboard
    - Deploy and get your custom domain

4. **Monitor and Maintain**
    - Check GitHub Actions logs for sync status
    - Monitor database size (SQLite is very efficient)
    - Update EXIF fetch count in `backend/etl.py` if needed

## 📝 License

MIT License - feel free to use this for your own photography portfolio!
