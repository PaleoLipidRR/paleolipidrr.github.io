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

echo "PASS: CV page checks (${sections} sections)"
