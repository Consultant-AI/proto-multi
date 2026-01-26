# Proto Logo Assets

Generated from HTML/CSS on 2026-01-26.

## Files

### Wordmarks (full text)
- `proto_wordmark_blue_transparent.png` (600×200) - Primary logo, blue on transparent
- `proto_wordmark_white_black.png` (600×200) - White on dark background
- `proto_wordmark_blue_white.png` (600×200) - Blue on white background

### Icons (P monogram)
- `proto_icon_blue_transparent.png` (200×200) - Primary icon
- `proto_icon_white_black.png` (200×200) - White on dark background
- `proto_icon_blue_white.png` (200×200) - Blue on white background

### Lockups (icon + text)
- `proto_lockup_blue_transparent.png` (700×200) - Primary lockup
- `proto_lockup_white_black.png` (700×200) - White on dark background

### Special Formats
- `favicon.png` (64×64) - Favicon for website
- `proto_email_signature.png` (300×80) - Email signature logo
- `proto_social_card.png` (1200×630) - Social media card (og:image, twitter:image)

## Brand Colors

- **Blue (Primary):** #4a9eff
- **White:** #f5f5f5
- **Black:** #0a0a0a
- **Gray (Secondary):** #888888

## Typography

- **Monospace/Code:** JetBrains Mono
- **Display/UI:** Space Grotesk

## Usage Guidelines

### Primary Logo
Use `proto_wordmark_blue_transparent.png` on dark backgrounds for presentations and pitch decks.

### Favicon
Use `favicon.png` (64×64) for website favicons. Most browsers will resize automatically.

### Email Signature
Use `proto_email_signature.png` in your email signature:
```html
<img src="proto_email_signature.png" alt="Proto" width="300" height="80">
```

### Social Media
Use `proto_social_card.png` for Open Graph and Twitter Card meta tags:
```html
<meta property="og:image" content="proto_social_card.png">
<meta name="twitter:image" content="proto_social_card.png">
```

## Regenerating

To regenerate all logos:

1. Edit `logos.html` to modify designs
2. Run: `python3 convert_to_images.py`

This will re-render all PNG files from the HTML/CSS.

## Files

- `logos.html` - HTML/CSS logo designs (view in browser to preview)
- `convert_to_images.py` - Script to convert HTML to PNG images
- `*.png` - Generated logo image files
