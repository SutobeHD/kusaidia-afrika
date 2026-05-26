"""Generate PNG favicons from a programmatic drawing (no SVG renderer needed)."""
from PIL import Image, ImageDraw, ImageFont
import os

OUT = os.path.dirname(os.path.abspath(__file__)) + "/assets"

TERRACOTTA = (181, 60, 42)
SAFFRON    = (248, 175, 82)
CREAM      = (251, 247, 241)

def draw_icon(size):
    """Draw the favicon at the requested square pixel size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Terrakotta circle
    d.ellipse([0, 0, size - 1, size - 1], fill=TERRACOTTA)

    # Saffron lower-right wedge (Pie-style)
    d.pieslice([0, 0, size - 1, size - 1], start=-15, end=90, fill=SAFFRON)

    # "K" centered
    try:
        # Try a few common serif fonts on Windows
        font_size = int(size * 0.66)
        candidate_fonts = [
            "C:/Windows/Fonts/georgia.ttf",
            "C:/Windows/Fonts/Cambria.ttc",
            "C:/Windows/Fonts/times.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        ]
        font = None
        for fp in candidate_fonts:
            if os.path.exists(fp):
                try:
                    font = ImageFont.truetype(fp, font_size)
                    break
                except Exception:
                    pass
        if font is None:
            font = ImageFont.load_default()
    except Exception:
        font = ImageFont.load_default()

    text = "K"
    bbox = d.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    # Visual baseline correction
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1] - int(size * 0.02)
    d.text((x, y), text, font=font, fill=CREAM)

    return img

# Standard sizes
for size, name in [
    (32,  "favicon-32.png"),
    (192, "favicon-192.png"),
    (180, "apple-touch-icon.png"),
    (512, "favicon-512.png"),
]:
    img = draw_icon(size)
    img.save(f"{OUT}/{name}", optimize=True)
    print(f"wrote {OUT}/{name}  ({size}x{size})")

print("done")
