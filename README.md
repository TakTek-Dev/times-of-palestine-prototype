# The Times of Palestine — redesign prototype

Static prototype of a redesign of [paltimesnews.com](https://paltimesnews.com), laid out on the structure of indiatimes.com and dressed in the client's own identity: **«leaf by leaf»**.

- The logo is one leaf stacked three times: red, green, ink. The site reads it as time. **Red is today, green is this week, black is on the record.** Every story wears the leaf of its age.
- Every frame is a leaf blade: two opposite corners round, neighbours lean opposite ways, hover turns the leaf over.
- Type: Abril Fatface for the big lower-case words, Instrument Sans for everything else.
- 40 sourced stories (links at the end of each story), photographs from Wikimedia Commons with credit and licence; archive photos are labelled as such.

The identity is documented on [`brand.html`](brand.html). Add `?loader` to any page to replay the opening.

## Build

```bash
python tools/edition.py   # research/news.json -> research/edition.json + assets/img
python tools/build.py     # every .html page
python tools/links.py     # internal link check
```

Never edit generated HTML by hand. Preview with `python -m http.server 8292`.
