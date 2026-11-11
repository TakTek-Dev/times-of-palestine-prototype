"""Read the stories already on paltimesnews.com into research/site.json (same shape as news.json)."""
import html, json, pathlib, re, subprocess, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "tools" / "out" / "site"
SITE = "https://paltimesnews.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
SECTION = {"Gaza": "gaza", "West Bank": "west-bank", "Jerusalem": "jerusalem", "Diaspora": "diaspora", "Solidarity": "solidarity"}


def get(url, dest):
    if not dest.exists():
        subprocess.run(["curl", "-sL", "-m", "40", "-A", UA, "-o", str(dest), url], check=False)
        time.sleep(0.3)
    return dest.read_text(encoding="utf-8", errors="replace")


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    links = set()
    for front in ("", "archive", "opinion", "photos", "section/Gaza", "section/West%20Bank", "section/Jerusalem", "section/Solidarity", "section/Diaspora"):
        page = get(f"{SITE}/{front}", RAW / ("front_" + re.sub(r"\W+", "_", front) + ".html"))
        links.update(re.findall(r'https://paltimesnews\.com/news/(\d+/[a-z0-9-]+)', page))
    out = []
    for link in sorted(links, key=lambda x: int(x.split("/")[0])):
        page = get(f"{SITE}/news/{link}", RAW / (link.split("/")[0] + ".html"))
        meta = {}
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, flags=re.S):
            try:
                data = json.loads(block)
            except ValueError:
                continue
            if isinstance(data, dict) and data.get("@type") == "NewsArticle":
                meta = data
        title = meta.get("headline", "")
        if not title or "[" in title or re.match(r"(Official position|Statement|Campaign):", title) or "What we know so far" in title:
            continue
        crumbs = [text(c) for c in re.findall(r'<li>(.*?)</li>', page[page.find('class="crumbs"'): page.find('class="crumbs"') + 1500], flags=re.S)]
        section = next((SECTION[c] for c in crumbs if c in SECTION), None)
        kicker = re.search(r'class="kicker[^"]*">(.*?)</p>', page, flags=re.S)
        tag = text(kicker.group(1)).split("·")[0].strip() if kicker else ""
        start = page.find('class="art__body')
        paras = [text(p) for p in re.findall(r"<p[^>]*>(.*?)</p>", page[start: start + 30000], flags=re.S)] if start > 0 else []
        paras = [p for p in paras if len(p) > 80][:8]
        cap = re.search(r"<figcaption[^>]*>(.*?)</figcaption>", page, flags=re.S)
        image = (meta.get("image") or [""])[0]
        if not section or len(paras) < 3:
            section = section or ("analysis" if "/opinion" in page[:20000] and "Analysis" in crumbs else section)
        if not section or len(paras) < 3:
            continue
        out.append({
            "id": link.split("/", 1)[1][:70], "section": section, "tag": tag or "Feature", "place": crumbs[-1] if crumbs else "",
            "title": title, "short": title, "kind": "ask" if re.match(r"(who|what|why|how)\b", title, re.I) else "say",
            "gist": text(meta.get("description", "")), "body": paras, "subheads": {}, "date": meta.get("datePublished"),
            "sources": [{"name": "The Times of Palestine", "url": f"{SITE}/news/{link}"}],
            "photo": {"file_url": image, "page_url": f"{SITE}/news/{link}", "credit": "", "license": "", "caption": text(cap.group(1)) if cap else ""} if image else None,
        })
    (ROOT / "research" / "site.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(out), "stories from the live site")


if __name__ == "__main__":
    main()
