#!/usr/bin/env bash
set -euo pipefail

# Local smoke test of the CV page script (assets/js/cv.js) in headless Chrome. Not run in CI.
#
# Usage: bash test/cv_page_smoke.sh <built site directory>
#
# Serves the built site on a free local port, loads /cv/ with several addresses in headless Chrome (--dump-dom, which
# prints the DOM after the scripts have run) and checks which section is showing. Prints one PASS/FAIL line per case
# and exits 1 if any case fails. Without Chrome or Chromium it prints SKIP and exits 0.

site="${1:?usage: $0 <built site directory>}"
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "${site}/cv/index.html" ] || {
  echo "FAIL: ${site}/cv/index.html does not exist" >&2
  exit 1
}

chrome=""
for candidate in google-chrome google-chrome-stable chromium chromium-browser; do
  if command -v "${candidate}" >/dev/null 2>&1; then
    chrome="$(command -v "${candidate}")"
    break
  fi
done
if [ -z "${chrome}" ]; then
  echo "SKIP: no Chrome or Chromium found; the CV page smoke test did not run"
  exit 0
fi

work="$(mktemp -d)"
server_pid=""
cleanup() {
  if [ -n "${server_pid}" ]; then
    kill "${server_pid}" 2>/dev/null || true
    wait "${server_pid}" 2>/dev/null || true
  fi
  rm -rf "${work}"
}
trap cleanup EXIT

port="$(python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')"
python3 -m http.server "${port}" --bind 127.0.0.1 --directory "${site}" >/dev/null 2>&1 &
server_pid=$!
for _ in $(seq 50); do
  python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${port}/cv/')" 2>/dev/null && break
  sleep 0.1
done

# The 7th entry of the first group of Presentations: past the "Show all" cut of 5.
cut_entry="$(python3 -c '
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
section = next(s for s in data["sections"] if s["id"] == "presentations")
print(section["groups"][0]["entries"][6]["id"])
' "${repo_root}/_data/cv.json")"

dump() {
  "${chrome}" --headless=new --disable-gpu --no-first-run --no-default-browser-check \
    --user-data-dir="${work}/profile" --virtual-time-budget=5000 --dump-dom "http://127.0.0.1:${port}/cv/$1" 2>/dev/null
}

failures=0
check() {
  local name="$1" hash="$2" visible="$3" card="${4:-}"
  dump "${hash}" >"${work}/dom.html" || true
  if python3 -I - "${work}/dom.html" "${visible}" "${card}" <<'PY'; then
import sys
from html.parser import HTMLParser

dom_path, want_section, want_card = sys.argv[1], sys.argv[2], sys.argv[3]


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Dom(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.sections, self.page, self.bar, self.card = [], None, None, None
        self.card_depth, self.details = 0, []  # open elements inside the wanted card; its <details> attributes

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "section" and "cv-section" in classes:
            self.sections.append((a.get("id"), "hidden" in a))
        elif "cv-page" in classes:
            self.page = classes
        elif "cv-filters" in classes:
            self.bar = a
        if self.card_depth and tag not in VOID:
            self.card_depth += 1
            if tag == "details":
                self.details.append(a)
        if want_card and a.get("id") == want_card:
            self.card, self.card_depth = a, 1

    def handle_endtag(self, tag):
        if self.card_depth and tag not in VOID:
            self.card_depth -= 1


dom = Dom()
with open(dom_path, encoding="utf-8") as f:
    dom.feed(f.read())
problems = []
shown = [i for i, hidden in dom.sections if not hidden]
if not dom.sections:
    problems.append("no sections in the DOM (did the page load?)")
elif shown != [want_section]:
    problems.append(f"visible sections {shown}, expected [{want_section!r}]")
if dom.page is None or "cv-js" not in dom.page:
    problems.append("the wrapper has no cv-js class")
if dom.bar is None or "hidden" in dom.bar:
    problems.append("the filter bar is hidden")
if want_card:
    if dom.card is None:
        problems.append(f"no element with id {want_card!r}")
    elif "hidden" in dom.card:
        problems.append(f"card {want_card!r} is hidden")
    elif dom.details and "open" not in dom.details[0]:
        problems.append(f"card {want_card!r} is shown but its <details> is not open")
if problems:
    print("  " + "; ".join(problems), file=sys.stderr)
    sys.exit(1)
PY
    echo "PASS: ${name}"
  else
    echo "FAIL: ${name}"
    failures=$((failures + 1))
  fi
}

check "/cv/ shows the landing section only" "" publications
check "/cv/#grants-fellowships shows that section only" "#grants-fellowships" grants-fellowships
check "/cv/#grants-noaa shows the entry's section" "#grants-noaa" grants-fellowships grants-noaa
check "/cv/#no-such-id falls back to the landing section" "#no-such-id" publications
check "/cv/#%E0%A4%A (malformed) falls back to the landing section" "#%E0%A4%A" publications
check "/cv/#teaching-experience-heading shows the heading's section" "#teaching-experience-heading" teaching-experience
check "/cv/#${cut_entry} (past the cut) shows Presentations and the entry" "#${cut_entry}" presentations "${cut_entry}"
check "/cv/#${cut_entry}-title (inside a card past the cut) shows and opens that card" "#${cut_entry}-title" presentations "${cut_entry}"
check "/cv/#pub-Rattanasriampaipong2025 (a software entry's Paper link) shows Publications and the card" "#pub-Rattanasriampaipong2025" publications pub-Rattanasriampaipong2025

[ "${failures}" -eq 0 ] || exit 1
