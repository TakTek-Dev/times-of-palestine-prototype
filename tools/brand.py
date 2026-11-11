"""The Times of Palestine mark as geometry, and the parts derived from it.

The supplied mark is one shape, a leaf pair, stacked three times at a pitch
equal to its own depth, so each leaf's tip sits in the notch of the next:
red, green, ink.  The site reads the stack as time: red is today, green is
this week, ink is the record.

Run: python tools/brand.py
"""
import pathlib, shutil, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
OLD = ROOT.parent / "Times of Palestine" / "img" / "brand"   # the client's supplied artwork

W, PITCH = 170.21, 73.71
RED, GREEN, INK = "#CC3333", "#006633", "#190707"
# One leaf pair, exactly as drawn in the supplied logo.
LEAF = ("M114.44 24.7C91.32 28.16 86.09 49.46 85.1 62.82C84.12 49.46 78.89 28.16 55.76 24.7C19.03 18.57 10.04 10.41 0 0"
        "C.79 16.28 0 52.53 47.04 53.29C84.58 53.9 85.09 73.71 85.09 73.71S85.62 53.9 123.17 53.29C170.21 52.53 169.41 16.28 170.21 0"
        "C160.16 10.41 151.18 18.57 114.44 24.7Z")


def leaf(cls="lf", fill="currentColor"):
    return f'<svg class="{cls}" viewBox="0 0 {W} {PITCH}" aria-hidden="true"><path fill="{fill}" d="{LEAF}"/></svg>'


def mark(size=64, cls="mark", on_dark=False):
    last = "#fff" if on_dark else INK
    red = "#EC6058" if on_dark else RED
    green = "#41A265" if on_dark else GREEN
    # each leaf sits in its own group so CSS can animate the path without losing its place in the stack
    leaves = "".join(f'<g transform="translate(0 {i * PITCH:.2f})"><path class="m{i}" fill="{c}" d="{LEAF}"/></g>' for i, c in enumerate((red, green, last)))
    return f'<svg class="{cls}" viewBox="0 0 {W} {PITCH * 3:.2f}" height="{size}" aria-hidden="true">{leaves}</svg>'


def mask_uri():
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {PITCH}"><path d="{LEAF}"/></svg>'
    return "url(\"data:image/svg+xml," + urllib.parse.quote(svg, safe="/:=' ") + "\")"


def main():
    assets = ROOT / "assets"
    assets.mkdir(exist_ok=True)
    for name in ("logo.svg", "logo-inverse.svg", "mark.svg"):
        shutil.copy(OLD / name, assets / name)
    pad = 60
    box = PITCH * 3 + 2 * pad
    tile = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {box:.1f} {box:.1f}"><rect width="{box:.1f}" height="{box:.1f}" rx="72" fill="#fff"/>'
            f'<g transform="translate({(box - W) / 2:.1f} {pad})">' +
            "".join(f'<path fill="{c}" transform="translate(0 {i * PITCH:.2f})" d="{LEAF}"/>' for i, c in enumerate((RED, GREEN, INK))) + "</g></svg>")
    (ROOT / "favicon.svg").write_text(tile, encoding="utf-8")
    (assets / "leaf.css").write_text(f":root{{--leaf-mask:{mask_uri()}}}\n", encoding="utf-8")


if __name__ == "__main__":
    main()
