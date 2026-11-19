#!/usr/bin/env bash
set -euo pipefail

# Checks the built CV page (/cv/), rendered from _data/cv.json by _layouts/cv_page.liquid.
#
# Usage: bash test/integration_cv.sh <built site directory>
#
# This is the local fixture test for today's data: it names particular entries (pub-Elling2026, grants-noaa,
# the 2023–2025 date, ...) and so may need updating when the LaTeX CV changes those entries. It is not run in CI.
# CI (the Deploy workflow) runs test/cv_page_check.py, which derives every expectation from the data files and
# hard-codes nothing about today's CV.
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

[ -s "${site}/assets/js/cv.js" ] || fail "${site}/assets/js/cv.js (the CV page script) is missing from the build"

grep -Eq 'Updated (January|February|March|April|May|June|July|August|September|October|November|December) [0-9]{4}' "${page}" ||
  fail 'no "Updated <Month> <YYYY>" line'

grep -q 'Description 1\.' "${page}" && fail 'the old placeholder text "Description 1." is still on the page'

# `|| true`: with no match grep exits 1, which pipefail would turn into a silent exit.
sections="$({ grep -o 'class="\?cv-section"\?[ >]' "${page}" || true; } | wc -l)"
[ "${sections}" -ge 18 ] || fail "expected at least 18 class=\"cv-section\", found ${sections}"

# The CV icon in the home page's social links (an <a> wrapping <i class="ai ai-cv">, from the `cv` entry
# of _data/socials.yml) links to the CV page and is named "CV". The navbar's own "cv" link does not count.
grep -Eq '<a [^>]*href="/cv/"[^>]*>[[:space:]]*<i [^>]*class="[^"]*ai-cv[ "]' "${home}" ||
  fail 'the CV icon in the home page social links does not link to href="/cv/"'
grep -Eq '<a [^>]*href="/cv/"[^>]*title="?CV"?[ >]|<a [^>]*title="?CV"?[^>]*href="/cv/"' "${home}" ||
  fail 'the CV icon in the home page social links is not titled "CV"'
grep -q 'title="\?Cv pdf' "${home}" && fail 'a social link on the home page is still titled "Cv pdf"'

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
    # Notes are always visible: they sit in the card's head, outside any <details>.
    if any(tag == "details" for tag, _ in stack):
        errors.append(f"text {note!r} is inside a <details>")
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
for name in ("all", "first-author", "co-author", "published", "under-review"):
    button = buttons.get(name)
    if button is None:
        errors.append(f"no <button data-filter={name!r}>")
    elif button.get("type") != "button":
        errors.append(f"button {name!r} has no type=button")
    elif button.get("aria-pressed") != ("true" if name == "all" else "false"):
        errors.append(f"button {name!r} has aria-pressed={button.get('aria-pressed')!r}")
labels = {"all": "All", "first-author": "First author", "co-author": "Co-author", "published": "Published", "under-review": "Under review / preprint"}
if [a.get("data-filter") for t, a in tags.tags if t == "button" and a.get("data-filter")] != list(labels):
    errors.append("the filter buttons are not, in order, " + ", ".join(labels))

if errors:
    for e in errors:
        print("FAIL: " + e, file=sys.stderr)
    sys.exit(1)
PY2

# Cards and the section panel (Revision 2): the page parsed into a small element tree.
python3 -I - "${data}" "${page}" "${repo_root}/_data/cv_figures.yml" <<'PY3'
import json
import sys
from html.parser import HTMLParser

data_path, page_path, figures_path = sys.argv[1], sys.argv[2], sys.argv[3]
with open(data_path, encoding="utf-8") as f:
    data = json.load(f)
with open(page_path, encoding="utf-8") as f:
    html = f.read()

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Node:
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.children = tag, attrs, parent, []
        self.classes = (attrs.get("class") or "").split()

    def walk(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.walk()

    def text(self):
        return " ".join(
            "".join(c if isinstance(c, str) else c.text() for c in self.children).split()
        )

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, dict(attrs), self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, text):
        self.cur.children.append(text)


tree = Tree()
tree.feed(html)
nodes = list(tree.root.walk())
errors = []


def with_class(name, within=None):
    return [n for n in (within.walk() if within else nodes) if name in n.classes]


# The wrapper names the landing section.
wrappers = with_class("cv-page")
if len(wrappers) != 1:
    errors.append(f"expected one .cv-page, found {len(wrappers)}")
elif wrappers[0].attrs.get("data-landing") != "publications":
    errors.append(f".cv-page has data-landing={wrappers[0].attrs.get('data-landing')!r}, expected 'publications'")

# The timeline's classes are gone.
for old in ("cv-row", "cv-when", "cv-rail"):
    if with_class(old):
        errors.append(f"{len(with_class(old))} element(s) still have class {old!r}")

# Without the script every section is visible: none carries the hidden attribute in the built HTML.
sections = [n for n in with_class("cv-section") if n.tag == "section"]
for s in sections:
    if "hidden" in s.attrs:
        errors.append(f"section {s.attrs.get('id')!r} carries the hidden attribute")

# The page script (Task 13): loaded with defer; section headings take focus; a polite live region for announcements.
scripts = [n for n in nodes if n.tag == "script" and (n.attrs.get("src") or "").split("?")[0].endswith("/assets/js/cv.js")]
if len(scripts) != 1:
    errors.append(f"expected one <script src=\".../assets/js/cv.js\">, found {len(scripts)}")
elif "defer" not in scripts[0].attrs:
    errors.append("the CV script is not loaded with defer")
for s in sections:
    headings = [n for n in s.walk() if n.tag == "h2" and "cv-section-title" in n.classes]
    if len(headings) != 1 or headings[0].attrs.get("tabindex") != "-1":
        errors.append(f"section {s.attrs.get('id')!r}: its <h2 class=\"cv-section-title\"> lacks tabindex=\"-1\"")
lives = [n for n in nodes if n.attrs.get("aria-live") == "polite" and "cv-live" in n.classes]
if len(lives) != 1:
    errors.append(f"expected one .cv-live with aria-live=\"polite\", found {len(lives)}")
elif "cv-sr-only" not in lives[0].classes:
    errors.append(".cv-live is not visually hidden (class cv-sr-only)")

# The section panel: a named <nav class="cv-nav"> with one link per section, in page order.
navs = [n for n in with_class("cv-nav") if n.tag == "nav"]
if len(navs) != 1:
    errors.append(f"expected one <nav class=\"cv-nav\">, found {len(navs)}")
else:
    nav = navs[0]
    if not (nav.attrs.get("aria-label") or "").strip():
        errors.append("<nav class=\"cv-nav\"> has no aria-label")
    links = [n for n in with_class("cv-nav-link", nav) if n.tag == "a"]
    section_ids = [s.attrs.get("id") for s in sections]
    hrefs = [a.attrs.get("href") for a in links]
    if hrefs != ["#" + i for i in section_ids]:
        errors.append(f"panel links {hrefs} do not match the sections {section_ids} one to one")
    for a in links:
        if a.attrs.get("href") != "#" + (a.attrs.get("data-section") or ""):
            errors.append(f"panel link {a.attrs.get('href')!r} has data-section={a.attrs.get('data-section')!r}")
    by_id = {a.attrs.get("data-section"): a for a in links}
    for section in data["sections"]:
        a = by_id.get(section["id"])
        if a is None:
            continue
        expected = sum(len(g.get("entries") or []) for g in section.get("groups") or [])
        counts = with_class("cv-nav-count", a)
        if expected == 0 and counts:
            errors.append(f"panel link for {section['id']!r} shows a count but the section has no entries")
        elif expected > 0 and [c.text() for c in counts] != [str(expected)]:
            errors.append(f"panel link for {section['id']!r} shows count {[c.text() for c in counts]}, expected {expected}")
    if "publications" not in by_id:
        errors.append("no panel link for publications")
    if "personal-interests" not in by_id:
        errors.append("no panel link for personal-interests")
    elif with_class("cv-nav-count", by_id["personal-interests"]):
        errors.append("the Personal Interests panel link has a count")

by_element_id = {n.attrs["id"]: n for n in nodes if n.attrs.get("id")}

# An ordinary card: the NOAA fellowship, with its date in the head and its note outside any <details>.
noaa = by_element_id.get("grants-noaa")
if noaa is None:
    errors.append("no element with id='grants-noaa'")
else:
    if "cv-card" not in noaa.classes:
        errors.append("grants-noaa is not a .cv-card")
    heads = [c for c in noaa.children if isinstance(c, Node) and "cv-card-head" in c.classes]
    if len(heads) != 1:
        errors.append(f"grants-noaa has {len(heads)} .cv-card-head children, expected 1")
    elif [d.text() for d in with_class("cv-date", heads[0])] != ["2023–2025"]:
        errors.append(f"grants-noaa: .cv-date in the head is {[d.text() for d in with_class('cv-date', heads[0])]}")
    notes = [n for n in with_class("cv-note", noaa) if "$200,000 over two years" in n.text()]
    if not notes:
        errors.append("grants-noaa: no .cv-note with '$200,000 over two years'")
    for n in notes:
        if any(a.tag == "details" for a in n.ancestors()):
            errors.append("grants-noaa: the note is inside a <details>")
    # Nothing to fold: no <details> at all.
    if any(n.tag == "details" for n in noaa.walk()):
        errors.append("grants-noaa has nothing to fold but has a <details>")

# A card without a date has no .cv-date at all.
education = by_element_id.get("education-texas-a-m-university")
if education is None:
    errors.append("no element with id='education-texas-a-m-university'")
elif with_class("cv-date", education):
    errors.append("education-texas-a-m-university has a .cv-date but no date")

# The badge sits in the tag row under the citation, outside the <details>; no tag row is empty.
elling = by_element_id.get("pub-Elling2026")
if elling is None:
    errors.append("no element with id='pub-Elling2026'")
else:
    rows = [r for r in with_class("cv-tags", elling) if r.tag == "p"]
    if not any("Journal cover" in r.text() for r in rows):
        errors.append("pub-Elling2026: 'Journal cover' is not in a <p class=\"cv-tags\">")
    for r in rows:
        if any(a.tag == "details" for a in r.ancestors()):
            errors.append("pub-Elling2026: .cv-tags is inside a <details>")
# Figures (Task 12): drawn from _data/cv_figures.yml inside the opened card, after the abstract and before the links.
def figures_of(card_id):
    card = by_element_id.get(card_id)
    if card is None:
        errors.append(f"no element with id={card_id!r}")
        return None, []
    return card, [n for n in card.walk() if n.tag == "figure"]


card, figs = figures_of("pub-Rattanasriampaipong2025")
if card is not None:
    if len(figs) != 1:
        errors.append(f"pub-Rattanasriampaipong2025: expected 1 figure, found {len(figs)}")
    for fig in figs:
        if "cv-figure" not in fig.classes:
            errors.append("pub-Rattanasriampaipong2025: the figure is not a .cv-figure")
        if not any(a.tag == "details" for a in fig.ancestors()):
            errors.append("pub-Rattanasriampaipong2025: the figure is not inside the <details>")
        if not any("cv-figures" in a.classes for a in fig.ancestors()):
            errors.append("pub-Rattanasriampaipong2025: the figure is not inside .cv-figures")
        imgs = [n for n in fig.walk() if n.tag == "img"]
        caps = [n for n in fig.walk() if n.tag == "figcaption"]
        if len(imgs) != 1:
            errors.append(f"pub-Rattanasriampaipong2025: figure holds {len(imgs)} img elements")
        else:
            img = imgs[0]
            if not img.attrs.get("src", "").endswith("nutrient-effect/fig1.png"):
                errors.append(f"pub-Rattanasriampaipong2025: figure src is {img.attrs.get('src')!r}")
            if not (img.attrs.get("alt") or "").strip():
                errors.append("pub-Rattanasriampaipong2025: the figure image has no alt text")
            if img.attrs.get("loading") != "lazy":
                errors.append("pub-Rattanasriampaipong2025: the figure image is not loading=lazy")
            if img.attrs.get("decoding") != "async":
                errors.append("pub-Rattanasriampaipong2025: the figure image is not decoding=async")
            if "data-zoomable" not in img.attrs:
                errors.append("pub-Rattanasriampaipong2025: the figure image lacks data-zoomable (click to enlarge)")
        if len(caps) != 1 or not caps[0].text():
            errors.append("pub-Rattanasriampaipong2025: the figure has no non-empty figcaption")
    # Order inside .cv-more: abstract, then figures, then links.
    more = [n for n in card.walk() if "cv-more" in n.classes]
    if len(more) == 1:
        order = [c.classes[0] for c in more[0].children if isinstance(c, Node) and c.classes and c.classes[0] in ("cv-abstract", "cv-figures", "cv-links")]
        if order != ["cv-abstract", "cv-figures", "cv-links"]:
            errors.append(f"pub-Rattanasriampaipong2025: .cv-more order is {order}, expected abstract, figures, links")
    summaries = [n for n in card.walk() if n.tag == "summary"]
    if len(summaries) != 1 or "figures" not in summaries[0].text().lower():
        errors.append("pub-Rattanasriampaipong2025: the summary does not mention figures")

card, figs = figures_of("pub-Rattanasriampaipong2022")
if card is not None:
    if len(figs) != 2:
        errors.append(f"pub-Rattanasriampaipong2022: expected 2 figures, found {len(figs)}")
    summaries = [n for n in card.walk() if n.tag == "summary"]
    if len(summaries) != 1 or "figures" not in summaries[0].text().lower():
        errors.append("pub-Rattanasriampaipong2022: the summary does not mention figures")

# An entry with no figures in _data/cv_figures.yml draws none and its summary does not promise any. The file's
# top-level keys are read with a pattern so this test needs no YAML library.
import re

with open(figures_path, encoding="utf-8") as f:
    figure_keys = set(re.findall(r"^([^\s#][^:]*):", f.read(), re.M))
for card in with_class("cv-card"):
    if card.attrs.get("id") in figure_keys:
        continue
    if [n for n in card.walk() if n.tag == "figure" or "cv-figures" in n.classes]:
        errors.append(f"{card.attrs.get('id')}: has figures but none are listed in cv_figures.yml")
    for n in card.walk():
        if n.tag == "summary" and "figures" in n.text().lower():
            errors.append(f"{card.attrs.get('id')}: the summary mentions figures but none are listed")

# A software entry's paper is linked to its publication card (the entry whose paper is Rattanasriampaipong2025).
software = [e for s in data["sections"] for g in s.get("groups") or [] for e in g.get("entries") or [] if e.get("paper") == "Rattanasriampaipong2025"]
if len(software) != 1:
    errors.append(f"expected one entry with paper 'Rattanasriampaipong2025', found {len(software)}")
else:
    card = by_element_id.get(software[0]["id"])
    hrefs = [n.attrs.get("href") for n in card.walk() if n.tag == "a"] if card else []
    if "#pub-Rattanasriampaipong2025" not in hrefs:
        errors.append(f"{software[0]['id']}: no <a href=\"#pub-Rattanasriampaipong2025\"> (links: {hrefs})")
    elif hrefs[0] != "#pub-Rattanasriampaipong2025":
        errors.append(f"{software[0]['id']}: the Paper link is not the entry's first link (links: {hrefs})")

# Ids are unique across the page (sections, their -heading ids, entries and their -title ids).
seen = {}
for n in nodes:
    i = n.attrs.get("id")
    if i:
        seen[i] = seen.get(i, 0) + 1
duplicates = sorted(i for i, c in seen.items() if c > 1)
if duplicates:
    errors.append(f"duplicate ids: {duplicates}")

# Summaries name what opens and point at their own card's title.
for summary in (n for n in nodes if n.tag == "summary"):
    card = next((a for a in summary.ancestors() if "cv-card" in a.classes), None)
    card_id = card.attrs.get("id") if card else None
    label = summary.text()
    if not label or label == "Details":
        errors.append(f"{card_id!r}: summary reads {label!r}")
    described = summary.attrs.get("aria-describedby")
    if card_id:
        if described != f"{card_id}-title":
            errors.append(f"{card_id!r}: summary has aria-describedby={described!r}, expected {card_id + '-title'!r}")
        else:
            target = by_element_id.get(described)
            if target is None or "cv-title" not in target.classes or card not in target.ancestors():
                errors.append(f"{card_id!r}: aria-describedby does not point at the .cv-title of the same card")

# Citations read cleanly: no doubled full stop where the year used to separate the authors from the title.
for c in with_class("cv-pub"):
    if ".." in c.text():
        errors.append(f"citation has a doubled full stop: {c.text()[:80]!r}")
for r in with_class("cv-tags"):
    if not r.text():
        errors.append(f"empty .cv-tags in {next((a.attrs.get('id') for a in r.ancestors() if 'cv-card' in a.classes), '?')!r}")

if errors:
    for e in errors:
        print("FAIL: " + e, file=sys.stderr)
    sys.exit(1)
PY3

# Tag row (Task 11): author role, Preprint and citation tags, read against papers.bib and citations.yml.
python3 -I - "${repo_root}" "${page}" <<'PY4'
import json
import re
import sys
from html.parser import HTMLParser

repo, page_path = sys.argv[1], sys.argv[2]
with open(page_path, encoding="utf-8") as f:
    html = f.read()
with open(repo + "/_bibliography/papers.bib", encoding="utf-8") as f:
    bib = f.read()
with open(repo + "/_data/citations.yml", encoding="utf-8") as f:
    citations = f.read()
with open(repo + "/_data/socials.yml", encoding="utf-8") as f:
    userid = re.search(r"^scholar_userid:\s*(\S+)", f.read(), re.M).group(1)

# The Scholar id and the count for the first-author paper, read straight from the two data files.
entry = re.search(r"@article\{Rattanasriampaipong2025,.*?\n\}", bib, re.S).group(0)
article_id = re.search(r"google_scholar_id\s*=\s*\{([^}]+)\}", entry).group(1)
count = re.search(r"^  " + re.escape(userid + ":" + article_id) + r":\n    citations: (\d+)", citations, re.M).group(1)

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Card(HTMLParser):
    """For the card with the given id: every element inside its <p class="cv-tags"> as (tag, attrs, text)."""

    def __init__(self, wanted):
        super().__init__(convert_charrefs=True)
        self.wanted, self.in_card, self.depth, self.in_row, self.row_depth = wanted, False, 0, False, 0
        self.items, self.stack, self.rows = [], [], 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if not self.in_card and a.get("id") == self.wanted:
            self.in_card, self.depth = True, 0
        if not self.in_card or tag in VOID:
            return
        self.depth += 1
        if tag == "p" and "cv-tags" in (a.get("class") or "").split():
            self.in_row, self.row_depth, self.rows = True, self.depth, self.rows + 1
        elif self.in_row:
            item = [tag, a, ""]
            self.items.append(item)
            self.stack.append(item)

    def handle_endtag(self, tag):
        if not self.in_card or tag in VOID:
            return
        if self.in_row and self.depth == self.row_depth:
            self.in_row = False
        elif self.in_row and self.stack:
            self.stack.pop()
        self.depth -= 1
        if self.depth == 0:
            self.in_card = False

    def handle_data(self, data):
        if self.in_row:
            for item in self.stack:
                item[2] += data


def row(card_id):
    parser = Card(card_id)
    parser.feed(html)
    return parser


def classes(item):
    return (item[1].get("class") or "").split()


errors = []

first = row("pub-Rattanasriampaipong2025")
roles = [" ".join(i[2].split()) for i in first.items if "cv-tag-role" in classes(i)]
if roles != ["First author"]:
    errors.append(f"pub-Rattanasriampaipong2025: role tags {roles}, expected ['First author']")
scholar = [i for i in first.items if i[0] == "a" and "cv-tag-metric" in classes(i)]
if len(scholar) != 1:
    errors.append(f"pub-Rattanasriampaipong2025: expected one Google Scholar tag, found {len(scholar)}")
else:
    href = scholar[0][1].get("href", "")
    if "citation_for_view=" not in href or article_id not in href:
        errors.append(f"pub-Rattanasriampaipong2025: Scholar href {href!r} lacks citation_for_view= and the article id")
    number = [i[2] for i in first.items if i[0] == "b" and i[2].strip() == count]
    if not number:
        errors.append(f"pub-Rattanasriampaipong2025: the Scholar tag does not show the count {count} from citations.yml")
for cls, label in (("altmetric-embed", "Altmetric"), ("__dimensions_badge_embed__", "Dimensions")):
    n = len([i for i in first.items if cls in classes(i)])
    if n != 1:
        errors.append(f"pub-Rattanasriampaipong2025: expected one .{cls} ({label}), found {n}")
# Tag order: role, then (badge), then metrics; the role comes first.
if first.items and "cv-tag-role" not in classes(first.items[0]):
    errors.append("pub-Rattanasriampaipong2025: the role tag is not first in the row")
# The metric tags, in order: Google Scholar, then Dimensions, then Altmetric.
metric_order = []
for i in first.items:
    for cls, label in (("cv-tag-metric", "Google Scholar"), ("__dimensions_badge_embed__", "Dimensions"), ("altmetric-embed", "Altmetric")):
        if cls in classes(i):
            metric_order.append(label)
if metric_order != ["Google Scholar", "Dimensions", "Altmetric"]:
    errors.append(f"pub-Rattanasriampaipong2025: metric tags in the order {metric_order}, expected Google Scholar, Dimensions, Altmetric")

elling = row("pub-Elling2026")
roles = [" ".join(i[2].split()) for i in elling.items if "cv-tag-role" in classes(i)]
if roles != ["Co-author"]:
    errors.append(f"pub-Elling2026: role tags {roles}, expected ['Co-author']")
kinds = [("badge" if "cv-badge" in classes(i) else "role" if "cv-tag-role" in classes(i) else None) for i in elling.items]
if [k for k in kinds if k] != ["role", "badge"]:
    errors.append(f"pub-Elling2026: the row does not hold the role tag then the badge (got {[k for k in kinds if k]})")

preprint = row("pub-Rattanasriampaipong2026")
roles = [" ".join(i[2].split()) for i in preprint.items if "cv-tag-role" in classes(i)]
if roles != ["First author"]:
    errors.append(f"pub-Rattanasriampaipong2026: role tags {roles}, expected ['First author']")
preprint_at = [n for n, i in enumerate(preprint.items) if " ".join(i[2].split()) == "Preprint" and "cv-tag" in classes(i)]
role_at = [n for n, i in enumerate(preprint.items) if "cv-tag-role" in classes(i)]
if not preprint_at:
    errors.append("pub-Rattanasriampaipong2026: no 'Preprint' tag")
elif role_at and preprint_at[0] < role_at[0]:
    errors.append("pub-Rattanasriampaipong2026: the 'Preprint' tag comes before the role tag")
# No metric tags while the preprint is not in papers.bib (matched by DOI, as the page does); once it is added there,
# the tags are expected and this check stands down.
with open(repo + "/_data/cv.json", encoding="utf-8") as f:
    cv_data = json.load(f)
preprint_doi = next(
    (e["pub"].get("doi") for s in cv_data["sections"] for g in s.get("groups") or [] for e in g.get("entries") or [] if e["id"] == "pub-Rattanasriampaipong2026" and e.get("pub")),
    None,
)
bib_dois = {d.strip().lower().removeprefix("https://doi.org/") for d in re.findall(r"\bdoi\s*=\s*[{\"]([^}\"]+)", bib, re.I)}
if not preprint_doi or preprint_doi.lower() not in bib_dois:
    for cls in ("altmetric-embed", "__dimensions_badge_embed__", "cv-tag-metric"):
        if [i for i in preprint.items if cls in classes(i)]:
            errors.append(f"pub-Rattanasriampaipong2026: unexpected .{cls} (the paper is not in papers.bib)")
# The Preprint tag belongs to under-review papers only.
if [i for i in first.items if " ".join(i[2].split()) == "Preprint"]:
    errors.append("pub-Rattanasriampaipong2025: a published paper has a 'Preprint' tag")

if errors:
    for e in errors:
        print("FAIL: " + e, file=sys.stderr)
    sys.exit(1)
PY4

echo "PASS: CV page checks (${sections} sections)"
