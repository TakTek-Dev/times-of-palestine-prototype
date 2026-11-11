"""Turn research/news.json (sourced stories) into the edition the site is built from.

Checks each story, works out which leaf it wears (today, this week, on record)
and saves its photograph at two sizes.  Run: python tools/edition.py
"""
import collections, datetime, io, json, pathlib, re, subprocess, time, urllib.parse

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
UA = "TakTekPrototype/1.0 (design prototype; static build)"
PAL = datetime.timezone(datetime.timedelta(hours=2))
NOW = datetime.datetime(2026, 11, 11, 18, 0, tzinfo=PAL)   # the edition's clock, Jerusalem time

SECTIONS = collections.OrderedDict([
    ("gaza", {"name": "Gaza", "line": "The Strip, street by street: aid, health, schools and the people rebuilding a day at a time."}),
    ("west-bank", {"name": "West Bank", "line": "Nablus to Hebron: land, harvest, roads and the towns between them."}),
    ("jerusalem", {"name": "Jerusalem", "line": "The Old City and the neighbourhoods around it."}),
    ("diaspora", {"name": "Diaspora", "line": "Palestinians abroad: camps, culture, sport and the long way home."}),
    ("solidarity", {"name": "Solidarity", "line": "Marches, campaigns, courts and what governments say and do."}),
    ("analysis", {"name": "Analysis", "line": "The context behind the day: explainers and the longer view."}),
])


def age(when):
    hours = (NOW - when).total_seconds() / 3600
    return "a-now" if hours < 24 else "a-week" if hours < 24 * 7 else "a-rec"


def photo(story):
    IMG.mkdir(parents=True, exist_ok=True)
    big, small = IMG / f"{story['id']}.webp", IMG / f"{story['id']}-s.webp"
    if big.exists() and small.exists():
        return True
    p = story.get("photo")
    if not p or not p.get("file_url"):
        return False
    name = urllib.parse.unquote(p["file_url"].split("?")[0].rsplit("/", 1)[-1])
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(name) + "?width=1600"
    if "wikimedia.org" not in p["file_url"]:
        url = p["file_url"]
    try:
        raw = subprocess.run(["curl", "-sL", "-m", "60", "-A", UA, url], capture_output=True, check=False).stdout
        im = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as err:
        print("  no photo", story["id"], err)
        return False
    time.sleep(0.6)
    if im.width < 700:
        return False
    w, h = im.size
    target = 16 / 10
    if w / h > target:
        nw = int(h * target); im = im.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / target); top = int((h - nh) * 0.38); im = im.crop((0, top, w, top + nh))
    im.resize((1120, 700), Image.LANCZOS).save(big, "WEBP", quality=78, method=6)
    im.resize((560, 350), Image.LANCZOS).save(small, "WEBP", quality=74, method=6)
    return True


def main():
    raw = []
    names = ("news.json",) if (ROOT / "research" / "news.json").exists() else ("site.json",)   # site.json is layout filler until the sourced edition exists
    for name in names:
        path = ROOT / "research" / name
        if path.exists():
            raw += json.loads(path.read_text(encoding="utf-8"))
    stories, seen = [], set()
    for s in raw:
        sid = re.sub(r"[^a-z0-9]+", "-", s["id"].lower()).strip("-")
        if sid in seen or s.get("section") not in SECTIONS or len(s.get("body", [])) < 3 or not s.get("sources"):
            print("  skipped", s.get("id"))
            continue
        seen.add(sid)
        when = datetime.datetime.fromisoformat(s["date"]).astimezone(PAL)
        when = min(when, NOW - datetime.timedelta(minutes=20))
        story = {
            "id": sid, "section": s["section"], "tag": s["tag"].strip(), "place": s.get("place", "").strip(),
            "title": s["title"].strip(), "short": s.get("short", s["title"]).strip(), "kind": s.get("kind", "say"),
            "gist": s["gist"].strip(), "body": s["body"], "subheads": {int(k): v for k, v in (s.get("subheads") or {}).items()},
            "date": when.isoformat(), "age": age(when), "sources": s["sources"], "photo": s.get("photo"),
            "minutes": max(1, round(sum(len(p.split()) for p in s["body"]) / 220)),
        }
        story["has_photo"] = photo(story)
        stories.append(story)
    stories.sort(key=lambda x: x["date"], reverse=True)
    out = {"now": NOW.isoformat(), "sections": SECTIONS, "stories": stories}
    (ROOT / "research" / "edition.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(len(stories), "stories,", sum(s["has_photo"] for s in stories), "with photo")
    print(collections.Counter(s["section"] for s in stories))
    print(collections.Counter(s["age"] for s in stories), collections.Counter(s["kind"] for s in stories))


if __name__ == "__main__":
    main()
