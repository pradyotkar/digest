#!/usr/bin/env python3
"""Regenerate daily-digest/index.html — archive of all digests, newest first.

Run after adding a new daily-digest/YYYY-MM-DD.html. Also refreshes latest.html
pointer copy if the newest digest is newer than latest.html.
"""
import os, re, sys

SITE = os.path.expanduser("~/.hermes/website_repo")
DD = os.path.join(SITE, "daily-digest")

def title_date(fn):
    try:
        s = open(os.path.join(DD, fn), encoding="utf-8", errors="replace").read()
        t = re.search(r'<title>Daily AI Digest — ([^<]+)</title>', s)
        return t.group(1) if t else None
    except Exception:
        return None

def story_count(fn):
    try:
        s = open(os.path.join(DD, fn), encoding="utf-8", errors="replace").read()
        return len(re.findall(r'class="story-number"', s)) or len(re.findall(r'<div class="story">', s))
    except Exception:
        return 0

def main():
    dates = sorted(
        (f[:-5] for f in os.listdir(DD) if re.match(r'^\d{4}-\d{2}-\d{2}\.html$', f)),
        reverse=True)
    if not dates:
        print("no digests found"); return 1

    # sync latest.html with newest digest
    newest = dates[0] + ".html"
    latest = os.path.join(DD, "latest.html")
    src = os.path.join(DD, newest)
    if not os.path.exists(latest) or open(latest, 'rb').read() != open(src, 'rb').read():
        import shutil
        shutil.copy2(src, latest)
        print("latest.html synced to", newest)

    rows = []
    for d in dates:
        fn = d + ".html"
        label = title_date(fn) or d
        n = story_count(fn)
        rows.append(f'''      <li><a href="/daily-digest/{fn}"><span class="d">{label}</span><span class="n">{n} stories</span></a></li>''')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Daily AI Digest Archive — Pradyot Kar</title>
<meta name="description" content="Archive of the Daily AI Digest — curated AI news on model releases, pricing, agents and policy, generated automatically for pradykar.com.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://pradykar.com/daily-digest/">
<meta property="og:title" content="Daily AI Digest Archive">
<meta property="og:description" content="Curated AI news — model releases, pricing, agents and policy.">
<meta property="og:image" content="https://pradykar.com/logo.png">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
<style>
  :root {{ --bg:#0d1117; --card:#161b22; --border:#30363d; --text:#c9d1d9; --muted:#8b949e; --accent:#58a6ff; --gold:#d2991d; }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif; background:var(--bg); color:var(--text); line-height:1.6; padding:2rem 1rem; }}
  .container {{ max-width:720px; margin:0 auto; }}
  a.back {{ display:inline-block; margin-bottom:1.2rem; font-size:.85rem; color:var(--accent); text-decoration:none; }}
  header {{ text-align:center; margin-bottom:2.5rem; }}
  header h1 {{ font-size:2rem; font-weight:800; background:linear-gradient(135deg,var(--accent),#bc8cff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }}
  header p {{ color:var(--muted); font-size:.95rem; margin-top:.4rem; }}
  ul {{ list-style:none; }}
  li a {{ display:flex; justify-content:space-between; align-items:center; background:var(--card); border:1px solid var(--border); border-radius:10px; padding:.9rem 1.2rem; margin-bottom:.6rem; color:var(--text); text-decoration:none; transition:border-color .15s; }}
  li a:hover {{ border-color:var(--accent); }}
  li .d {{ font-weight:600; }}
  li .n {{ font-size:.8rem; color:var(--muted); }}
  footer {{ text-align:center; margin-top:2.5rem; color:var(--muted); font-size:.8rem; }}
  footer a {{ color:var(--accent); text-decoration:none; }}
</style>
</head>
<body>
<div class="container">
<a class="back" href="https://pradykar.com/">← pradykar.com</a>
<header>
  <h1>🤖 Daily AI Digest — Archive</h1>
  <p>{len(dates)} editions · generated automatically each morning (5 AM PT) · newest first</p>
</header>
<ul>
{chr(10).join(rows)}
</ul>
<footer>
  <p><a href="/daily-digest/latest.html">View latest digest</a> · <a href="/labs">Labs</a></p>
</footer>
</div>
</body>
</html>'''
    out = os.path.join(DD, "index.html")
    open(out, "w", encoding="utf-8").write(html)
    print(f"index.html written with {len(dates)} entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())