#!/usr/bin/env python3
"""
Travel page generator for pradykar.com.
Reads trip data from ~/Downloads/travel-test/ (manual mode) or from
a structured trips config, generates travel.html and /travel/<slug>.html pages.

Usage: python3 scripts/generate_travel.py
"""
import os, sys, re, json, html as html_mod, shutil
from datetime import datetime
from pathlib import Path

REPO_DIR = Path("/tmp/digester_repo")
TRAVEL_DATA_DIR = Path.home() / "Downloads" / "travel-test"
OUTPUT_DIR = REPO_DIR / "travel"
IMAGES_DIR = REPO_DIR / "images" / "travel"

# ── Trip parsing ────────────────────────────────────────────────
def parse_trip_info(filepath):
    """Parse trip-info.txt into title, dates, body."""
    with open(filepath) as f:
        text = f.read()
    lines = text.strip().split("\n")
    title = ""
    dates = ""
    body_lines = []
    mode = "header"
    for line in lines:
        if mode == "header":
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[1].strip()
            elif line.lower().startswith("dates:"):
                dates = line.split(":", 1)[1].strip()
            elif line.strip() == "":
                mode = "body"
        else:
            body_lines.append(line)
    body = "\n".join(body_lines).strip()
    return title, dates, body

def slugify(text):
    """Convert text to URL-safe slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:60]

def scan_trips():
    """Scan TRAVEL_DATA_DIR for trip folders."""
    trips = []
    if not TRAVEL_DATA_DIR.exists():
        return trips
    for item in sorted(TRAVEL_DATA_DIR.iterdir(), reverse=True):
        if item.is_dir():
            info_file = item / "trip-info.txt"
            if info_file.exists():
                title, dates, body = parse_trip_info(info_file)
                slug = slugify(item.name)
                # Collect images
                images = sorted([
                    f.name for f in item.iterdir()
                    if f.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp')
                ])
                # Determine year-month for sorting
                ym = item.name[:7] if re.match(r'\d{4}-\d{2}', item.name) else "9999-99"
                trips.append({
                    "title": title or item.name,
                    "dates": dates or "",
                    "body": body or "",
                    "slug": slug,
                    "folder": item.name,
                    "images": images,
                    "year_month": ym,
                    "cover": images[0] if images else None,
                })
    return trips

# ── HTML templates ──────────────────────────────────────────────

NAV_SHARED = """<nav class="navbar" role="navigation" aria-label="Main navigation">
    <div class="inner">
        <a href="/" class="logo">Pradyot Kar</a>
        <button class="nav-toggle" onclick="document.querySelector('.nav-links').classList.toggle('open')" aria-label="Toggle navigation">☰</button>
        <div class="nav-links">
            <a href="/">Home</a>
            <a href="/experience">Experience</a>
            <a href="/labs">Labs</a>
            <a href="/about">About</a>
            <a href="/travel" class="active">Travel</a>
            <a href="/contact" class="nav-cta">Discuss a Project</a>
        </div>
    </div>
</nav>"""

FOOTER_SHARED = """<footer>
    <div class="inner">
        <div class="links">
            <a href="/">Home</a>
            <a href="/experience">Experience</a>
            <a href="/labs">Labs</a>
            <a href="/about">About</a>

            <a href="https://www.bayshoreintel.com" target="_blank" rel="noopener">Bayshore Intelligence</a>
        </div>
        <span class="copy">© 2026 Pradyot Kar</span>
    </div>
</footer>"""

LIGHTBOX_JS = """
<script>
let lightboxImages = [];
let lightboxIndex = 0;

function openLightbox(imgEl) {
    const gallery = imgEl.closest('.photo-grid') || imgEl.closest('.trip-detail');
    if (!gallery) return;
    const all = gallery.querySelectorAll('.photo-grid img, .gallery-img');
    lightboxImages = Array.from(all).map(im => im.src);
    lightboxIndex = lightboxImages.indexOf(imgEl.src);
    if (lightboxIndex === -1) lightboxIndex = 0;
    showLightbox();
}

function showLightbox() {
    const lb = document.getElementById('lightbox');
    if (!lb) return;
    lb.querySelector('img').src = lightboxImages[lightboxIndex];
    lb.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    updateNav();
}

function closeLightbox() {
    document.getElementById('lightbox').style.display = 'none';
    document.body.style.overflow = '';
}

function changeImage(d) {
    lightboxIndex = (lightboxIndex + d + lightboxImages.length) % lightboxImages.length;
    showLightbox();
}

function updateNav() {
    const prev = document.querySelector('.lb-prev');
    const next = document.querySelector('.lb-next');
    if (prev) prev.style.display = lightboxImages.length > 1 ? 'flex' : 'none';
    if (next) next.style.display = lightboxImages.length > 1 ? 'flex' : 'none';
}

document.addEventListener('keydown', function(e) {
    const lb = document.getElementById('lightbox');
    if (!lb || lb.style.display !== 'flex') return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') changeImage(-1);
    if (e.key === 'ArrowRight') changeImage(1);
});
</script>"""

def build_travel_page(trips):
    """Generate /travel/index.html with vertical timeline."""
    # Group trips by year
    years = {}
    for t in trips:
        y = t["year_month"][:4]
        if y not in years:
            years[y] = []
        years[y].append(t)
    years_sorted = sorted(years.keys(), reverse=True)

    # Build timeline HTML
    if not trips:
        timeline_html = """
        <div class="empty-state">
            <div class="empty-icon">🌍</div>
            <h3>First trip coming soon</h3>
            <p>Travel writeups and photography will appear here once I've put them together.</p>
        </div>"""
    else:
        timeline_parts = []
        for year in years_sorted:
            entries = years[year]
            timeline_parts.append(f'<div class="tl-year-group"><div class="tl-year">{year}</div>')
            for t in entries:
                cover_html = f'<img src="/images/travel/{t["folder"]}/{t["cover"]}" alt="{html_mod.escape(t["title"])}" loading="lazy" class="tl-thumb">' if t["cover"] else '<div class="tl-thumb tl-thumb-placeholder"></div>'
                blurb = html_mod.escape(t["body"][:120] + "...") if len(t["body"]) > 120 else html_mod.escape(t["body"])
                timeline_parts.append(f'''
                <a href="/travel/{t["slug"]}" class="tl-entry">
                    {cover_html}
                    <div class="tl-entry-text">
                        <div class="tl-entry-title">{html_mod.escape(t["title"])}</div>
                        <div class="tl-entry-date">{html_mod.escape(t["dates"])}</div>
                        <div class="tl-entry-blurb">{blurb}</div>
                    </div>
                </a>''')
            timeline_parts.append('</div>')
        timeline_html = "\n".join(timeline_parts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel — Pradyot Kar</title>
    <meta name="description" content="Trip writeups and travel photography by Pradyot Kar.">
    <meta property="og:title" content="Travel — Pradyot Kar">
    <meta property="og:description" content="Travel photography and trip writeups.">
    <meta property="og:image" content="/logo.png">
    <meta property="og:url" content="https://pradykar.com/travel">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=swap" rel="stylesheet">
    <style>
        :root{{--ink:#0b1220;--slate:#5f6b7a;--muted:#7b8796;--border:#dfe5ec;--surface:#f5f7fa;--white:#ffffff;--max-width:1200px;--radius:8px;--blue:#245eea;--shadow-md:0 4px 12px rgba(0,0,0,0.08)}}
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Inter',sans-serif;background:var(--white);color:var(--ink);font-size:16px;line-height:1.6;padding-top:64px}}
        a{{color:var(--blue);text-decoration:none}}
        .navbar{{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(255,255,255,0.97);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);height:64px}}
        .navbar .inner{{max-width:var(--max-width);margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:100%}}
        .navbar .logo{{font-weight:700;font-size:18px;color:var(--ink)}}
        .nav-links{{display:flex;align-items:center;gap:2px}}
        .nav-links a{{color:var(--slate);font-size:14px;font-weight:500;padding:8px 14px;border-radius:var(--radius);transition:all .15s}}
        .nav-links a:hover{{color:var(--ink);background:var(--surface)}}
        .nav-links a.active{{color:var(--ink);font-weight:600}}
        .nav-cta{{background:var(--blue);color:var(--white)!important;padding:8px 20px!important;border-radius:var(--radius);font-weight:600}}
        .nav-toggle{{display:none;background:none;border:none;font-size:22px;color:var(--ink);cursor:pointer;padding:4px}}
        @media(max-width:768px){{.nav-toggle{{display:block}}.nav-links{{display:none;position:absolute;top:64px;left:0;right:0;background:var(--white);flex-direction:column;padding:12px 24px 20px;border-bottom:1px solid var(--border);box-shadow:var(--shadow-md)}}.nav-links.open{{display:flex}}.nav-links a{{padding:10px 8px;font-size:15px}}.nav-cta{{margin-top:8px;text-align:center}}}}
        .page-header{{padding:100px 24px 40px;text-align:center;max-width:600px;margin:0 auto}}
        .page-header h1{{font-size:36px;font-weight:800;margin-bottom:8px;letter-spacing:-0.5px}}
        .page-header p{{color:var(--slate);font-size:15px}}
        .travel-section{{padding:0 24px 80px;max-width:700px;margin:0 auto}}
        .tl-year-group{{margin-bottom:40px}}
        .tl-year{{font-size:20px;font-weight:700;color:var(--ink);margin-bottom:16px;padding-bottom:8px;border-bottom:2px solid var(--border)}}
        .tl-entry{{display:flex;gap:16px;padding:16px;border-radius:var(--radius);margin-bottom:12px;transition:all .15s;border:1px solid transparent;color:var(--ink)}}
        .tl-entry:hover{{background:var(--surface);border-color:var(--border)}}
        .tl-thumb{{width:80px;height:80px;border-radius:8px;object-fit:cover;flex-shrink:0;background:var(--surface)}}
        .tl-thumb-placeholder{{width:80px;height:80px;border-radius:8px;background:var(--surface);flex-shrink:0}}
        .tl-entry-text{{flex:1;min-width:0}}
        .tl-entry-title{{font-size:16px;font-weight:700;margin-bottom:2px}}
        .tl-entry-date{{font-size:12px;color:var(--blue);font-weight:600;margin-bottom:4px}}
        .tl-entry-blurb{{font-size:14px;color:var(--slate);line-height:1.5}}
        .empty-state{{text-align:center;padding:80px 24px}}
        .empty-icon{{font-size:48px;margin-bottom:16px}}
        .empty-state h3{{font-size:22px;font-weight:700;margin-bottom:8px}}
        .empty-state p{{color:var(--slate);font-size:15px;max-width:400px;margin:0 auto}}
        footer{{padding:48px 0;border-top:1px solid var(--border)}}
        footer .inner{{max-width:var(--max-width);margin:0 auto;padding:0 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}}
        footer .links{{display:flex;gap:20px;flex-wrap:wrap}}
        footer a{{color:var(--slate);font-size:14px}}
        footer a:hover{{color:var(--ink)}}
        footer .copy{{color:var(--muted);font-size:13px}}
        @media(max-width:640px){{.tl-entry{{flex-direction:column}}.tl-thumb{{width:100%;height:160px}}.page-header h1{{font-size:28px}}}}
        @media(prefers-reduced-motion:reduce){{*{{animation-duration:0.01ms!important;transition-duration:0.01ms!important}}}}
    </style>
</head>
<body>
{NAV_SHARED}
<div class="page-header">
    <h1>Travel</h1>
    <p>Documenting the places I've been, one trip at a time.</p>
</div>
<div class="travel-section">
{timeline_html}
</div>
{FOOTER_SHARED}
<script>
document.querySelectorAll('.nav-toggle').forEach(b=>{{b.addEventListener('click',()=>document.querySelector('.nav-links').classList.toggle('open'))}})
document.addEventListener('click',function(e){{var n=document.querySelector('.nav-links'),t=document.querySelector('.nav-toggle');t&&!t.contains(e.target)&&!n.contains(e.target)&&n.classList.remove('open')}})
</script>
</body>
</html>"""
    
    # Ensure clean output
    html = html.replace("{NAV_SHARED}", NAV_SHARED).replace("{FOOTER_SHARED}", FOOTER_SHARED)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (REPO_DIR / "travel.html").write_text(html)
    print(f"✅ Generated travel/index.html — {len(trips)} trip(s)")

def build_trip_page(trip):
    """Generate /travel/<slug>.html for a single trip."""
    # Build gallery grid
    gallery_rows = []
    for img in trip["images"]:
        src = f"/images/travel/{trip['folder']}/{img}"
        gallery_rows.append(f'<img src="{src}" alt="{html_mod.escape(trip["title"])}" onclick="openLightbox(this)" class="gallery-img" loading="lazy">')
    
    gallery_html = "\n            ".join(gallery_rows) if gallery_rows else '<p style="color:var(--slate);font-size:14px">No photos yet.</p>'
    
    body_html = html_mod.escape(trip["body"]).replace("\n", "<br>\n")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_mod.escape(trip["title"])} — Travel · Pradyot Kar</title>
    <meta name="description" content="{html_mod.escape(trip["title"][:150])} — trip writeup and photos by Pradyot Kar.">
    <meta property="og:title" content="{html_mod.escape(trip["title"])} — Pradyot Kar">
    <meta property="og:description" content="Trip writeup and photos.">
    <meta property="og:image" content="/images/travel/{trip['folder']}/{trip['cover'] or ''}">
    <meta property="og:url" content="https://pradykar.com/travel/{trip['slug']}">
    <meta name="twitter:card" content="summary_large_image">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500&display=swap" rel="stylesheet">
    <style>
        :root{{--ink:#0b1220;--slate:#5f6b7a;--muted:#7b8796;--border:#dfe5ec;--surface:#f5f7fa;--white:#ffffff;--max-width:1200px;--radius:8px;--blue:#245eea;--shadow-md:0 4px 12px rgba(0,0,0,0.08);--shadow-lg:0 8px 30px rgba(0,0,0,0.15)}}
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:'Inter',sans-serif;background:var(--white);color:var(--ink);font-size:16px;line-height:1.6;padding-top:64px}}
        a{{color:var(--blue);text-decoration:none}}
        .navbar{{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(255,255,255,0.97);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);height:64px}}
        .navbar .inner{{max-width:var(--max-width);margin:0 auto;padding:0 24px;display:flex;align-items:center;justify-content:space-between;height:100%}}
        .navbar .logo{{font-weight:700;font-size:18px;color:var(--ink)}}
        .nav-links{{display:flex;align-items:center;gap:2px}}
        .nav-links a{{color:var(--slate);font-size:14px;font-weight:500;padding:8px 14px;border-radius:var(--radius);transition:all .15s}}
        .nav-links a:hover{{color:var(--ink);background:var(--surface)}}
        .nav-links a.active{{color:var(--ink);font-weight:600}}
        .nav-cta{{background:var(--blue);color:var(--white)!important;padding:8px 20px!important;border-radius:var(--radius);font-weight:600}}
        .nav-toggle{{display:none;background:none;border:none;font-size:22px;color:var(--ink);cursor:pointer;padding:4px}}
        @media(max-width:768px){{.nav-toggle{{display:block}}.nav-links{{display:none;position:absolute;top:64px;left:0;right:0;background:var(--white);flex-direction:column;padding:12px 24px 20px;border-bottom:1px solid var(--border);box-shadow:var(--shadow-md)}}.nav-links.open{{display:flex}}.nav-links a{{padding:10px 8px;font-size:15px}}.nav-cta{{margin-top:8px;text-align:center}}}}
        .page-header{{padding:100px 24px 0;max-width:700px;margin:0 auto}}
        .page-header a{{font-size:14px;font-weight:500;color:var(--slate);display:inline-block;margin-bottom:16px}}
        .page-header a:hover{{color:var(--blue)}}
        .page-header h1{{font-size:32px;font-weight:800;margin-bottom:4px;letter-spacing:-0.5px}}
        .page-header .trip-dates{{font-size:14px;color:var(--blue);font-weight:600;margin-bottom:24px}}
        .trip-body{{padding:0 24px 40px;max-width:700px;margin:0 auto}}
        .trip-body .writeup{{font-family:'Source Serif 4',Georgia,serif;font-size:17px;line-height:1.8;color:var(--slate);margin-bottom:40px}}
        .photo-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding:0 24px 80px;max-width:900px;margin:0 auto}}
        .photo-grid img{{width:100%;aspect-ratio:4/3;object-fit:cover;border-radius:var(--radius);cursor:pointer;transition:opacity .15s}}
        .photo-grid img:hover{{opacity:0.85}}
        @media(max-width:640px){{.photo-grid{{grid-template-columns:repeat(2,1fr)}}.page-header h1{{font-size:26px}}}}
        /* Lightbox */
        .lightbox{{display:none;position:fixed;top:0;left:0;right:0;bottom:0;z-index:1000;background:rgba(0,0,0,0.92);justify-content:center;align-items:center}}
        .lightbox img{{max-width:90vw;max-height:85vh;object-fit:contain;border-radius:4px}}
        .lb-close{{position:absolute;top:20px;right:24px;color:#fff;font-size:28px;cursor:pointer;background:none;border:none;z-index:1001}}
        .lb-nav{{position:absolute;top:50%;transform:translateY(-50%);color:#fff;font-size:36px;cursor:pointer;background:rgba(255,255,255,0.08);border:none;padding:16px 12px;border-radius:8px;transition:background .15s;z-index:1001}}
        .lb-nav:hover{{background:rgba(255,255,255,0.15)}}
        .lb-prev{{left:16px}}
        .lb-next{{right:16px}}
        .lb-counter{{position:absolute;bottom:20px;color:rgba(255,255,255,0.6);font-size:13px;z-index:1001}}
        footer{{padding:48px 0;border-top:1px solid var(--border)}}
        footer .inner{{max-width:var(--max-width);margin:0 auto;padding:0 24px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px}}
        footer .links{{display:flex;gap:20px;flex-wrap:wrap}}
        footer a{{color:var(--slate);font-size:14px}}
        footer a:hover{{color:var(--ink)}}
        footer .copy{{color:var(--muted);font-size:13px}}
        @media(max-width:640px){{footer .inner{{flex-direction:column;text-align:center}}}}
        @media(prefers-reduced-motion:reduce){{*{{animation-duration:0.01ms!important}}}}
    </style>
</head>
<body>
{NAV_SHARED}
<div class="page-header">
    <a href="/travel">← Back to Travel</a>
    <h1>{html_mod.escape(trip["title"])}</h1>
    <div class="trip-dates">{html_mod.escape(trip["dates"])}</div>
</div>
<div class="trip-body">
    <div class="writeup">{body_html}</div>
</div>
<div class="photo-grid">
    {gallery_html}
</div>

<!-- Lightbox -->
<div class="lightbox" id="lightbox" onclick="closeLightbox()" role="dialog" aria-modal="true">
    <button class="lb-close" onclick="closeLightbox()" aria-label="Close">✕</button>
    <button class="lb-nav lb-prev" onclick="event.stopPropagation();changeImage(-1)" aria-label="Previous">‹</button>
    <button class="lb-nav lb-next" onclick="event.stopPropagation();changeImage(1)" aria-label="Next">›</button>
    <img src="" alt="" onclick="event.stopPropagation()">
    <div class="lb-counter" id="lb-counter"></div>
</div>

{FOOTER_SHARED}
{LIGHTBOX_JS}
<script>
document.querySelectorAll('.nav-toggle').forEach(b=>{{b.addEventListener('click',()=>document.querySelector('.nav-links').classList.toggle('open'))}})
document.addEventListener('click',function(e){{var n=document.querySelector('.nav-links'),t=document.querySelector('.nav-toggle');t&&!t.contains(e.target)&&!n.contains(e.target)&&n.classList.remove('open')}})

// Lightbox: update counter
const origShow = showLightbox;
showLightbox = function() {{
    origShow();
    const c = document.getElementById('lb-counter');
    if (c) c.textContent = (lightboxIndex + 1) + ' / ' + lightboxImages.length;
}};
</script>
</body>
</html>"""
    
    html = html.replace("{NAV_SHARED}", NAV_SHARED).replace("{FOOTER_SHARED}", FOOTER_SHARED).replace("{LIGHTBOX_JS}", LIGHTBOX_JS)
    
    trip_dir = OUTPUT_DIR / trip["slug"]
    trip_dir.mkdir(parents=True, exist_ok=True)
    (trip_dir / "index.html").write_text(html)
    (REPO_DIR / "travel" / f"{trip['slug']}.html").write_text(html)
    print(f"✅ Generated /travel/{trip['slug']}/ — {len(trip['images'])} photo(s)")

def copy_images(trip):
    """Copy trip images from source to repo."""
    src_dir = TRAVEL_DATA_DIR / trip["folder"]
    dst_dir = IMAGES_DIR / trip["folder"]
    dst_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for img in trip["images"]:
        src = src_dir / img
        dst = dst_dir / img
        if src.exists():
            shutil.copy2(src, dst)
            count += 1
    print(f"  Copied {count} image(s) to {dst_dir}")

# ── Main ────────────────────────────────────────────────────────
def main():
    trips = scan_trips()
    if trips:
        # Sort by year_month descending (newest first)
        trips.sort(key=lambda t: t["year_month"], reverse=True)
        for t in trips:
            copy_images(t)
            build_trip_page(t)
        build_travel_page(trips)
    else:
        print("No trips found in ~/Downloads/travel-test/")
        build_travel_page([])  # empty state
        print("Generated travel page with empty state")
    
    print("\nDone. Run: cd /tmp/digester_repo && git add -A && git commit ... && git push")

if __name__ == "__main__":
    main()
