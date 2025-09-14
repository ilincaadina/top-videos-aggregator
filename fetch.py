import os, requests, html, json
from datetime import datetime

SITE_TITLE = "Top Videos & News"
OUT_HTML = "index.html"

# ---------- YouTube: Most Popular ----------
def fetch_youtube(api_key, region="RO", max_results=15):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics,contentDetails",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": api_key,
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    items = []
    for v in r.json().get("items", []):
        vid = v["id"]
        sn = v["snippet"]
        st = v.get("statistics", {})
        items.append({
            "title": sn.get("title"),
            "channel": sn.get("channelTitle"),
            "views": int(st.get("viewCount", 0)) if st.get("viewCount") else None,
            "embed": f"https://www.youtube.com/embed/{vid}",
            "href": f"https://www.youtube.com/watch?v={vid}",
        })
    return items

# ---------- News: Google News RSS (fără cheie) ----------
# Top stories pentru România, în română.
def fetch_news(max_items=15):
    feed = "https://news.google.com/rss?hl=ro&gl=RO&ceid=RO:ro"
    r = requests.get(feed, timeout=30)
    r.raise_for_status()
    from xml.etree import ElementTree as ET
    root = ET.fromstring(r.content)
    ns = {}
    items = []
    for item in root.findall("./channel/item", ns)[:max_items]:
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        items.append({
            "title": title,
            "href": link,
        })
    return items

def fmt_int(n):
    return f"{n:,}".replace(",", " ")

def render_html(videos, news):
    video_cards = []
    for it in videos:
        title = html.escape(it["title"] or "")
        channel = html.escape(it.get("channel") or "")
        views = f'{fmt_int(it["views"])} views' if it.get("views") is not None else "—"
        video_cards.append(f"""
        <article class="card">
          <h3>{title}</h3>
          <p class="meta">{channel} • {views}</p>
          <div class="frame"><iframe src="{it['embed']}" loading="lazy" allowfullscreen></iframe></div>
          <a class="link" href="{it['href']}" target="_blank" rel="noopener">Deschide pe YouTube</a>
        </article>""")

    news_items = []
    for n in news:
        t = html.escape(n["title"] or "")
        href = n["href"]
        news_items.append(f'<li><a href="{href}" target="_blank" rel="noopener">{t}</a></li>')

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang="ro">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_TITLE}</title>
<style>
  :root{{--bg:#fafafa;--fg:#111;--muted:#666;--card:#fff;--border:#eee;--link:#0366d6}}
  body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Helvetica,Arial,sans-serif;margin:0;background:var(--bg);color:var(--fg)}}
  header{{position:sticky;top:0;background:#fff;border-bottom:1px solid var(--border);padding:12px 16px}}
  header h1{{font-size:18px;margin:0}}
  header .sub{{color:var(--muted);font-size:12px}}
  main{{max-width:1200px;margin:0 auto;padding:16px;display:grid;grid-template-columns:2fr 1fr;gap:20px}}
  .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}}
  .card{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:12px;box-shadow:0 1px 2px rgba(0,0,0,.04)}}
  .card h3{{font-size:16px;margin:0 0 8px}}
  .meta{{color:var(--muted);font-size:12px;margin:0 0 10px}}
  .frame{{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:12px;border:1px solid var(--border)}}
  .frame iframe{{position:absolute;top:0;left:0;width:100%;height:100%;border:0}}
  .link{{display:inline-block;margin-top:8px;font-size:12px;color:var(--link);text-decoration:none}}
  aside .card{{padding:16px}}
  aside h2{{font-size:16px;margin:0 0 8px}}
  aside ul{{list-style:disc;padding-left:18px;margin:0}}
  aside li{{margin:8px 0}}
  footer{{text-align:center;color:var(--muted);font-size:12px;padding:24px}}
  @media (max-width:900px){{ main{{grid-template-columns:1fr}} }}
</style>
</head>
<body>
<header>
  <h1>{SITE_TITLE}</h1>
  <div class="sub">Auto-actualizat • {now}</div>
</header>
<main>
  <section>
    <div class="grid">
      {''.join(video_cards)}
    </div>
  </section>
  <aside>
    <div class="card">
      <h2>Știri populare</h2>
      <ul>
        {''.join(news_items)}
      </ul>
    </div>
  </aside>
</main>
<footer>
  Folosește doar API-uri/embeds oficiale. Adaugă descrieri & categorii pentru SEO/monetizare.
</footer>
</body>
</html>"""

def main():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise SystemExit("Lipsește YOUTUBE_API_KEY (setează-l în GitHub Secrets).")
    videos = fetch_youtube(api_key, region="RO", max_results=15)
    news = fetch_news(max_items=15)
    html_page = render_html(videos, news)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_page)

if __name__ == "__main__":
    main()
