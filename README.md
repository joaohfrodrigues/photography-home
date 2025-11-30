# Photography Portfolio - joaohfrodrigues.com

A professional photography portfolio website built with FastHTML and Unsplash API, featuring
advanced filtering, responsive design, and comprehensive SEO optimization.

## ✨ Features

### Core Functionality

- 📸 **Dynamic Photo Gallery** - Fetch and display curated photos from Unsplash
- 🔍 **Advanced Filtering** - Search by keywords, filter by year and tags, sort by date/popularity
- 🖼️ **Full-Screen Lightbox** - Immersive photo viewing with EXIF data and navigation
- 📱 **Responsive Design** - Masonry grid layout that adapts to all screen sizes
- ⚡ **Performance Optimized** - Resource preloading, DNS prefetch, deferred scripts

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

- 💾 **Smart Caching** - 30-minute API response caching to optimize performance
- 📊 **Performance Monitoring** - Built-in metrics tracking (load time, TTFB, DOM ready)
- 🎭 **Lazy Loading** - On-demand EXIF data fetching for faster initial loads
- ✅ **Unsplash Compliance** - Full API guideline adherence (attribution, download tracking)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- An [Unsplash](https://unsplash.com/developers) API account (free tier: 50 requests/hour)
- A [Vercel](https://vercel.com) account for deployment

### Local Development

1. **Install dependencies:**

```bash
pip install -r requirements.txt
```

1. **Set up environment variables:**

    Create a `.env` file in the project root:

    ```bash
    UNSPLASH_ACCESS_KEY=your_unsplash_access_key
    ```

    Get your Unsplash API key:
    - Go to <https://unsplash.com/oauth/applications>
    - Create a new application
    - Copy your Access Key

1. **Run the development server:**

```bash
python main.py
```

Visit <http://localhost:5001> to see your site!

## 📸 Customizing Your Portfolio

### Change Photo Query

Edit `main.py` and modify the Unsplash search query:

```python
# Search for specific topics
params = {
    'query': 'your-unsplash-username',  # Your Unsplash photos
    'per_page': 30,
    'order_by': 'popular'
}
```

### Filter by Collection

Use an Unsplash collection ID:

```python
# Instead of /search/photos, use /collections/{id}/photos
url = f"https://api.unsplash.com/collections/your-collection-id/photos"
```

## 🌐 Deploy to Vercel

### Option 1: Using Vercel CLI

1. **Install Vercel CLI:**

```bash
npm i -g vercel
```

1. **Deploy:**

```bash
vercel
```

1. **Add environment variables:** In the Vercel dashboard, go to your project → Settings →
   Environment Variables and add:
    - `UNSPLASH_ACCESS_KEY`
    - `UNSPLASH_USERNAME`

### Option 2: Using GitHub + Vercel

1. Push your code to GitHub
2. Go to [Vercel](https://vercel.com) and import your repository
3. Add environment variables in the project settings
4. Deploy!

### Custom Domain

In Vercel dashboard:

1. Go to your project → Settings → Domains
2. Add `joaohfrodrigues.com`
3. Follow Vercel's instructions to update your DNS settings

## 🎨 Customization

### Update Site Title & Name

Edit `main.py` and change:

```python
H1('JOÃO RODRIGUES'),  # Your name
Title('João Rodrigues | Photography, Data and Development'),  # Browser tab title
```

### Modify Styling

All CSS is embedded in `main.py` within the `Style()` component. Update colors, fonts, and layout as
desired.

### Change Gallery Layout

Modify the CSS grid in the `.gallery-grid` class:

```css
grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
```

## 🛠️ Tech Stack

- **[FastHTML](https://fastht.ml/)** - Modern Python web framework
- **[Unsplash API](https://unsplash.com/developers)** - High-quality photo service with CDN
- **[Vercel](https://vercel.com)** - Serverless deployment platform
- **[httpx](https://www.python-httpx.org/)** - Modern async HTTP client

## 📚 Documentation

- **[ANALYTICS_SETUP.md](./ANALYTICS_SETUP.md)** - Complete guide to setting up Vercel, Google, or
  Plausible analytics
- **[UNSPLASH_PRODUCTION.md](./UNSPLASH_PRODUCTION.md)** - Step-by-step guide to applying for
  Unsplash Production API access
- **[content/pages/README.md](./content/pages/README.md)** - Guide to managing static content pages

## 📁 Project Structure

```text
photography-home/
├── components/          # Reusable UI components
│   ├── pages/          # Full page components
│   └── ui/             # UI components (header, footer, gallery, etc.)
├── content/            # Static content (markdown files)
│   └── pages/          # Markdown pages (about.md, etc.)
├── routes/             # Route handlers
├── services/           # Business logic (API clients, utilities)
│   ├── unsplash.py     # Unsplash API client
│   ├── markdown.py     # Markdown rendering service
│   ├── compliance.py   # Unsplash compliance (download tracking)
│   └── photo_details.py # EXIF data fetching
├── static/             # Static assets
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript files
│   └── favicons/       # Favicon images
├── tests/              # Test files
├── main.py             # Application entry point
├── config.py           # Configuration and environment variables
└── requirements.txt    # Python dependencies
```

### Content Management

Static pages (About, Contact, etc.) are managed as markdown files in `content/pages/`:

- **Easy Updates:** Edit markdown files directly, no code changes needed
- **Metadata:** YAML frontmatter for page title, description, and URL
- **Separation of Concerns:** Content separated from code and styling

### Dynamic vs Static Pages

- **Dynamic Pages:** Gallery page fetches data from Unsplash API
- **Static Pages:** About page and other content loaded from markdown files

## 🎯 Performance

The site is optimized for speed and user experience:

- **Resource Hints:** DNS prefetch, preconnect, and preload for critical assets
- **Deferred Loading:** JavaScript loaded with `defer` attribute
- **Smart Caching:** API responses cached for 30 minutes to minimize requests
- **Lazy EXIF Loading:** Camera metadata fetched on-demand in lightbox
- **Debounced Search:** 300ms delay prevents excessive filtering during typing
- **Loading States:** Visual feedback during async operations

## 🔍 SEO Features

The site includes comprehensive SEO optimization:

- **Meta Tags:** Title, description, keywords, author, viewport
- **Open Graph:** Full OG protocol support for social sharing
- **Twitter Cards:** Optimized for Twitter/X link previews
- **JSON-LD:** Structured data with Person schema
- **Sitemap:** Auto-generated XML sitemap at `/sitemap.xml`
- **Robots.txt:** Proper crawler instructions at `/robots.txt`
- **Favicons:** 4 sizes (16x16, 32x32, ICO, Apple Touch Icon)
- **Semantic HTML:** Proper heading hierarchy and ARIA attributes

## ♿ Accessibility

- **Screen Reader Support:** ARIA labels and semantic HTML
- **Reduced Motion:** Respects `prefers-reduced-motion` user preference
- **Keyboard Navigation:** Arrow keys for lightbox, Escape to close
- **Focus Management:** Proper focus states on interactive elements
- **Color Contrast:** WCAG AA compliant contrast ratios

## 🚀 Next Steps

1. **Apply for Unsplash Production API** - See [UNSPLASH_PRODUCTION.md](./UNSPLASH_PRODUCTION.md)
2. **Set up Analytics** - Follow [ANALYTICS_SETUP.md](./ANALYTICS_SETUP.md)
3. **Add Custom Domain** - Configure in Vercel dashboard
4. **Create About Page** - Add `/about` route with your story
5. **Add Contact Form** - Implement form with email service

## 📝 License

MIT License - feel free to use this for your own photography portfolio!
