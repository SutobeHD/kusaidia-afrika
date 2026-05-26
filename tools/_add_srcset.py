"""Add srcset+sizes to every <img> that has a responsive variant on disk."""
import re
import glob
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = ROOT + "/assets/images"

# Build a set of stems that have responsive variants
have_variants = set()
for f in glob.glob(SRC_DIR + "/*_480.jpg"):
    stem = os.path.basename(f).replace("_480.jpg", "")
    have_variants.add(stem)

# Pattern matches: <img ... src="<prefix>assets/images/STEM.jpg" ...>
# where <prefix> may be "" or "../"
IMG_RE = re.compile(
    r'<img(?P<head>[^>]*?)src="(?P<prefix>\.\./)?assets/images/(?P<stem>[a-zA-Z0-9._-]+)\.jpg"(?P<tail>[^>]*?)/?>',
    re.DOTALL,
)

def transform(match, page_path):
    head = match.group("head")
    prefix = match.group("prefix") or ""
    stem = match.group("stem")
    tail = match.group("tail")
    full_tag = match.group(0)

    # Skip if already has srcset
    if "srcset" in full_tag:
        return full_tag
    # Skip if no responsive variants exist
    if stem not in have_variants:
        return full_tag

    base = f"{prefix}assets/images/{stem}"
    srcset = (
        f'{base}_480.jpg 480w, '
        f'{base}_800.jpg 800w, '
        f'{base}.jpg 1024w'
    )
    sizes = "(max-width: 600px) 480px, (max-width: 1000px) 800px, 1024px"

    new_tag = (
        f'<img{head}src="{base}.jpg" '
        f'srcset="{srcset}" '
        f'sizes="{sizes}"{tail} />'
    )
    return new_tag

count = 0
img_count = 0
for path in glob.glob("**/*.html", recursive=True):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    matches_before = len(IMG_RE.findall(content))
    new = IMG_RE.sub(lambda m: transform(m, path), content)
    if new != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        count += 1
        # Count how many tags got srcset
        added_here = new.count("srcset") - content.count("srcset")
        img_count += added_here

print(f"Updated {count} HTML files, {img_count} <img> tags got srcset")
