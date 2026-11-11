"""The identity book: brand.html.  Numbers on the page are computed here or in brand.py."""
import brand
import build

LF = build.LF


def lum(hex_):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


CSS = """<style>
.bk{padding-block:clamp(40px,7vw,90px);border-block-start:1px solid var(--line)}
.bk>h2{font-size:clamp(40px,6vw,76px);margin-block-end:14px;display:flex;align-items:center;gap:.22em}
.bk>h2 .lf{font-size:.34em}
.bk>p{max-inline-size:62ch;color:var(--text-2);font-size:19px;margin-block-end:30px}
.bk-n{font-weight:700;color:var(--red);font-size:13px;letter-spacing:.08em;display:block;margin-block-end:14px}
.plate{background:var(--mist);border-radius:var(--nib) var(--leaf);padding:clamp(20px,4vw,48px);display:grid;place-items:center;min-inline-size:0}
.plate.flip{border-radius:var(--leaf) var(--nib)}
.plate svg,.plate img{max-inline-size:100%;block-size:auto}
.two{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:stretch}
.two>*{min-inline-size:0}
.facts{display:grid;gap:10px;align-content:start}
.facts li{display:grid;grid-template-columns:auto 1fr;gap:16px;padding:16px 20px;border-radius:var(--nib) 22px;background:var(--mist);align-items:center}
.facts li:nth-child(even){border-radius:22px var(--nib)}
.facts .lf{font-size:26px}
.sw{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,190px),1fr));gap:12px}
.sw div{border-radius:var(--nib) 30px;padding:18px;min-block-size:170px;display:grid;align-content:end;gap:2px;font-size:14px;box-shadow:inset 0 0 0 1px rgb(25 7 7/.08)}
.sw div:nth-child(even){border-radius:30px var(--nib)}
.sw b{font-size:18px}
.tt{display:grid;gap:12px}
.tt div{padding:24px 26px;border-radius:var(--nib) var(--leaf);background:var(--mist);display:grid;gap:10px;min-inline-size:0}
.tt div:nth-child(even){border-radius:var(--leaf) var(--nib)}
.tt small{font-weight:700;font-size:12.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--green)}
.parts{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,270px),1fr));gap:12px}
.parts>div{padding:22px;border-radius:var(--nib) var(--leaf);background:var(--mist);display:grid;gap:16px;align-content:space-between;min-block-size:240px}
.parts>div:nth-child(even){border-radius:var(--leaf) var(--nib)}
.parts h3{font-size:19px;font-weight:700}.parts p{font-size:15px;color:var(--text-2)}
.demo{display:grid;place-items:center;min-block-size:110px}
.nolgo{background:var(--night);color:#fff;border-radius:var(--nib) clamp(40px,8vw,120px);padding:clamp(26px,5vw,64px);display:grid;gap:26px;overflow:hidden}
.nolgo .word{font-size:clamp(56px,11vw,150px);display:flex;align-items:center;gap:.16em}
.nolgo .word .lf{font-size:.3em;color:var(--red-n)}
.nolgo .vine{color:var(--green-n)}
@media (max-width:800px){.two{grid-template-columns:minmax(0,1fr)}}
</style>
"""


def nest():
    """The mark with its pitch drawn in: each tip sits in the next notch."""
    w, p = brand.W, brand.PITCH
    leaves = "".join(f'<path fill="{c}" transform="translate(0 {i * p:.2f})" d="{brand.LEAF}"/>' for i, c in enumerate((brand.RED, brand.GREEN, "var(--text)")))
    lines = "".join(f'<line x1="-40" x2="{w + 40}" y1="{i * p:.2f}" y2="{i * p:.2f}"/>' for i in range(4))
    return (f'<svg viewBox="-60 -20 {w + 190} {3 * p + 40:.0f}" width="420" role="img" aria-label="The mark: one leaf stacked three times">{leaves}'
            f'<g stroke="var(--text-3)" stroke-width=".8" stroke-dasharray="1.5 4" stroke-linecap="round">{lines}<line x1="{w / 2}" x2="{w / 2}" y1="-14" y2="{3 * p + 14:.1f}"/></g>'
            f'<g font-family="Instrument Sans" font-size="9.5" font-weight="700" fill="var(--text)"><text x="{w + 46}" y="{p * .5 + 3:.0f}">today</text><text x="{w + 46}" y="{p * 1.5 + 3:.0f}">this week</text><text x="{w + 46}" y="{p * 2.5 + 3:.0f}">on record</text></g></svg>')


def main():
    red, green, ink = brand.RED, brand.GREEN, brand.INK
    sw = [("Red · today", red, "#fff", f"{ratio(red, '#ffffff'):.1f}:1 on white. The logo's red, unchanged. Only on what happened today."),
          ("Green · this week", green, "#fff", f"{ratio(green, '#ffffff'):.1f}:1 on white. The logo's green. Context, links, explainers."),
          ("Ink · on record", ink, "#fff", f"{ratio(ink, '#ffffff'):.1f}:1 on white. The wordmark's ink. Text, and everything older than a week."),
          ("White", "#FFFFFF", ink, "The page. No cream, no paper tint."),
          ("Mist", "#F4F4F5", ink, "Neutral grey for surfaces."),
          ("Night", "#150909", "#fff", f"The record's ground. Red lifts to #F0736B ({ratio('#F0736B', '#150909'):.1f}:1), green to #52B377 ({ratio('#52B377', '#150909'):.1f}:1).")]
    swatches = "".join(f'<div style="background:{c};color:{t}"><b>{n}</b><span>{c}</span><span style="opacity:.85">{note}</span></div>' for n, c, t, note in sw)
    sample = build.STORIES[0]
    body = f'''<div class="wrap">
<header class="phead">{build.word("leaf by leaf", "h1", "word-in")}<p>The identity of The Times of Palestine, grown from the three leaves of its logo. Take the logo away and the page is still theirs.</p></header>

<section class="bk"><span class="bk-n">01 · THE MARK</span>{build.word("one leaf, three times")}
<p>The supplied mark is a single shape, a pair of leaves on one stem, stacked three times. The stack is exactly as tall as three leaves: the tip of each one sits in the notch of the next. Nothing was redrawn. The site takes the shape and the order as they are.</p>
<div class="two"><div class="plate">{nest()}</div>
<ul class="facts"><li><i class="lf a-now"></i><span><b>Red is today.</b> Anything reported in the last 24 hours wears the top leaf.</span></li><li><i class="lf a-week"></i><span><b>Green is this week.</b> Stories still growing: follow-ups, context, explainers.</span></li><li><i class="lf a-rec"></i><span><b>Black is on the record.</b> Older than a week, and still true.</span></li><li><span style="font-weight:700;font-size:22px">1 : {brand.W / brand.PITCH:.2f}</span><span>Depth to width of one leaf. Every leaf on the site keeps it.</span></li></ul></div>
<div class="two" style="margin-block-start:14px"><div class="plate flip" style="background:var(--surface);box-shadow:inset 0 0 0 1px var(--line)"><img class="logo-l" src="assets/logo.svg" alt="" width="1597" height="257"><img class="logo-d" src="assets/logo-inverse.svg" alt="" width="1597" height="257"></div><div class="plate" style="background:#150909"><img src="assets/logo-inverse.svg" alt="" width="1597" height="257"></div></div>
</section>

<section class="bk"><span class="bk-n">02 · THE SHAPES</span>{build.word("everything is a leaf")}
<p>One blade of the mark, squared up, is a rectangle with two opposite corners rounded. That is the only frame on the site: photographs, buttons, chips, boxes. Neighbours lean opposite ways, as the two blades of a leaf do. Point at one and it turns over.</p>
<div class="parts">
<div><div class="demo"><i class="lf a-now" style="font-size:64px"></i></div><div><h3>The leaf</h3><p>Marks every tag, subhead and section word. Its colour is the story's age. It dips when you point at the story.</p></div></div>
<div><div class="demo"><span class="ph" style="inline-size:170px;aspect-ratio:16/10;background:var(--green)"></span></div><div><h3>The blade</h3><p>Every photograph and box. Two soft corners, two firm ones. Hover turns it over.</p></div></div>
<div><div class="demo" style="inline-size:100%"><div class="vine a-week" style="inline-size:100%"></div></div><div><h3>The vine</h3><p>Leaves tip to tip in a row: the border between today, this week and the record.</p></div></div>
<div><div class="demo"><div class="stem" style="block-size:96px;inline-size:40px;padding:0"></div></div><div><h3>The stem</h3><p>The latest stories hang off one line that runs red to green to black, newest at the top.</p></div></div>
</div></section>

<section class="bk"><span class="bk-n">03 · COLOUR</span>{build.word("three colours, one meaning each")}
<p>The colours are the logo's own and each does one job. Colour is never decoration here: it tells the reader when.</p>
<div class="sw">{swatches}</div></section>

<section class="bk"><span class="bk-n">04 · TYPE</span>{build.word("a word and a voice")}
<p>The wordmark is a fat-face Didone with ball terminals. Of ten display serifs set beside it, Abril Fatface was the closest in weight, contrast and terminals, so it carries the big lower-case words. Instrument Sans does everything else: its width axis sets headlines at 80 to 88 percent, which keeps a long headline to two lines, and at full width it reads cleanly at 19 pixels.</p>
<div class="tt">
<div><small>The word · Abril Fatface · always lower case</small><p class="word" style="font-size:clamp(54px,10vw,130px)">this week</p></div>
<div><small>Headlines · Instrument Sans · width 82 · weight 700</small><p style="font-size:clamp(28px,4.6vw,54px);font-stretch:82%;font-weight:700;line-height:1.04;letter-spacing:-.015em">{build.e(sample["title"])}</p></div>
<div><small>Reading · Instrument Sans · width 100 · weight 400</small><p style="font-size:19px;line-height:1.66;max-inline-size:64ch">{build.e(sample["body"][0])}</p></div>
</div></section>

<section class="bk"><span class="bk-n">05 · MOTION</span>{build.word("how it grows")}
<p>The opening draws a stem, then the three leaves unfurl from it in order: red, green, black. Between pages a three-colour line crosses the top. In discover, a story is told in three leaves: now, why, on record. Reduced-motion settings switch all of it off.</p>
<p><a class="btn" href="index.html?loader">Play the opening{build.ic("arrow")}</a></p></section>

<section class="bk"><span class="bk-n">06 · WITHOUT THE LOGO</span>{build.word("still theirs")}
<p>No mark and no wordmark below.</p>
<div class="nolgo"><span class="tag" style="color:var(--red-n)">{LF}<b style="color:#fff">Olive harvest</b></span><p class="word">{LF}<span>today</span></p><div class="vine"></div><span class="three" style="position:static"><i class="lf on"></i><i class="lf on"></i><i class="lf"></i></span></div>
</section>
</div>'''
    build.write("brand.html", build.shell("brand.html", f"Identity | {build.NAME}", "The identity of The Times of Palestine: leaf by leaf.", body, extra_head=CSS))


if __name__ == "__main__":
    main()
