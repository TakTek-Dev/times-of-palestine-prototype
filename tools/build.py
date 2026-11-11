"""Build every page of The Times of Palestine prototype from research/edition.json.

Run: python tools/build.py      (never edit the generated .html by hand)
"""
import collections, datetime, html, json, pathlib, re

import brand

ROOT = pathlib.Path(__file__).resolve().parent.parent
V = 1  # bump after any CSS/JS change
ED = json.loads((ROOT / "research" / "edition.json").read_text(encoding="utf-8"))
NOW = datetime.datetime.fromisoformat(ED["now"])
SECTIONS = ED["sections"]
STORIES = ED["stories"]
LIVE = "https://paltimesnews.com"
NAME = "The Times of Palestine"
AGE_WORD = {"a-now": "Today", "a-week": "This week", "a-rec": "On record"}

e = html.escape
LF = '<i class="lf"></i>'

ICONS = {
    "home": '<path d="M4 11l8-7 8 7v8a1 1 0 0 1-1 1h-4v-6h-6v6H5a1 1 0 0 1-1-1z"/>',
    "discover": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "explain": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.3a2.5 2.5 0 1 1 3.6 2.3c-.8.4-1.200 1-1.200 1.900"/><path d="M12 16.800h.01"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    "moon": '<path d="M20 14.500A8 8 0 0 1 9.500 4a8 8 0 1 0 10.500 10.500z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.500 1.500M17.500 17.500L19 19M5 19l1.500-1.500M17.500 6.500L19 5"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h10"/>',
    "close": '<path d="M6 6l12 12M18 6L6 18"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "left": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "pin": '<path d="M12 21s7-6.200 7-11.500A7 7 0 0 0 5 9.500C5 14.800 12 21 12 21z"/><circle cx="12" cy="9.500" r="2.500"/>',
    "link": '<path d="M10 14a4 4 0 0 0 5.700 0l3-3a4 4 0 0 0-5.700-5.700l-1 1"/><path d="M14 10a4 4 0 0 0-5.700 0l-3 3a4 4 0 0 0 5.700 5.700l1-1"/>',
    "share": '<path d="M12 15V4M8 8l4-4 4 4"/><path d="M5 13v5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-5"/>',
    "out": '<path d="M8 16l8-8M9 8h7v7"/>',
    "play": '<path d="M8 5l12 7-12 7z"/>',
}


def ic(name, cls=""):
    return f'<svg class="ic{" " + cls if cls else ""}" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


def word(text, tag="h2", extra="", attrs=""):
    """A lower-case serif word led by a leaf."""
    return f'<{tag} class="word {extra}"{attrs}>{LF}<span>{e(text)}</span></{tag}>'


def when(s):
    d = datetime.datetime.fromisoformat(s["date"])
    return f'<time class="when" data-rel datetime="{d.isoformat()}">{d.day} {d.strftime("%b")}</time>'


def tagline(s, link=None):
    inner = f'{LF}<b>{e(s["tag"])}</b>'
    cls = f'tag {s["age"]}'
    return f'<a class="{cls}" href="{link}">{inner}</a>' if link else f'<span class="{cls}">{inner}</span>'


def pic(s, base, small=True, eager=False, cls=""):
    c = f"ph {cls}".strip()
    if not s["has_photo"]:
        return f'<span class="{c} none">{LF}</span>'
    name = f"{s['id']}-s.webp" if small else f"{s['id']}.webp"
    size = 'width="560" height="350"' if small else 'width="1120" height="700"'
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    return f'<span class="{c}"><img src="{base}assets/img/{name}" alt="" {size} {load}></span>'


def href(s, base):
    return f"{base}story/{s['id']}.html"


def card(s, base, big=False, i=0, gist=False):
    g = f'<p class="gist">{e(s["gist"])}</p>' if gist or big else ""
    return (f'<article class="card{" big" if big else ""} rv" style="--i:{i}"><a href="{href(s, base)}" tabindex="-1" aria-hidden="true">{pic(s, base, small=not big)}</a>'
            f'<div class="meta">{tagline(s)}{when(s)}</div><h3><a href="{href(s, base)}">{e(s["short"])}</a></h3>{g}</article>')


def row(s, base, i=0):
    return (f'<a class="row rv" style="--i:{i}" href="{href(s, base)}">{pic(s, base)}'
            f'<div>{tagline(s)}<h3>{e(s["short"])}</h3>{when(s)}</div></a>')


def ask(s, base, i=0):
    return (f'<a class="ask rv" style="--i:{i}" href="{href(s, base)}"><div>{tagline(s)}<h3>{e(s["short"])}</h3></div><p>{LF}<span>{e(s["gist"])}</span></p></a>')


def slug(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def topics(min_count=2):
    seen = collections.Counter(s["tag"] for s in STORIES)
    return [(slug(t), t, c) for t, c in seen.most_common() if c >= min_count]


def chips(base=""):
    return '<div class="chips rv">' + "".join(f'<a class="chip" href="{base}topic/{t}.html">{e(n)} <small>{c}</small></a>' for t, n, c in topics()) + "</div>"


NAV = [("index.html", "Home"), ("discover.html", "Discover"), ("gaza.html", "Gaza"), ("west-bank.html", "West Bank"), ("jerusalem.html", "Jerusalem"),
       ("diaspora.html", "Diaspora"), ("solidarity.html", "Solidarity"), ("analysis.html", "Analysis"), ("explained.html", "Explained")]
TABS = [("index.html", "Home", "home"), ("discover.html", "Discover", "discover"), ("explained.html", "Explained", "explain"), ("search.html", "Search", "search")]


def logo(height, lazy=False):
    attr = 'width="1597" height="257"' + (' loading="lazy"' if lazy else "")
    return (f'<img class="logo-l" src="{{base}}assets/logo.svg" alt="{NAME}" {attr} style="block-size:{height}px">'
            f'<img class="logo-d" src="{{base}}assets/logo-inverse.svg" alt="{NAME}" {attr} style="block-size:{height}px">')


def shell(path, title, desc, body, active="", base="", image=None, extra_head=""):
    nav = "".join(f'<a href="{base}{h}"{" aria-current=\"page\"" if h == active else ""}>{n}</a>' for h, n in NAV)
    tabs = "".join(f'<a href="{base}{h}"{" aria-current=\"page\"" if h == active else ""}>{ic(i)}{n}</a>' for h, n, i in TABS)
    sheet = "".join(f'<a href="{base}{h}">{LF}{n}</a>' for h, n in NAV + [("search.html", "Search")])
    og = f'{base}assets/img/{image}.webp' if image else f'{base}assets/logo.svg'
    return f'''<!doctype html>
<html lang="en" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#ffffff">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{og}">
<link rel="icon" href="{base}favicon.svg" type="image/svg+xml">
<link rel="preload" href="{base}assets/fonts/instrument-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{base}assets/fonts/abril-fatface.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{base}assets/leaf.css?v={V}">
<link rel="stylesheet" href="{base}assets/tp.css?v={V}">
<script>(function(){{var d=document.documentElement;d.classList.add('js');try{{var t=localStorage.getItem('tp-theme');if(t)d.dataset.theme=t;else if(matchMedia('(prefers-color-scheme: dark)').matches)d.dataset.theme='dark';if(/[?&]loader/.test(location.search)||!sessionStorage.getItem('tp-on'))d.classList.add('boot');else if(sessionStorage.getItem('tp-nav'))d.classList.add('nav-in')}}catch(e){{}}}})()</script>
{extra_head}</head>
<body data-now="{NOW.isoformat()}" data-base="{base}">
<a class="skip" href="#main">Skip to the stories</a>
<div class="veil" aria-hidden="true">{brand.mark(230)}</div>
<div class="pagebar" aria-hidden="true"></div>
<header class="top"><div class="wrap top-in">
<a class="brand" href="{base}index.html" aria-label="{NAME}, home">{logo(36).format(base=base)}</a>
<nav class="nav" aria-label="Sections">{nav}</nav>
<div class="tools">
<a class="ib" href="{base}search.html" aria-label="Search">{ic("search")}</a>
<button class="ib" type="button" data-theme-toggle aria-label="Dark mode" aria-pressed="false">{ic("moon", "i-moon")}{ic("sun", "i-sun")}</button>
<button class="ib burger" type="button" aria-label="Menu" aria-expanded="false" aria-controls="sheet">{ic("menu")}</button>
</div></div></header>
<div class="sheet" id="sheet" role="dialog" aria-modal="true" aria-label="Menu">
<div class="sheet-top"><a class="brand" href="{base}index.html" aria-label="{NAME}, home"><img src="{base}assets/logo-inverse.svg" alt="{NAME}" width="1597" height="257" style="block-size:32px"></a><button class="ib sheet-close" type="button" aria-label="Close menu">{ic("close")}</button></div>
<nav aria-label="All sections">{sheet}</nav>
<div class="sheet-foot"><a href="{base}about.html">About</a><a href="{base}about.html#standards">Standards</a><a href="{base}contact.html">Contact</a><a href="{base}brand.html">Identity</a></div>
</div>
<main id="main">
{body}
</main>
<footer class="foot"><div class="vine" aria-hidden="true"></div><div class="wrap">
<div class="foot-big"><a href="{base}index.html" aria-label="{NAME}, home"><img src="{base}assets/logo-inverse.svg" alt="{NAME}" width="1597" height="257" loading="lazy"></a><p>The news of the day, the context behind it, and the stories of the people who live it.</p></div>
<div class="foot-grid">
<div><h3><i class="lf a-now" style="color:var(--red-n)"></i>Places</h3><ul><li><a href="{base}gaza.html">Gaza</a></li><li><a href="{base}west-bank.html">West Bank</a></li><li><a href="{base}jerusalem.html">Jerusalem</a></li><li><a href="{base}diaspora.html">Diaspora</a></li></ul></div>
<div><h3><i class="lf" style="color:var(--green-n)"></i>Read</h3><ul><li><a href="{base}solidarity.html">Solidarity</a></li><li><a href="{base}analysis.html">Analysis</a></li><li><a href="{base}explained.html">Explained</a></li><li><a href="{base}discover.html">Discover</a></li></ul></div>
<div><h3><i class="lf" style="color:#fff"></i>The Times</h3><ul><li><a href="{base}about.html">About us</a></li><li><a href="{base}about.html#standards">Editorial standards</a></li><li><a href="{base}contact.html">Contact</a></li><li><a href="{base}search.html">Search</a></li></ul></div>
<div><h3>This prototype</h3><ul><li><a href="{base}brand.html">The identity</a></li><li><a href="{base}index.html?loader">Play the opening</a></li><li><a href="{LIVE}" rel="noopener">The current site</a></li></ul></div>
</div>
<div class="legal"><span>&copy; {NOW.year} {NAME}</span><span>Design prototype. Stories are sourced and linked; photographs are credited on each story.</span></div>
</div></footer>
<nav class="tabs" aria-label="Quick sections">{tabs}</nav>
<script src="{base}assets/tp.js?v={V}" defer></script>
</body>
</html>
'''


def write(path, page):
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")


# ------------------------------------------------------------------ discover
def shorts_list():
    picks = [s for s in STORIES if s["has_photo"]][:12]
    data = []
    for s in picks:
        more = s["body"][1] if len(s["body"]) > 1 else s["body"][0]
        if len(more) > 240:
            more = more[:238].rsplit(" ", 1)[0].rstrip(",;:") + "…"
        src = "Sources: " + ", ".join(x["name"] for x in s["sources"])
        data.append({"id": s["id"], "photo": s["has_photo"], "tag": f'{e(s["tag"])} · {e(s["place"])}' if s["place"] else e(s["tag"]),
                     "title": e(s["short"]), "gist": e(s["gist"]), "more": e(more), "sources": e(src)})
    return picks, data


def short_card(s, base="", i=0):
    return (f'<button class="short rv" style="--i:{i}" type="button" data-short="{s["id"]}"><img src="{base}assets/img/{s["id"]}-s.webp" alt="" width="560" height="350" loading="lazy" decoding="async">'
            f'<span class="three" aria-hidden="true"><i class="lf on"></i><i class="lf on"></i><i class="lf on"></i></span>'
            f'<span class="short-txt">{tagline(s)}<h3>{e(s["short"])}</h3></span></button>')


def shorts_script(data):
    return f'<script type="application/json" id="shorts-data">{json.dumps(data, ensure_ascii=False).replace("</", "<\\/")}</script>'


# ------------------------------------------------------------------ home
def home():
    used = set()

    def take(pool, n):
        got = [s for s in pool if s["id"] not in used][:n]
        used.update(s["id"] for s in got)
        return got

    lead = take([s for s in STORIES if s["has_photo"]], 1)[0]
    stem = take(STORIES, 6)
    stamp = f'{NOW.strftime("%A")} {NOW.day} {NOW.strftime("%B %Y")}'
    knots = "".join(f'<a class="knot" href="{href(s, "")}"><i class="lf {s["age"]}"></i><div><span class="meta">{when(s)}<span class="tag"><b>{e(s["tag"])}</b></span></span><h3>{e(s["short"])}</h3></div>{pic(s, "")}</a>' for s in stem)
    today = (f'<section class="today wrap" aria-labelledby="today"><div class="today-head">{word("today", "h1", "word-in", " id=\"today\"")}'
             f'<p><time datetime="{NOW.isoformat()}">{stamp}</time><span>{NOW.strftime("%H:%M")} in Jerusalem · newest at the top</span></p></div>'
             f'<div class="today-grid"><a class="lead" href="{href(lead, "")}">{pic(lead, "", small=False, eager=True)}<div class="meta">{tagline(lead)}{when(lead)}<span class="when">{ic("pin")}{e(lead["place"])}</span></div>'
             f'<h2>{e(lead["short"])}</h2><p class="gist">{e(lead["gist"])}</p></a>'
             f'<div class="stem"><h2>Latest</h2>{knots}<a class="more" href="search.html">Everything, newest first{ic("arrow")}</a></div></div>'
             f'<p class="key"><span><i class="lf a-now"></i><b>Red</b> is today</span><span><i class="lf a-week"></i><b>Green</b> is this week</span><span><i class="lf a-rec"></i><b>Black</b> is on the record</span></p></section>')

    week = take([s for s in STORIES if s["section"] != "analysis"], 8)
    week_html = (f'<section class="sec wrap" aria-labelledby="week"><div class="sec-head"><div>{word("this week", attrs=" id=\"week\"", extra="a-week")}<p>The stories still growing.</p></div></div>'
                 f'{chips()}<div class="grid" style="margin-block-start:28px">{"".join(card(s, "", i=i % 4) for i, s in enumerate(week))}</div></section>') if week else ""

    picks, data = shorts_list()
    disc = (f'<section class="band" aria-labelledby="disc"><div class="vine" aria-hidden="true"></div><div class="wrap"><div class="sec-head"><div>{word("discover", attrs=" id=\"disc\"")}<p>A story in three leaves: what happened, why it matters, and what is on the record.</p></div>'
            f'<div class="rail-nav" data-rail="rail"><button class="ib" type="button" data-dir="prev" aria-label="Earlier">{ic("left")}</button><button class="ib" type="button" data-dir="next" aria-label="More">{ic("arrow")}</button></div></div>'
            f'<div class="rail" id="rail">{"".join(short_card(s, "", i % 6) for i, s in enumerate(picks))}</div>'
            f'<p style="margin-block-start:22px"><a class="more" href="discover.html">Open discover{ic("arrow")}</a></p></div></section>{shorts_script(data)}')

    asks = [s for s in STORIES if s["kind"] == "ask"][:8]
    ask_html = (f'<section class="sec wrap" aria-labelledby="ask"><div class="sec-head"><div>{word("explained", attrs=" id=\"ask\"", extra="a-week")}<p>You ask who, what and why. The answer in one line, before the full story.</p></div>'
                f'<a class="more" href="explained.html">All explainers{ic("arrow")}</a></div><div class="asks">{"".join(ask(s, "", i % 3) for i, s in enumerate(asks))}</div></section>') if len(asks) >= 2 else ""

    trio = ""
    for key in ("gaza", "west-bank", "jerusalem"):
        pool = [s for s in STORIES if s["section"] == key]
        if not pool:
            continue
        trio += (f'<div><h2 class="word"><span>{e(SECTIONS[key]["name"].lower())}</span><a class="more" href="{key}.html" aria-label="All of {SECTIONS[key]["name"]}">{ic("arrow")}</a></h2>'
                 f'{card(pool[0], "")}<div class="rows">{"".join(row(s, "", i=i) for i, s in enumerate(pool[1:4]))}</div></div>')
    trio_html = f'<section class="sec wrap" aria-label="Gaza, West Bank and Jerusalem"><div class="trio">{trio}</div></section>'

    pair = ""
    for key in ("solidarity", "diaspora"):
        pool = [s for s in STORIES if s["section"] == key][:4]
        if pool:
            pair += (f'<div><div class="sec-head" style="margin-block-end:18px"><h2 class="word" style="font-size:clamp(34px,3.8vw,50px)"><span>{key}</span></h2><a class="more" href="{key}.html" aria-label="All of {key}">{ic("arrow")}</a></div>'
                     f'<div class="rows">{"".join(row(s, "", i=i) for i, s in enumerate(pool))}</div></div>')
    pair_html = f'<section class="sec wrap" aria-label="Solidarity and diaspora"><div class="split even">{pair}</div></section>' if pair else ""

    rec = take([s for s in STORIES if s["section"] == "analysis"], 4)
    rec += take([s for s in reversed(STORIES) if s["section"] != "analysis"], 8 - len(rec))
    half = (len(rec) + 1) // 2
    rec_html = (f'<section class="record" aria-labelledby="rec"><div class="vine" aria-hidden="true"></div><div class="wrap"><div class="sec-head"><div>{word("on record", attrs=" id=\"rec\"")}<p>Analysis and the stories that stay true after the day is over.</p></div>'
                f'<a class="more" href="analysis.html">All analysis{ic("arrow")}</a></div><div class="split even"><div class="rows">{"".join(row(s, "", i=i) for i, s in enumerate(rec[:half]))}</div>'
                f'<div class="rows">{"".join(row(s, "", i=i) for i, s in enumerate(rec[half:]))}</div></div></div></section>')

    body = today + week_html + disc + ask_html + trio_html + pair_html + rec_html
    write("index.html", shell("index.html", NAME, "The Times of Palestine is an English-language news site about Palestine: the news of the day, the context behind it, and the stories of the people who live it.", body, active="index.html"))


# ------------------------------------------------------------------ lists
def listing(path, title, line, stories, base="", active="", crumb="", extra="", plain=""):
    if not stories:
        body = f'<div class="wrap"><header class="phead">{crumb}{word(title, "h1", "word-in")}<p>{e(line)}</p></header><p class="page">Nothing here in this edition yet.</p></div>'
        return write(path, shell(path, f"{plain or title.title()} | {NAME}", line, body, active=active, base=base))
    lead, rest = stories[0], stories[1:]
    lead_html = (f'<a class="top-story" href="{href(lead, base)}">{pic(lead, base, small=False, eager=True)}<div><span class="meta">{tagline(lead)}{when(lead)}</span>'
                 f'<h2>{e(lead["short"])}</h2><p class="gist">{e(lead["gist"])}</p></div></a>')
    asks = [s for s in rest if s["kind"] == "ask"][:3]
    if len(asks) == 3:
        rest = [s for s in rest if s not in asks]
        ask_html = f'<div class="asks" style="margin-block:clamp(34px,5vw,56px)">{"".join(ask(s, base, i) for i, s in enumerate(asks))}</div>'
    else:
        ask_html = ""
    body = (f'<div class="wrap"><header class="phead">{crumb}{word(title, "h1", "word-in")}<p>{e(line)}</p>{extra}</header>{lead_html}'
            f'<div class="grid">{"".join(card(s, base, i=i % 4, gist=True) for i, s in enumerate(rest[:4]))}</div>{ask_html}'
            f'<div class="grid"{" style=\"margin-block-start:36px\"" if not ask_html else ""}>{"".join(card(s, base, i=i % 4, gist=True) for i, s in enumerate(rest[4:]))}</div></div>')
    write(path, shell(path, f"{plain or title.title()} | {NAME}", line, body, active=active, base=base))


def sections():
    for key, sec in SECTIONS.items():
        listing(f"{key}.html", sec["name"].lower(), sec["line"], [s for s in STORIES if s["section"] == key], active=f"{key}.html", plain=sec["name"], extra=chips().replace(' rv"', '"'))
    for t, n, c in topics():
        crumb = f'<p class="crumb"><a href="../index.html">Home</a>{LF}<span>Topic</span></p>'
        listing(f"topic/{t}.html", n.lower(), f"{c} stories on {n.lower()}, newest first.", [s for s in STORIES if s["tag"] == n], base="../", crumb=crumb, plain=n)
    asks = [s for s in STORIES if s["kind"] == "ask"]
    body = (f'<div class="wrap"><header class="phead">{word("explained", "h1", "word-in")}<p>You ask who, what and why. The answer in one line, before the full story.</p></header>'
            f'<div class="asks" style="padding-block-end:40px">{"".join(ask(s, "", i % 3) for i, s in enumerate(asks))}</div></div>')
    write("explained.html", shell("explained.html", f"Explained | {NAME}", "Explainers from The Times of Palestine.", body, active="explained.html"))


# ------------------------------------------------------------------ story
def story_pages():
    for n, s in enumerate(STORIES):
        base = "../"
        d = datetime.datetime.fromisoformat(s["date"])
        sec = SECTIONS[s["section"]]
        prose = ""
        for i, para in enumerate(s["body"]):
            if i in s["subheads"] and i:
                prose += f'<h2>{LF}<span>{e(s["subheads"][i])}</span></h2>'
            prose += f"<p>{e(para)}</p>"
        related = [x for x in STORIES if x["id"] != s["id"] and x["tag"] == s["tag"]][:4]
        related += [x for x in STORIES if x["id"] != s["id"] and x not in related and x["section"] == s["section"]][: 4 - len(related)]
        nxt = STORIES[(n + 1) % len(STORIES)]
        tag_link = f"{base}topic/{slug(s['tag'])}.html" if any(t[1] == s["tag"] for t in topics()) else None
        fig = ""
        if s["has_photo"]:
            p = s["photo"]
            credit = " ".join(x for x in [e(p.get("caption", "")), f'Photo: <a href="{e(p["page_url"])}" rel="noopener">{e(p["credit"])}</a>' if p.get("credit") else "", e(p.get("license", ""))] if x)
            fig = f'<figure class="story-pic">{pic(s, base, small=False, eager=True)}<figcaption>{credit}</figcaption></figure>'
        sources = "".join(f'<li><a href="{e(x["url"])}" rel="noopener">{e(x["name"])}{ic("out")}</a></li>' for x in s["sources"])
        body = (f'<div class="prog" aria-hidden="true"></div><article class="wrap">'
                f'<header class="story-head"><p class="crumb"><a href="{base}{s["section"]}.html">{e(sec["name"])}</a>{tagline(s, tag_link)}</p>'
                f'<h1>{e(s["title"])}</h1>'
                f'<div class="oneline rv"><small>{LF}{"The short answer" if s["kind"] == "ask" else "In one line"}</small><p>{e(s["gist"])}</p></div>'
                f'<div class="by"><span class="tag {s["age"]}">{LF}<b>{AGE_WORD[s["age"]]}</b></span><time datetime="{d.isoformat()}"><b>{d.day} {d.strftime("%B %Y")}</b>, {d.strftime("%H:%M")} Jerusalem</time>'
                f'{f"""<span class="when">{ic("pin")}{e(s["place"])}</span>""" if s["place"] else ""}<span class="when">{ic("clock")}{s["minutes"]} min read</span></div></header>'
                f'{fig}<div class="story-grid"><div><div class="prose">{prose}</div>'
                f'<section class="onrecord" aria-labelledby="src"><h2 id="src"><i class="lf a-rec"></i>On the record</h2><ul>{sources}</ul><p>Reported from the sources above, in our own words.</p></section>'
                f'<div class="end"><div class="share"><button class="btn" type="button" data-share="native">{ic("share")}<span>Share</span></button>'
                f'<button class="btn ghost" type="button" data-share="copy">{ic("link")}<span>Copy link</span></button></div></div></div>'
                f'<aside class="aside" aria-labelledby="rel"><div><h2 id="rel" class="word">more</h2><div class="rows">{"".join(row(x, base, i=i) for i, x in enumerate(related))}</div></div></aside></div>'
                f'<a class="next" href="{href(nxt, base)}"><span><small>Next story</small><b>{e(nxt["short"])}</b></span>{ic("arrow")}</a></article>')
        ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": s["title"], "datePublished": s["date"],
              "publisher": {"@type": "NewsMediaOrganization", "name": NAME}, "description": s["gist"]}
        head = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script>\n'
        write(f"story/{s['id']}.html", shell("", f"{s['short']} | {NAME}", s["gist"], body, base=base, image=s["id"] if s["has_photo"] else None, extra_head=head, active=f"{s['section']}.html"))


# ------------------------------------------------------------------ other pages
def discover():
    picks, data = shorts_list()
    body = (f'<div class="wrap"><header class="phead">{word("discover", "h1", "word-in")}<p>A story in three leaves: what happened, why it matters, and what is on the record. Tap right to move on, left to go back.</p></header>'
            f'<div class="grid" style="grid-template-columns:repeat(auto-fill,minmax(min(46%,210px),1fr));gap:14px;padding-block-end:40px">{"".join(short_card(s, "", i % 5) for i, s in enumerate(picks))}</div></div>{shorts_script(data)}')
    write("discover.html", shell("discover.html", f"Discover | {NAME}", "Stories in three taps.", body, active="discover.html"))


def search():
    body = (f'<div class="wrap"><header class="phead">{word("search", "h1", "word-in")}<p>Every story in this edition, by place, topic or name.</p>'
            f'<form class="find" id="find" role="search"><label class="vh" for="q">Search {NAME}</label><input id="q" name="q" type="search" placeholder="Try “Nablus”, “aid” or “olive”" autocomplete="off" enterkeyhint="search">'
            f'<button class="btn" type="submit">{ic("search")}Search</button></form></header>'
            f'<p class="count" id="count" role="status" aria-live="polite"></p><div class="rows" id="results" style="max-inline-size:820px;padding-block-end:40px"></div><noscript><p>Search needs JavaScript.</p></noscript></div>')
    write("search.html", shell("search.html", f"Search | {NAME}", "Search The Times of Palestine.", body, active="search.html"))
    index = []
    for s in STORIES:
        d = datetime.datetime.fromisoformat(s["date"])
        index.append({"id": s["id"], "title": s["short"], "tag": s["tag"], "place": s["place"], "age": s["age"], "photo": s["has_photo"], "when": f'{d.day} {d.strftime("%b")}',
                      "hay": " ".join([s["title"], s["gist"], s["tag"], s["place"], SECTIONS[s["section"]]["name"]]).lower()})
    (ROOT / "assets" / "stories.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")


def simple(path, title, plain, intro, inner):
    body = f'<div class="wrap"><header class="phead">{word(title, "h1", "word-in")}<p>{intro}</p></header><div class="page">{inner}</div></div>'
    write(path, shell(path, f"{plain} | {NAME}", re.sub(r"<[^>]+>", "", intro), body))


def others():
    simple("about.html", "about", "About", "The Times of Palestine is an English-language news site about Palestine.",
           f'<p>The news of the day, the context behind it, and the stories of the people who live it. We report daily life as carefully as the day&#39;s events, and we say where every fact comes from.</p>'
           f'<h2 id="standards">Editorial standards</h2><p>Every story on this site ends with the sources it was reported from. A photograph that was not taken at the event is labelled as an archive image, with its year. The full standards are on the current site: <a href="{LIVE}/about#standards" rel="noopener">editorial standards</a>.</p>'
           f'<h2>How to read us</h2><p>The three leaves of our mark tell you when a story is from. A red leaf is today. A green leaf is this week. A black leaf is on the record: older, and still true.</p>')
    links = "".join(f'<a href="{LIVE}{p}" rel="noopener"><span>{n}</span>{ic("out")}</a>' for n, p in
                    [("Contact the newsroom", "/contact"), ("Our writers", "/writers"), ("Privacy notice", "/privacy"), ("Terms", "/privacy#terms")])
    simple("contact.html", "contact", "Contact", "The contact form, the writers and the legal pages stay where they are on the current site.", f'<div class="list-links">{links}</div>')
    lost = (f'<div class="wrap lost">{word("lost", "h1", "word-in")}<p style="font-size:21px;color:var(--text-2);max-inline-size:40ch">This page fell off the stem. The stories are still where you left them.</p>'
            f'<div class="chips"><a class="btn" href="index.html">Back to today{ic("arrow")}</a><a class="btn ghost" href="search.html">{ic("search")}Search</a></div></div>')
    page = shell("404.html", f"Page not found | {NAME}", "Page not found.", lost)
    base_fix = '<script>(function(){var b=location.hostname.endsWith("github.io")?"/"+location.pathname.split("/")[1]+"/":"/";document.write(\'<base href="\'+b+\'">\')})()</script>\n'
    write("404.html", page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + base_fix, 1))


if __name__ == "__main__":
    import shutil
    for stale in ("story", "topic"):      # pages of stories no longer in the edition
        shutil.rmtree(ROOT / stale, ignore_errors=True)
    brand.main()
    home()
    sections()
    story_pages()
    discover()
    search()
    others()
    import book
    book.main()
    print(len(list(ROOT.glob("*.html"))) + len(list(ROOT.glob("*/*.html"))), "pages")
