"""The indiatimes.com layout, in The Times of Palestine's identity.

Feed pages (home, sections, topics, explained) use the three columns of the
indiatimes.com front: a sticky menu, one feed of story cards, side modules.
Story pages use its article: a full-width photograph carrying the headline,
then the text beside the latest stories.  Runs after build.py's own pages and
replaces those files.

Run through build.py.
"""
import datetime, json

import build
from build import LF, e, ic

build.ICONS.update({
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.600 2.600 2.600 15.400 0 18M12 3c-2.600 2.600-2.600 15.400 0 18"/>',
    "flag": '<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>',
    "chart": '<path d="M4 20h16"/><path d="M7 16v-5M12 16V7M17 16v-8"/>',
    "up": '<path d="M12 19V5M6 11l6-6 6 6"/>',
})

RAIL = [("index.html", "home", "home"), ("discover.html", "discover", "discover"), ("gaza.html", "gaza", "pin"), ("west-bank.html", "west bank", "pin"),
        ("jerusalem.html", "jerusalem", "pin"), ("diaspora.html", "diaspora", "globe"), ("solidarity.html", "solidarity", "flag"),
        ("analysis.html", "analysis", "chart"), ("explained.html", "explained", "explain"), ("search.html", "search", "search")]

SCRIPT = """<script>
(()=>{const up=document.querySelector('.fd-up');if(up){addEventListener('scroll',()=>up.classList.toggle('on',scrollY>900),{passive:true});up.addEventListener('click',()=>scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'}))}
const box=document.querySelector('.fd-q');if(!box)return;const qs=JSON.parse(document.getElementById('fd-qs').textContent);let i=0;
const q=box.querySelector('.q'),a=box.querySelector('.a'),go=box.querySelector('.go'),read=box.querySelector('.read');
function paint(){q.textContent=qs[i].q;a.textContent=qs[i].a;read.href=qs[i].href;box.classList.remove('open');go.textContent='show the answer';go.setAttribute('aria-expanded','false')}
go.addEventListener('click',()=>{const o=box.classList.toggle('open');go.textContent=o?'hide':'show the answer';go.setAttribute('aria-expanded',o)});
box.querySelector('[data-d=prev]').addEventListener('click',()=>{i=(i-1+qs.length)%qs.length;paint()});
box.querySelector('[data-d=next]').addEventListener('click',()=>{i=(i+1)%qs.length;paint()});paint()})();
</script>"""


def head(base):
    return f'<link rel="stylesheet" href="{base}assets/feed.css?v={build.V}">\n'


def stamp(s):
    d = datetime.datetime.fromisoformat(s["date"])
    return f'<time datetime="{d.isoformat()}">{d.strftime("%b")} {d.day}, {d.year}, {d.strftime("%H:%M")}</time>'


def desk(s):
    return build.SECTIONS[s["section"]]["name"] + " desk"


def byline(s):
    return f'<span class="fd-by"><span class="fd-ava {s["age"]}" aria-hidden="true">{LF}</span><span><b>{e(desk(s))}</b>{stamp(s)}</span></span>'


def feed_card(s, base):
    url = build.href(s, base)
    pic = (f'<img src="{base}assets/img/{s["id"]}.webp" alt="" width="1120" height="700" loading="lazy" decoding="async">' if s["has_photo"] else LF)
    return (f'<article class="fd-card rv"><a class="fd-pic{"" if s["has_photo"] else " none"}" href="{url}" tabindex="-1" aria-hidden="true">{pic}</a>'
            f'<span class="pill {s["age"]}">{LF}{e(s["tag"])}</span>'
            f'<div class="fd-body"><h2><a href="{url}">{e(s["short"])}</a></h2><p class="fd-gist">{e(s["gist"])}<span class="fd-more" aria-hidden="true">...more</span></p></div>'
            f'<div class="fd-foot">{byline(s)}'
            f'<button class="fd-share" type="button" data-share="native" data-url="{url}" data-title="{e(s["short"])}"><span>share</span>{ic("share")}</button></div></article>')


def discover_block(picks, base):
    cards = "".join(build.short_card(s, base, 0).replace(' rv"', '"') for s in picks)
    return (f'<section class="fd-block" aria-label="Discover"><div class="fd-block-head"><b>{LF}<span>the times on discover<small>a story in three leaves</small></span></b>'
            f'<a class="fd-out" href="{base}discover.html">open</a></div><div class="fd-strip">{cards}</div></section>')


def explained_block(asks, base):
    cards = "".join(build.ask(s, base, 0).replace(' rv"', '"') for s in asks)
    return (f'<section class="fd-block" aria-label="Explained"><div class="fd-block-head"><b>{LF}<span>explained<small>the answer in one line</small></span></b>'
            f'<a class="fd-out" href="{base}explained.html">all</a></div><div class="fd-strip" style="grid-auto-columns:minmax(220px,56%)">{cards}</div></section>')


def tall(stories, base):
    return "".join(f'<a href="{build.href(s, base)}"><img src="{base}assets/img/{s["id"]}-s.webp" alt="" width="560" height="350" loading="lazy" decoding="async"><span class="pill {s["age"]}">{LF}{e(s["tag"])}</span>'
                   f'<span class="t"><b>{e(s["short"])}</b><small>by {e(desk(s))}, {stamp(s)}</small></span></a>' for s in stories)


def side(base):
    stories = build.STORIES
    places = ""
    for key in ("gaza", "west-bank", "jerusalem", "diaspora"):
        pool = [s for s in stories if s["section"] == key]
        if pool:
            places += (f'<a class="fd-place" href="{base}{key}.html"><i class="dotc {pool[0]["age"]}">{LF}</i><span><b>{e(build.SECTIONS[key]["name"])}</b>'
                       f'<small>{len(pool)} stories · latest {build.when(pool[0])}</small></span>{ic("arrow")}</a>')
    latest = [x for x in stories if x["has_photo"]][:5]
    qs = [{"q": s["short"], "a": s["gist"], "href": build.href(s, base)} for s in stories if s["kind"] == "ask"]
    return (f'<aside class="fd-side" aria-label="More from The Times of Palestine">'
            f'<section><h2>{LF}places</h2><div class="fd-box">{places}</div></section>'
            f'<section><h2>{LF}latest stories</h2><div class="fd-tall">{tall(latest, base)}</div></section>'
            f'<section><h2>{LF}quick question</h2><div class="fd-q"><p class="q"></p><p class="a" aria-live="polite"></p>'
            f'<div class="row-b"><button class="ib" type="button" data-d="prev" aria-label="Previous question">{ic("left")}</button><button class="go" type="button" aria-expanded="false"></button>'
            f'<button class="ib" type="button" data-d="next" aria-label="Next question">{ic("arrow")}</button></div><a class="read" href="#">read the story</a></div></section>'
            f'<script type="application/json" id="fd-qs">{json.dumps(qs, ensure_ascii=False).replace("</", "<\\/")}</script></aside>')


def layout(main, active, base):
    rail = "".join(f'<a href="{base}{h}"{" aria-current=\"page\"" if h == active else ""}>{ic(i)}{n}</a>' for h, n, i in RAIL)
    return (f'<div class="fd"><nav class="fd-rail" aria-label="Sections">{rail}<hr><small>Red is today, green is this week, black is on the record.</small></nav>'
            f'<div class="fd-main">{main}</div>{side(base)}</div><button class="fd-up" type="button" aria-label="Back to top">{ic("up")}</button>')


def feed_page(path, word, stories, base="", active="", crumb="", line="", blocks=True, title=None, desc=""):
    now = build.NOW
    picks, data = build.shorts_list()
    asks = [s for s in build.STORIES if s["kind"] == "ask"]
    cards = []
    for n, s in enumerate(stories):
        cards.append(feed_card(s, base))
        if blocks and n == 2:
            cards.append(discover_block(picks[:8], base))
        if blocks and n == 7 and len(asks) > 2:
            cards.append(explained_block(asks[:6], base))
    if not stories:
        cards.append('<p class="fd-line">Nothing here in this edition yet.</p>')
    main = (f'{crumb}<div class="fd-head"><h1 class="word{"" if word == "today" else " big"}">{e(word)}{LF}</h1>'
            f'<time datetime="{now.isoformat()}">{now.strftime("%b")} {now.day}, {now.year} | {now.strftime("%I:%M %p").lstrip("0")}</time></div>'
            f'{f"""<p class="fd-line">{e(line)}</p>""" if line else ""}<div class="fd-list">{"".join(cards)}</div>')
    body = layout(main, active, base) + (build.shorts_script(data) if blocks else "") + SCRIPT
    build.write(path, build.shell(path, title or f"{word.title()} | {build.NAME}", desc or line or build.NAME, body, active=active, base=base,
                                  extra_head=head(base), body_cls="feedmode"))


def story_pages():
    stories = build.STORIES
    for n, s in enumerate(stories):
        base = "../"
        sec = build.SECTIONS[s["section"]]
        hero_img = f'<img src="{base}assets/img/{s["id"]}.webp" alt="" width="1120" height="700" fetchpriority="high">' if s["has_photo"] else ""
        hero = (f'<header class="st-hero{"" if s["has_photo"] else " none"}">{hero_img}<span class="pill {s["age"]}">{LF}{e(s["tag"])}</span>'
                f'<div class="st-acts"><button type="button" data-share="native" aria-label="Share this story"><span class="vh">share</span>{ic("share")}</button>'
                f'<a href="#src" aria-label="Sources">{ic("link")}</a></div><h1>{e(s["title"])}</h1></header>')
        cap = ""
        if s["has_photo"]:
            p = s["photo"]
            bits = [e(p.get("caption", ""))]
            if p.get("credit"):
                bits.append(f'Photo: <a href="{e(p["page_url"])}" rel="noopener">{e(p["credit"])}</a> {e(p.get("license", ""))}')
            cap = f'<p class="st-cap">{" ".join(b for b in bits if b)}</p>'
        prose = ""
        for i, para in enumerate(s["body"]):
            if i in s["subheads"] and i:
                prose += f'<h2>{LF}<span>{e(s["subheads"][i])}</span></h2>'
            prose += f"<p>{e(para)}</p>"
        sources = "".join(f'<li><a href="{e(x["url"])}" rel="noopener">{e(x["name"])}{ic("out")}</a></li>' for x in s["sources"])
        related = [x for x in stories if x["id"] != s["id"] and x["tag"] == s["tag"]][:4]
        related += [x for x in stories if x["id"] != s["id"] and x not in related and x["section"] == s["section"]][: 4 - len(related)]
        nxt = stories[(n + 1) % len(stories)]
        latest = [x for x in stories if x["has_photo"] and x["id"] != s["id"]][:4]
        label = "The short answer" if s["kind"] == "ask" else "In one line"
        main = (f'<div class="st"><article><div class="st-by">{byline(s)}<span class="st-read">{s["minutes"]} min read</span></div>'
                f'<div class="st-syn rv"><small>{LF}{label}</small>{e(s["gist"])}</div>{cap}'
                f'<div class="prose">{prose}</div>'
                f'<section class="onrecord" aria-labelledby="src"><h2 id="src"><i class="lf a-rec"></i>On the record</h2><ul>{sources}</ul>'
                f'<p>Reported from the sources above, in our own words. Filed under <a href="{base}{s["section"]}.html" style="text-decoration:underline">{e(sec["name"])}</a>.</p></section>'
                f'<div class="end"><div class="share"><button class="btn" type="button" data-share="native">{ic("share")}<span>Share</span></button>'
                f'<button class="btn ghost" type="button" data-share="copy">{ic("link")}<span>Copy link</span></button></div></div></article>'
                f'<aside class="st-side" aria-label="Latest stories"><section><h2>{LF}latest stories</h2><div class="fd-tall">{tall(latest, base)}</div></section></aside></div>'
                f'<div class="st-more"><div class="sec-head" style="margin-block-end:12px"><h2 class="word" style="font-size:clamp(34px,4vw,48px)"><span>more</span></h2></div>'
                f'<div class="split even"><div class="rows">{"".join(build.row(x, base, i=i) for i, x in enumerate(related[:2]))}</div>'
                f'<div class="rows">{"".join(build.row(x, base, i=i) for i, x in enumerate(related[2:4]))}</div></div>'
                f'<a class="next" href="{build.href(nxt, base)}" style="margin-block-start:30px"><span><small>Next story</small><b>{e(nxt["short"])}</b></span>{ic("arrow")}</a></div>')
        ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": s["title"], "datePublished": s["date"],
              "publisher": {"@type": "NewsMediaOrganization", "name": build.NAME}, "description": s["gist"]}
        extra = head(base) + f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")}</script>\n'
        body = f'<div class="prog" aria-hidden="true"></div>{hero}{main}'
        build.write(f"story/{s['id']}.html", build.shell("", f"{s['short']} | {build.NAME}", s["gist"], body, base=base,
                                                         image=s["id"] if s["has_photo"] else None, extra_head=extra, active=f"{s['section']}.html"))


def main():
    stories = build.STORIES
    feed_page("index.html", "today", stories, active="index.html", title=build.NAME,
              desc="The Times of Palestine: the news of the day, the context behind it, and the stories of the people who live it.")
    for key, sec in build.SECTIONS.items():
        feed_page(f"{key}.html", sec["name"].lower(), [s for s in stories if s["section"] == key], active=f"{key}.html",
                  line=sec["line"], blocks=False, title=f"{sec['name']} | {build.NAME}")
    for t, n, c in build.topics():
        crumb = f'<p class="fd-crumb"><a href="../index.html">home</a>{LF}<span>topic</span></p>'
        feed_page(f"topic/{t}.html", n.lower(), [s for s in stories if s["tag"] == n], base="../", crumb=crumb,
                  line=f"{c} stories on {n.lower()}, newest first.", blocks=False, title=f"{n} | {build.NAME}")
    feed_page("explained.html", "explained", [s for s in stories if s["kind"] == "ask"], active="explained.html",
              line="You ask who, what and why. The answer in one line, before the full story.", blocks=False, title=f"Explained | {build.NAME}")
    story_pages()
    (build.ROOT / "feed.html").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
