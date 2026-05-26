"""Generate multiple-size variants of every image in assets/images/."""
from PIL import Image
import os
import glob

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = ROOT + "/assets/images"
OUT_DIR = SRC_DIR  # output alongside originals (suffix _480 / _800)

SIZES = [480, 800]  # original keeps its native size (typically 1024)

count = 0
for src in glob.glob(SRC_DIR + "/*.jpg"):
    base = os.path.basename(src)
    name, ext = os.path.splitext(base)
    # Skip already-generated variants
    if name.endswith(("_480", "_800")):
        continue

    try:
        img = Image.open(src).convert("RGB")
    except Exception as e:
        print(f"  skip (cannot open) {base}: {e}")
        continue

    w, h = img.size
    for target_w in SIZES:
        if target_w >= w:
            continue  # do not upscale
        ratio = target_w / w
        new_h = int(h * ratio)
        small = img.resize((target_w, new_h), Image.LANCZOS)
        out_path = f"{SRC_DIR}/{name}_{target_w}.jpg"
        small.save(out_path, format="JPEG", quality=82, optimize=True, progressive=True)
        count += 1

print(f"Generated {count} responsive variants")
print()
print("Examples:")
for f in sorted(glob.glob(SRC_DIR + "/hero-mbulu*.jpg")):
    sz = os.path.getsize(f) // 1024
    print(f"  {os.path.basename(f):<40}  {sz} KB")
