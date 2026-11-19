#!/usr/bin/env bash
set -euo pipefail

# Checks the built CV page (/cv/), rendered from _data/cv.json by _layouts/cv_timeline.liquid.
#
# Usage: bash test/integration_cv.sh <built site directory>
#
# The data file is regenerated from the LaTeX CV, so the expected headline numbers are read out of
# _data/cv.json rather than hard-coded. Production builds minify the HTML onto very few lines, so the
# structural checks (which element holds a text, whether it sits inside a <details>) parse the page
# with Python's html.parser instead of relying on line breaks.

site="${1:?usage: $0 <built site directory>}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
data="${repo_root}/_data/cv.json"
page="${site}/cv/index.html"
home="${site}/index.html"

fail() {
  echo "FAIL: $*" >&2
  exit 1
}

[ -f "${page}" ] || fail "${page} does not exist"
[ -f "${home}" ] || fail "${home} does not exist"
[ -f "${data}" ] || fail "${data} does not exist"

# Download link to the PDF, with a download attribute on the same <a>.
grep -Eq '<a [^>]*href="?/assets/pdf/CV_Rattanasriampaipong\.pdf"?[^>]*download|<a [^>]*download[^>]*href="?/assets/pdf/CV_Rattanasriampaipong\.pdf"?' "${page}" ||
  fail 'no <a href="/assets/pdf/CV_Rattanasriampaipong.pdf" download> on the CV page'

grep -Eq 'id="?grants-noaa"?[ >]' "${page}" || fail 'no element with id="grants-noaa"'

grep -Eq 'Updated (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{4}' "${page}" ||
  fail 'no "Updated <Month> <YYYY>" line'

grep -q 'Description 1\.' "${page}" && fail 'the old placeholder text "Description 1." is still on the page'

# `|| true`: with no match grep exits 1, which pipefail would turn into a silent exit.
sections="$({ grep -o 'class="\?cv-section"\?[ >]' "${page}" || true; } | wc -l)"
[ "${sections}" -ge 18 ] || fail "expected at least 18 class=\"cv-section\", found ${sections}"

# The CV icon in the home page's social links (an <a> wrapping <i class="ai ai-cv">, from the cv_pdf key
# of _data/socials.yml) links to the CV page. The navbar's own "cv" link does not count.
grep -Eq '<a [^>]*href="/cv/"[^>]*>[[:space:]]*<i [^>]*class="[^"]*ai-cv[ "]' "${home}" ||
  fail 'the CV icon in the home page social links does not link to href="/cv/"'

# Headline numbers, from the data file.
python3 -I - "${data}" "${page}" <<'PY'
import json
import sys
from html.parser import HTMLParser

data_path, page_path = sys.argv[1], sys.argv[2]
with open(data_path, encoding="utf-8") as f:
    stats = json.load(f)["stats"]
with open(page_path, encoding="utf-8") as f:
    html = f.read()

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Page(HTMLParser):
    """Records, for every text node, the stack of open elements (tag, classes) above it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.texts = []

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        classes = (dict(attrs).get("class") or "").split()
        self.stack.append((tag, classes))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

    def handle_data(self, data):
        if data.strip():
            self.texts.append((data, list(self.stack)))


parser = Page()
parser.feed(html)
errors = []

stats_box = [t for t, stack in parser.texts if any("cv-stats" in c for _, c in stack)]
stats_text = " ".join(" ".join(stats_box).split())
for label, expected in (
    ("funding", stats["funding"]),
    ("citations", stats["citations"]),
    ("students", stats["students"] + "+"),
):
    if expected not in stats_text:
        errors.append(f"stats line does not show {label} {expected!r} (stats text: {stats_text!r})")

note = "$200,000 over two years"
holders = [stack for t, stack in parser.texts if note in t]
if not holders:
    errors.append(f"text {note!r} not found")
for stack in holders:
    # Notes are always visible: outside any <details>, or in its <summary>, never in the folded body.
    tags = [tag for tag, _ in stack]
    if "details" in tags and "summary" not in tags[tags.index("details") :]:
        errors.append(f"text {note!r} is folded inside a <details>")
    if not any("cv-note" in c for _, c in stack):
        errors.append(f"text {note!r} is not inside an element with class cv-note")

if errors:
    for e in errors:
        print("FAIL: " + e, file=sys.stderr)
    sys.exit(1)
PY

# Publication details, cross-links and the filter bar (Task 7): the element with the given id, found with the
# same parser, must contain the given link texts / hrefs / texts / attributes.
python3 -I - "${page}" <<'PY2'
import sys
from html.parser import HTMLParser

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Subtree(HTMLParser):
    """Collects, for the element with the given id, its own attributes, link (href, text) pairs and all text."""

    def __init__(self, wanted):
        super().__init__(convert_charrefs=True)
        self.wanted, self.depth, self.attrs, self.done = wanted, 0, None, False
        self.links, self.text, self._href, self._link_text = [], [], None, []

    def handle_starttag(self, tag, attrs):
        if self.done:
            return
        a = dict(attrs)
        if self.attrs is None and a.get("id") == self.wanted:
            self.attrs, self.depth = a, 0
        if self.attrs is None:
            return
        if tag in VOID:
            return
        self.depth += 1
        if tag == "a":
            self._href, self._link_text = a.get("href"), []

    def handle_endtag(self, tag):
        if self.attrs is None or self.done or tag in VOID:
            return
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._link_text).split())))
            self._href = None
        self.depth -= 1
        if self.depth == 0:
            self.done = True

    def handle_data(self, data):
        if self.attrs is None or self.done:
            return
        self.text.append(data)
        if self._href is not None:
            self._link_text.append(data)


def element(page_html, element_id):
    parser = Subtree(element_id)
    parser.feed(page_html)
    return parser


with open(sys.argv[1], encoding="utf-8") as f:
    html = f.read()

errors = []


def need(element_id):
    el = element(html, element_id)
    if el.attrs is None:
        errors.append(f"no element with id={element_id!r}")
        return None
    return el


def link_texts(el):
    # The decorative arrow is aria-hidden; compare on the label without it.
    return [(href, text.removesuffix("→").strip()) for href, text in el.links]


nutrient = need("pub-Rattanasriampaipong2025")
if nutrient:
    if nutrient.attrs.get("data-first-author") != "true":
        errors.append("pub-Rattanasriampaipong2025: data-first-author is not 'true'")
    if nutrient.attrs.get("data-status") != "published":
        errors.append("pub-Rattanasriampaipong2025: data-status is not 'published'")
    links = link_texts(nutrient)
    for label in ("DOI", "PDF", "Project page", "Code"):
        if label not in [t for _, t in links]:
            errors.append(f"pub-Rattanasriampaipong2025: no link with text {label!r} (links: {links})")
    if ("/projects/nutrient-effect/", "Project page") not in links:
        errors.append(f"pub-Rattanasriampaipong2025: Project page does not link to /projects/nutrient-effect/ (links: {links})")
    if ("https://doi.org/10.1029/2025gl115237", "DOI") not in links:
        errors.append(f"pub-Rattanasriampaipong2025: DOI link is not https://doi.org/10.1029/2025gl115237 (links: {links})")
    if not any(t == "PDF" and h.startswith("/assets/pdf/") for h, t in links):
        errors.append(f"pub-Rattanasriampaipong2025: PDF link does not point into /assets/pdf/ (links: {links})")
    if "Abstract" not in " ".join(nutrient.text):
        errors.append("pub-Rattanasriampaipong2025: no 'Abstract' text")

# No matching project page: no Project page and no PDF link.
texas = need("pub-Rattanasriampaipong2026")
if texas:
    labels = [t for _, t in link_texts(texas)]
    for label in ("Project page", "PDF"):
        if label in labels:
            errors.append(f"pub-Rattanasriampaipong2026: unexpected {label!r} link (links: {link_texts(texas)})")

elling = need("pub-Elling2026")
if elling:
    text = " ".join(elling.text)
    for needle in ("Journal cover", "My contribution"):
        if needle not in text:
            errors.append(f"pub-Elling2026: no {needle!r} text")

course = need("teaching-ocng-251")
if course:
    if ("/courses/the_blue_planet/", "Course page") not in link_texts(course):
        errors.append(f"teaching-ocng-251: no 'Course page' link to /courses/the_blue_planet/ (links: {link_texts(course)})")

course = need("teaching-geos-470")
if course:
    if ("/courses/data_methods_geos/", "Course page") not in link_texts(course):
        errors.append(f"teaching-geos-470: no 'Course page' link to /courses/data_methods_geos/ (links: {link_texts(course)})")

# The filter bar: hidden until the script shows it, with one real button per filter, "All" pressed.
class Tags(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


tags = Tags()
tags.feed(html)
bars = [a for t, a in tags.tags if "cv-filters" in (a.get("class") or "").split()]
if len(bars) != 1:
    errors.append(f"expected one .cv-filters, found {len(bars)}")
elif "hidden" not in bars[0]:
    errors.append(".cv-filters does not carry the hidden attribute")
buttons = {a.get("data-filter"): a for t, a in tags.tags if t == "button" and a.get("data-filter")}
for name in ("all", "first-author", "published", "under-review"):
    button = buttons.get(name)
    if button is None:
        errors.append(f"no <button data-filter={name!r}>")
    elif button.get("type") != "button":
        errors.append(f"button {name!r} has no type=button")
    elif button.get("aria-pressed") != ("true" if name == "all" else "false"):
        errors.append(f"button {name!r} has aria-pressed={button.get('aria-pressed')!r}")

if errors:
    for e in errors:
        print("FAIL: " + e, file=sys.stderr)
    sys.exit(1)
PY2

echo "PASS: CV page checks (${sections} sections)"
