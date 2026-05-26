"""Generate a 1200x630 Open Graph card image for social-media previews."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ROOT  = os.path.dirname(os.path.abspath(__file__))
HERO  = ROOT + "/assets/images/hero-mbulu.jpg"
OUT   = ROOT + "/assets/og-image.jpg"

W, H = 1200, 630
TERRACOTTA = (181, 60, 42)
SAFFRON    = (248, 175, 82)
CREAM      = (251, 247, 241)
INK        = (31, 26, 22)

# Load and crop the hero
hero = Image.open(HERO).convert("RGB")
ar_target = W / H
ar_source = hero.size[0] / hero.size[1]
if ar_source > ar_target:
    new_h = hero.size[1]
    new_w = int(new_h * ar_target)
    x = (hero.size[0] - new_w) // 2
    hero = hero.crop((x, 0, x + new_w, new_h))
else:
    new_w = hero.size[0]
    new_h = int(new_w / ar_target)
    y = (hero.size[1] - new_h) // 4  # crop from upper half
    hero = hero.crop((0, y, new_w, y + new_h))
hero = hero.resize((W, H), Image.LANCZOS)

# Darken / saturate-down for legibility
overlay = Image.new("RGBA", (W, H), (31, 26, 22, 130))
img = hero.convert("RGBA")
img = Image.alpha_composite(img, overlay)

# Terrakotta band on bottom-left
band_h = 200
band = Image.new("RGBA", (W, band_h), TERRACOTTA + (235,))
img.paste(band, (0, H - band_h), band)

# Saffron thin strip above the band
strip = Image.new("RGBA", (W, 6), SAFFRON + (255,))
img.paste(strip, (0, H - band_h - 6), strip)

d = ImageDraw.Draw(img)

# Brand wordmark
def load_font(paths, size):
    for fp in paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

font_serif_bold = load_font([
    ROOT + "/assets/fonts/cormorant-garamond-v21-latin-600.woff2",  # may not work
    "C:/Windows/Fonts/Cambria.ttc",
    "C:/Windows/Fonts/georgia.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
], 92)

font_sans = load_font([
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
], 28)

font_serif_italic = load_font([
    "C:/Windows/Fonts/cambriai.ttf",
    "C:/Windows/Fonts/georgiai.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
], 36)

# Eyebrow tag
d.text((60, 60), "HELFEN IN AFRIKA  ·  SEIT 2001",
       font=font_sans, fill=SAFFRON)

# Main wordmark
d.text((60, H - band_h + 36), "Kusaidia Afrika",
       font=font_serif_bold, fill=CREAM)

# Tagline
d.text((60, H - band_h + 140), "»Kusaidia« — Suaheli für Helfen.",
       font=font_serif_italic, fill=(250, 227, 166))

# Save as JPG (smaller, social-platform-friendly)
img.convert("RGB").save(OUT, format="JPEG", quality=87, optimize=True)
print(f"wrote {OUT}  ({W}x{H})")
