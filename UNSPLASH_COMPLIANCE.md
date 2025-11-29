# Unsplash API Production Compliance

This application is fully compliant with Unsplash API Guidelines for production apps.

## ✅ Compliance Checklist

### 1. Hotlink Photos ✅
- Photos are hotlinked directly from Unsplash using the original `urls.raw` endpoint
- No copying or re-hosting of images on our servers
- Implementation: `services/unsplash.py` - uses `photo['urls']['raw']`

### 2. Trigger Downloads ✅
- Download events are triggered when users view photos in lightbox
- Uses Unsplash's `download_location` endpoint
- Implementation: 
  - `services/compliance.py` - `trigger_download()` function
  - `main.py` - `/api/trigger-download` endpoint
  - `components/scripts.py` - Triggers on lightbox open

### 3. App Name & Identity ✅
- App name: "João Rodrigues Photography Portfolio"
- Visually distinct from Unsplash
- Does not use "Unsplash" in the name
- Custom branding and design

### 4. Attribution ✅
- **Photographer Attribution**: Full name displayed and linked
- **Unsplash Attribution**: "Unsplash" linked to unsplash.com
- **Format**: "Photo by [Photographer Name] on Unsplash"
- **Locations**:
  - Hover overlay on each gallery image
  - Prominent section in lightbox modal
  - All links open in new tabs with proper rel attributes

## Implementation Details

### Attribution Display
```
Gallery: Hover attribution badge (top-right)
Lightbox: Attribution section with clickable links
Format: "Photo by [Name] on Unsplash"
```

### Download Tracking
- Automatically triggered when user opens lightbox
- Logged server-side for monitoring
- Complies with Unsplash analytics requirements

### Photo URLs
- Using `urls.raw` for maximum quality
- Direct hotlinking from Unsplash CDN
- No intermediate caching (Cloudinary disabled for compliance)

## API Rate Limits
- Free tier: 50 requests/hour
- Current usage: ~2 requests/hour (with 30-min cache)
- Well within limits ✅

## Production Checklist
- [x] Hotlink from Unsplash CDN
- [x] Trigger download events
- [x] Proper attribution on all photos
- [x] Link photographer and Unsplash
- [x] Distinct visual identity
- [x] Accurate app description
- [x] No Unsplash logo usage
- [x] Different name from "Unsplash"
