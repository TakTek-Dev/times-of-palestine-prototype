"""Check every internal href/src in the built pages resolves to a file."""
import pathlib, re, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
bad, n = [], 0
for page in list(ROOT.glob("*.html")) + list(ROOT.glob("*/*.html")):
    if "tools" in page.parts:
        continue
    for ref in re.findall(r'(?:href|src)="([^"#]+)', page.read_text(encoding="utf-8")):
        if re.match(r"(https?:|mailto:|data:)", ref):
            continue
        n += 1
        target = (page.parent / urllib.parse.unquote(ref.split("?")[0])).resolve()
        if not target.exists():
            bad.append((page.relative_to(ROOT).as_posix(), ref))
print(n, "internal references,", len(bad), "broken")
for b in bad[:30]:
    print(" ", *b)
