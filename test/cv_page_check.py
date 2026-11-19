#!/usr/bin/env python3
"""Check the built CV page against the data it was built from (run in CI by .github/workflows/deploy.yml).

Usage: cv_page_check.py <built site directory> <repo root>

Every expectation is derived from the repo's _data/cv.json, _data/cv_links.yml, _data/cv_figures.yml and the front
matter of _pages/cv.md, so a legitimate edit to any of them does not break the check; nothing about today's CV is
hard-coded. It asserts on <built>/cv/index.html:

- every entry id appears exactly once, as the id of a .cv-card, and there are as many .cv-card elements as entries;
- every section is a section.cv-section, in the data's order, with a panel link whose href is #<section id>;
- no id appears twice on the page; no <summary> is empty; no section carries hidden in the built HTML;
- the stats in the data appear in the stats line; the Download link points at the page's cv_pdf and has download;
- each entry has as many <figure> elements as the figures file lists for it (none when it lists none);
- every publication card has data-status and data-first-author; the links file's labels show in their cards;
- an entry whose `paper` names a publication card links to it (#pub-<paper>);
- assets/js/cv.js is loaded with defer; when the page has Altmetric or Dimensions embeds, their scripts are loaded.

Prints one FAIL line per problem and exits 1, or a final PASS line and exits 0. Needs PyYAML.
"""

import json
import os
import sys
from html.parser import HTMLParser

import yaml

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# The third-party scripts that fill the metric embeds, recognised by a part of their src.
EMBED_SCRIPTS = (
    ("altmetric-embed", "Altmetric", ("altmetric", "d1bxh8uas1mnw7.cloudfront.net/assets/embed.js")),
    ("__dimensions_badge_embed__", "Dimensions", ("badge.dimensions.ai/badge.js",)),
)


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
        return " ".join("".join(c if isinstance(c, str) else c.text() for c in self.children).split())


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


def front_matter(path):
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            data = yaml.safe_load("\n".join(lines[1:end]))
            return data if isinstance(data, dict) else {}
    return {}


def load_yaml(path):
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def check(site, repo):
    errors = []
    page_path = os.path.join(site, "cv", "index.html")
    if not os.path.isfile(page_path):
        return [f"{page_path} does not exist"], 0, 0
    with open(os.path.join(repo, "_data", "cv.json"), encoding="utf-8") as f:
        data = json.load(f)
    links_file = load_yaml(os.path.join(repo, "_data", "cv_links.yml"))
    figures_file = load_yaml(os.path.join(repo, "_data", "cv_figures.yml"))
    settings = front_matter(os.path.join(repo, "_pages", "cv.md"))
    config = load_yaml(os.path.join(repo, "_config.yml"))
    baseurl = (config.get("baseurl") or "").rstrip("/")

    with open(page_path, encoding="utf-8") as f:
        tree = Tree()
        tree.feed(f.read())
    nodes = list(tree.root.walk())

    entries = [e for s in data["sections"] for g in s.get("groups") or [] for e in g.get("entries") or []]
    entry_by_id = {e["id"]: e for e in entries}

    # Cards: one per entry, each entry id exactly once.
    cards = [n for n in nodes if "cv-card" in n.classes]
    card_by_id = {}
    for card in cards:
        card_by_id.setdefault(card.attrs.get("id"), []).append(card)
    for entry in entries:
        found = card_by_id.get(entry["id"], [])
        if len(found) != 1:
            errors.append(f"entry {entry['id']!r} appears as a .cv-card {len(found)} times, expected once")
    if len(cards) != len(entries):
        errors.append(f"the page has {len(cards)} .cv-card elements, the data has {len(entries)} entries")
    for card_id in card_by_id:
        if card_id not in entry_by_id:
            errors.append(f".cv-card {card_id!r} is not an entry of the data")

    def card(entry_id):
        found = card_by_id.get(entry_id, [])
        return found[0] if len(found) == 1 else None

    # Sections, in order, each with its panel link; none hidden without the script.
    sections = [n for n in nodes if n.tag == "section" and "cv-section" in n.classes]
    want_ids = [s["id"] for s in data["sections"]]
    have_ids = [s.attrs.get("id") for s in sections]
    if have_ids != want_ids:
        errors.append(f"sections on the page {have_ids} differ from the data's {want_ids}")
    for section in sections:
        if "hidden" in section.attrs:
            errors.append(f"section {section.attrs.get('id')!r} carries the hidden attribute in the built HTML")
    navs = [n for n in nodes if n.tag == "nav" and "cv-nav" in n.classes]
    nav_hrefs = [a.attrs.get("href") for nav in navs for a in nav.walk() if a.tag == "a" and "cv-nav-link" in a.classes]
    for section_id in want_ids:
        if "#" + section_id not in nav_hrefs:
            errors.append(f"no panel link with href '#{section_id}'")

    # Landing section, when the page sets one.
    wrappers = [n for n in nodes if "cv-page" in n.classes]
    if settings.get("landing_section") and (len(wrappers) != 1 or wrappers[0].attrs.get("data-landing") != settings["landing_section"]):
        errors.append(f".cv-page does not carry data-landing={settings['landing_section']!r}")

    # Unique ids; no empty summary.
    counts = {}
    for n in nodes:
        if n.attrs.get("id"):
            counts[n.attrs["id"]] = counts.get(n.attrs["id"], 0) + 1
    for element_id in sorted(i for i, c in counts.items() if c > 1):
        errors.append(f"duplicate id on the page: {element_id!r} ({counts[element_id]} times)")
    for summary in (n for n in nodes if n.tag == "summary"):
        if not summary.text():
            owner = summary.parent
            while owner is not None and "cv-card" not in owner.classes:
                owner = owner.parent
            errors.append(f"empty <summary> in {owner.attrs.get('id') if owner else 'the page'!r}")

    # Stats line.
    stats = data.get("stats") or {}
    stats_text = " ".join(n.text() for n in nodes if "cv-stats" in n.classes)
    wanted = []
    if stats.get("funding"):
        wanted.append(("funding", stats["funding"]))
    if stats.get("citations"):
        wanted.append(("citations", stats["citations"]))
        if stats.get("hindex"):
            wanted.append(("h-index", f"h-index {stats['hindex']}"))
    if stats.get("students"):
        wanted.append(("students", f"{stats['students']}+"))
    for label, value in wanted:
        if str(value) not in stats_text:
            errors.append(f"the stats line does not show {label} {value!r}")

    # Download link.
    if settings.get("cv_pdf"):
        href = baseurl + settings["cv_pdf"]
        downloads = [n for n in nodes if n.tag == "a" and n.attrs.get("href") == href]
        if not downloads:
            errors.append(f"no link to the PDF {href!r}")
        elif not any("download" in n.attrs for n in downloads):
            errors.append(f"the link to {href!r} has no download attribute")

    # Figures, from the figures file.
    for entry in entries:
        c = card(entry["id"])
        if c is None:
            continue
        listed = figures_file.get(entry["id"]) or []
        drawn = [n for n in c.walk() if n.tag == "figure"]
        if len(drawn) != len(listed):
            errors.append(f"{entry['id']}: {len(drawn)} <figure> elements, the figures file lists {len(listed)}")

    # Publication cards.
    for entry in entries:
        c = card(entry["id"])
        if c is None or not entry.get("pub"):
            continue
        for attribute in ("data-status", "data-first-author"):
            if attribute not in c.attrs:
                errors.append(f"{entry['id']}: the publication card has no {attribute}")

    # Hand-kept links, from the links file.
    for entry_id, items in links_file.items():
        c = card(entry_id)
        if c is None:
            errors.append(f"cv_links.yml key {entry_id!r} has no card on the page")
            continue
        link_texts = [a.text() for a in c.walk() if a.tag == "a"]
        for item in items or []:
            label = str(item.get("label", "")) if isinstance(item, dict) else ""
            if not any(label and label in t for t in link_texts):
                errors.append(f"{entry_id}: no link labelled {label!r}")

    # A software entry's paper.
    for entry in entries:
        c = card(entry["id"])
        paper = entry.get("paper")
        if c is None or not paper:
            continue
        hrefs = [a.attrs.get("href") for a in c.walk() if a.tag == "a"]
        target = f"pub-{paper}"
        if target in entry_by_id and f"#{target}" not in hrefs:
            errors.append(f"{entry['id']}: no link to its paper '#{target}'")
        if target not in entry_by_id and f"#{target}" in hrefs:
            errors.append(f"{entry['id']}: links to '#{target}', which is not on the page")

    # Scripts.
    scripts = [n for n in nodes if n.tag == "script" and n.attrs.get("src")]
    cv_scripts = [s for s in scripts if s.attrs["src"].split("?")[0] == baseurl + "/assets/js/cv.js"]
    if len(cv_scripts) != 1:
        errors.append(f"expected one script tag for /assets/js/cv.js, found {len(cv_scripts)}")
    elif "defer" not in cv_scripts[0].attrs:
        errors.append("the script tag for /assets/js/cv.js has no defer")
    for cls, name, needles in EMBED_SCRIPTS:
        if any(cls in n.classes for n in nodes) and not any(any(x in s.attrs["src"] for x in needles) for s in scripts):
            errors.append(f"the page has {name} embeds ({cls}) but no {name} script tag")

    return errors, len(sections), len(cards)


def main(argv):
    if len(argv) != 3:
        print("usage: cv_page_check.py <built site directory> <repo root>", file=sys.stderr)
        return 2
    try:
        errors, sections, cards = check(argv[1], argv[2])
    except (OSError, ValueError, KeyError, TypeError, AttributeError, yaml.YAMLError) as error:
        print(f"FAIL: cannot check the CV page: {error}".replace("\n", " "), file=sys.stderr)
        return 1
    for error in errors:
        print(f"FAIL: {error}", file=sys.stderr)
    if errors:
        return 1
    print(f"PASS: CV page check ({sections} sections, {cards} cards)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
