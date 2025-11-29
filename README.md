# Photography Portfolio - joaohfrodrigues.com

A minimalist photography portfolio website built with FastHTML, Cloudinary, and deployed on Vercel.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- A [Cloudinary](https://cloudinary.com) account (free tier works great!)
- A [Vercel](https://vercel.com) account for deployment

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables:**
   
   Copy `.env.example` to `.env` and add your Cloudinary credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your Cloudinary details from https://cloudinary.com/console:
   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

3. **Run the development server:**
```bash
python main.py
```

   Visit http://localhost:5001 to see your site!

## 📸 Adding Your Photos

### Upload to Cloudinary

1. Log in to your [Cloudinary dashboard](https://cloudinary.com/console/media_library)
2. Upload your photos to the Media Library
3. Note the "Public ID" of each photo (e.g., `portfolio/sunset-beach`)

### Update the Gallery

Edit `main.py` and replace the `SAMPLE_PHOTOS` list with your Cloudinary public IDs:

```python
SAMPLE_PHOTOS = [
    {'id': 'portfolio/sunset-beach', 'title': 'Sunset Beach'},
    {'id': 'portfolio/mountain-view', 'title': 'Mountain View'},
    # Add more photos...
]
```

## 🌐 Deploy to Vercel

### Option 1: Using Vercel CLI

1. **Install Vercel CLI:**
```bash
npm i -g vercel
```

2. **Deploy:**
```bash
vercel
```

3. **Add environment variables:**
   In the Vercel dashboard, go to your project → Settings → Environment Variables and add:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`

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
Title('João Rodrigues | Photography'),  # Browser tab title
```

### Modify Styling
All CSS is embedded in `main.py` within the `Style()` component. Update colors, fonts, and layout as desired.

### Change Gallery Layout
Modify the CSS grid in the `.gallery-grid` class:
```css
grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
```

## 🛠️ Tech Stack

- **[FastHTML](https://fastht.ml/)** - Modern Python web framework
- **[Cloudinary](https://cloudinary.com)** - Image hosting and optimization
- **[Vercel](https://vercel.com)** - Serverless deployment platform

## 📝 License

MIT License - feel free to use this for your own photography portfolio!
Photography portfolio with Cloudinary and Vercel
