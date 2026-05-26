"""Add Open Graph + Twitter Card tags to every HTML page (anchored at </head>)."""
import re
import glob
import os

BASE_URL = "https://sutobehd.github.io/kusaidia-afrika/"
SITE_NAME = "Kusaidia Afrika"

title_re = re.compile(r"<title>(.*?)</title>", re.DOTALL)
desc_re = re.compile(r'<meta\s+name="description"\s+content="([^"]*)"\s*/?>')
head_close_re = re.compile(r'\n*</head>')
theme_color_present = re.compile(r'theme-color')

count = 0
for path in glob.glob("**/*.html", recursive=True):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if "og:title" in content:
        continue

    title_m = title_re.search(content)
    title = (title_m.group(1) if title_m else "Kusaidia Afrika").strip()
    title = title.replace("&shy;", "").replace("&nbsp;", " ").strip()

    desc_m = desc_re.search(content)
    desc = (desc_m.group(1) if desc_m else
            "Kusaidia Afrika - Helfen in Afrika e.V.").strip()

    rel = path.replace("\\", "/")
    page_url = BASE_URL + rel
    og_image_url = BASE_URL + "assets/og-image.jpg"

    lang_m = re.search(r'<html lang="(\w+)"', content)
    lang = lang_m.group(1) if lang_m else "de"
    locale = "de_DE" if lang == "de" else "en_US"

    def esc(s):
        return s.replace('"', "&quot;").replace("\n", " ").strip()

    theme_color_line = "" if theme_color_present.search(content) else \
        '  <meta name="theme-color" content="#b53c2a">\n'

    og_block = f"""
  {theme_color_line.strip()}
  <!-- Open Graph / social preview -->
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="{SITE_NAME}">
  <meta property="og:locale" content="{locale}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{page_url}">
  <meta property="og:image" content="{og_image_url}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{og_image_url}">
</head>"""

    # Replace closing </head> with the block (which contains </head>)
    new, n = head_close_re.subn(og_block, content, count=1)
    if n > 0 and new != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
        count += 1

print(f"Added OG + theme-color to {count} files")
