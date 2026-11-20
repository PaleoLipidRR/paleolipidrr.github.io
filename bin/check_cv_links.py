#!/usr/bin/env python3
"""Check _data/cv.json, and _data/cv_links.yml (and optionally _data/cv_figures.yml) against it.

Usage: check_cv_links.py <cv.json> <cv_links.yml> [<cv_figures.yml> <site root>]

The data file itself is checked in every invocation, because the page is built from it with no one looking:
`schema_version` must be 1; `sections` a non-empty list; each section needs a non-empty string `id` and
`title` and a `groups` list; each entry a non-empty string `id`, unique across the file; each detail block a
`type` of p, ul or table. Every string the page outputs as HTML (values under a key named `html` or ending in
`_html`, the items of such lists, table row cells and `pub.abstract`) may contain only the tags b, i, em, sub,
sup and code without attributes, and a with exactly one attribute, an href starting with http://, https://,
mailto:, / or #.

Every key of the links file must be an entry id in cv.json, and every value must be a non-empty list of
mappings with exactly the keys `label` and `url`, both non-empty strings. An empty or comment-only file
passes.

With the two extra arguments the figures file is checked too: every key must be an entry id, every value a
non-empty list of mappings with exactly the keys `src`, `alt` and `caption` (non-empty strings; an empty
or null alt is reported as "figure without alt text"). `src` is a path relative to the site root, with no leading
slash and no `..` segment, and must be an existing regular file under that root. An empty or comment-only
figures file passes. The page's settings are checked too: in the front matter of <site root>/_pages/cv.md,
`landing_section` and every id in `collapse_sections` must be a section id of cv.json (a missing file or key is
fine).

Exit status: 0 when the files are fine, 1 when there are problems (one line per problem on stderr),
2 on a wrong argument count (anything but two or four arguments).
"""

import json
import os
import sys
from html.parser import HTMLParser

import yaml

SCHEMA_VERSION = 1
BLOCK_TYPES = ("p", "ul", "table")
PLAIN_TAGS = {"b", "i", "em", "sub", "sup", "code"}
HREF_PREFIXES = ("http://", "https://", "mailto:", "/", "#")


def entry_ids(cv):
    """The set of entry ids in cv.json; raises ValueError naming the first part of an unexpected shape."""
    if not isinstance(cv, dict) or not isinstance(cv.get("sections"), list):
        raise ValueError("cv.json must be an object with a list `sections`")
    ids = set()
    for section in cv["sections"]:
        if not isinstance(section, dict):
            raise ValueError("cv.json: a section is not an object")
        for group in section.get("groups") or []:
            if not isinstance(group, dict):
                raise ValueError("cv.json: a group is not an object")
            for entry in group.get("entries") or []:
                if not isinstance(entry, dict):
                    raise ValueError("cv.json: an entry is not an object")
                if isinstance(entry.get("id"), str) and entry["id"]:
                    ids.add(entry["id"])
    return ids


class _Html(HTMLParser):
    """Collects what an HTML-bearing string holds outside the allowed tags, as short descriptions such as "<script>"."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.bad = []
        self.open = []  # allowed tags opened and not yet closed

    def handle_starttag(self, tag, attrs):
        names = [name for name, _ in attrs]
        if tag in PLAIN_TAGS or tag == "a":
            self.open.append(tag)
        if tag in PLAIN_TAGS:
            if names:
                self.bad.append(f"<{tag} {' '.join(names)}>")
        elif tag == "a":
            if names != ["href"]:
                self.bad.append(f"<a {' '.join(names)}>" if names else "<a>")
            elif not (attrs[0][1] or "").startswith(HREF_PREFIXES):
                self.bad.append(f'<a href="{attrs[0][1] or ""}">')
        else:
            self.bad.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag not in PLAIN_TAGS and tag != "a":
            self.bad.append(f"</{tag}>")
        elif tag in self.open:
            # Close the innermost matching tag (and anything left open inside it, which is reported at the end).
            index = len(self.open) - 1 - self.open[::-1].index(tag)
            self.bad.extend(f"<{t}> is not closed" for t in self.open[index + 1 :])
            del self.open[index:]

    def handle_comment(self, data):
        self.bad.append("<!--")

    def handle_decl(self, decl):
        self.bad.append(f"<!{decl.split()[0] if decl.split() else ''}>")

    def handle_pi(self, data):
        self.bad.append("<?")

    def unknown_decl(self, data):
        self.bad.append("<![")


def html_problems(text, owner):
    """One line per disallowed tag or attribute in an HTML-bearing string; `owner` is an entry or section id."""
    parser = _Html()
    parser.feed(text)
    # html.parser keeps an unfinished construct ("x<img src=x onerror=..." with no ">") in rawdata without reporting it,
    # and close() would drop it; a leftover "<" means markup the browser may still complete.
    if "<" in parser.rawdata:
        parser.bad.append(f"unfinished markup {parser.rawdata[parser.rawdata.index('<'):][:40]!r}")
    parser.close()
    parser.bad.extend(f"<{tag}> is not closed" for tag in parser.open)
    found = []
    for bad in parser.bad:
        line = f"disallowed HTML in {owner}: {bad}"
        if line not in found:
            found.append(line)
    return found


def _html_values(value, owner, key, found):
    """Checks a value under an HTML-bearing key: a string, or a list of strings (None is an absent value)."""
    if value is None:
        return
    if isinstance(value, str):
        found.extend(html_problems(value, owner))
    elif isinstance(value, list) and all(isinstance(item, str) or item is None for item in value):
        for item in value:
            if item is not None:
                found.extend(html_problems(item, owner))
    else:
        found.append(f"{owner}: {key} must be a string or a list of strings")


def _walk_html(node, owner, found):
    """Checks every HTML-bearing value inside an entry or a section's own fields (not its groups)."""
    if isinstance(node, dict):
        for key, value in node.items():
            if not isinstance(key, str):
                continue
            if key == "html" or key.endswith("_html"):
                _html_values(value, owner, key, found)
            elif key == "rows" and isinstance(value, list):
                for row in value:
                    _html_values(row, owner, "rows", found)
            elif key == "groups":
                continue
            else:
                _walk_html(value, owner, found)
    elif isinstance(node, list):
        for item in node:
            _walk_html(item, owner, found)


def _strings(value):
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def block_shape_problems(block, entry_id):
    """The fields a detail block of a known type must have, in the shape the page loops over."""
    kind = block["type"]
    if kind == "p" and not isinstance(block.get("html"), str):
        return [f"entry {entry_id}: a p block's html must be a string"]
    if kind == "ul" and not _strings(block.get("items_html")):
        return [f"entry {entry_id}: a ul block's items_html must be a list of strings"]
    if kind == "table":
        found = []
        if "columns" in block and block["columns"] is not None and not _strings(block["columns"]):
            found.append(f"entry {entry_id}: a table block's columns must be a list of strings")
        rows = block.get("rows")
        if not (isinstance(rows, list) and all(_strings(row) for row in rows)):
            found.append(f"entry {entry_id}: a table block's rows must be a list of lists of strings")
        return found
    return []


def data_problems(cv):
    """Problems of cv.json's own shape and content; assumes the structure entry_ids() accepts."""
    found = []
    sections = cv["sections"]
    if not sections:
        return ["cv.json: sections must be a non-empty list"]
    seen = set()
    for number, section in enumerate(sections, start=1):
        section_id = section.get("id")
        if not isinstance(section_id, str) or not section_id.strip():
            found.append(f"section {number}: id must be a non-empty string")
            section_id = f"section {number}"
        title = section.get("title")
        if not isinstance(title, str) or not title.strip():
            found.append(f"section {section_id}: title must be a non-empty string")
        if not isinstance(section.get("groups"), list):
            found.append(f"section {section_id}: groups must be a list")
        _walk_html(section, section_id, found)
        for group in section.get("groups") or []:
            for entry in group.get("entries") or []:
                entry_id = entry.get("id")
                if not isinstance(entry_id, str) or not entry_id.strip():
                    found.append(f"an entry in section {section_id} has no id (it must be a non-empty string)")
                    entry_id = f"an entry in section {section_id}"
                elif entry_id in seen:
                    found.append(f"duplicate entry id: {entry_id}")
                else:
                    seen.add(entry_id)
                detail = entry.get("detail")
                if detail is not None and not isinstance(detail, list):
                    found.append(f"entry {entry_id}: detail must be a list")
                for block in detail if isinstance(detail, list) else []:
                    block_type = block.get("type") if isinstance(block, dict) else None
                    if block_type not in BLOCK_TYPES:
                        found.append(f"unknown detail block type '{block_type}' in entry {entry_id}")
                    else:
                        found.extend(block_shape_problems(block, entry_id))
                _walk_html(entry, entry_id, found)
                pub = entry.get("pub")
                if isinstance(pub, dict):
                    _html_values(pub.get("abstract"), entry_id, "pub.abstract", found)
    return found


def front_matter(path):
    """The YAML front matter of a page as a dict; {} when the file or the front matter is missing."""
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    for end in range(1, len(lines)):
        if lines[end].strip() == "---":
            data = yaml.safe_load("\n".join(lines[1:end]))
            return data if isinstance(data, dict) else {}
    return {}


def settings_problems(cv, root):
    """landing_section and collapse_sections of <root>/_pages/cv.md must name sections of cv.json."""
    settings = front_matter(os.path.join(root, "_pages", "cv.md"))
    section_ids = {s.get("id") for s in cv["sections"]}
    wanted = []
    if settings.get("landing_section") is not None:
        wanted.append(settings["landing_section"])
    collapse = settings.get("collapse_sections")
    if collapse is not None:
        wanted.extend(collapse if isinstance(collapse, list) else [collapse])
    found = []
    for name in wanted:
        if not isinstance(name, str):
            found.append(f"_pages/cv.md: a section id must be a string, found {name!r}")
        elif name not in section_ids:
            found.append(f"unknown section id in _pages/cv.md: {name}")
    return found


def problems(cv, links):
    if links is None:
        entry_ids(cv)  # still reject a cv.json of the wrong shape
        return []
    if not isinstance(links, dict):
        return ["the links file must be a mapping from entry id to a list of links"]
    ids = entry_ids(cv)
    found = []
    for key, value in links.items():
        if not isinstance(key, str):
            found.append(f"key is not a string: {key!r}")
            continue
        if key not in ids:
            found.append(f"orphan key: {key}")
        if not isinstance(value, list) or not value:
            found.append(f"{key}: value must be a non-empty list of {{label, url}} mappings")
            continue
        for index, item in enumerate(value, start=1):
            where = f"{key}: item {index}"
            if not isinstance(item, dict):
                found.append(f"{where} is not a mapping with label and url")
            elif set(item) != {"label", "url"}:
                found.append(f"{where} must have exactly the keys label and url, found {sorted(map(str, item))}")
            elif not all(isinstance(item[k], str) and item[k].strip() for k in ("label", "url")):
                found.append(f"{where}: label and url must be non-empty strings")
    return found


def figure_problems(cv, figures, root):
    """Problems of the figures file; `root` is the site root directory."""
    if figures is None:
        entry_ids(cv)
        return []
    if not isinstance(figures, dict):
        return ["the figures file must be a mapping from entry id to a list of figures"]
    ids = entry_ids(cv)
    real_root = os.path.realpath(root)
    found = []
    for key, value in figures.items():
        if not isinstance(key, str):
            found.append(f"figure key is not a string: {key!r}")
            continue
        if key not in ids:
            found.append(f"orphan figure key: {key}")
        if not isinstance(value, list) or not value:
            found.append(f"{key}: value must be a non-empty list of {{src, alt, caption}} mappings")
            continue
        for index, item in enumerate(value, start=1):
            where = f"{key}: figure {index}"
            if not isinstance(item, dict):
                found.append(f"{where} is not a mapping with src, alt and caption")
                continue
            if set(item) != {"src", "alt", "caption"}:
                found.append(f"{where} must have exactly the keys src, alt and caption, found {sorted(map(str, item))}")
                continue
            # `alt:` with no value loads as None; it is reported like an empty alt.
            if item["alt"] is None or (isinstance(item["alt"], str) and not item["alt"].strip()):
                found.append(f"figure without alt text: {key}")
                if not all(isinstance(item[k], str) for k in ("src", "caption")):
                    found.append(f"{where}: src and caption must be strings")
                continue
            if not all(isinstance(item[k], str) for k in ("src", "alt", "caption")):
                found.append(f"{where}: src, alt and caption must be strings")
                continue
            if not item["caption"].strip():
                found.append(f"{where}: caption must not be empty")
            src = item["src"]
            if not src.strip():
                found.append(f"{where}: src must not be empty")
                continue
            parts = src.replace("\\", "/").split("/")
            if src.startswith("/") or os.path.isabs(src) or ".." in parts or "\0" in src:
                found.append(f"figure path outside the site: {src}")
                continue
            target = os.path.join(real_root, src)
            real_target = os.path.realpath(target)
            if real_target != real_root and not real_target.startswith(real_root + os.sep):
                found.append(f"figure path outside the site: {src}")
            elif not os.path.isfile(real_target):
                found.append(f"missing figure file: {src}")
    return found


def main(argv):
    if len(argv) not in (3, 5):
        print("usage: check_cv_links.py <cv.json> <cv_links.yml> [<cv_figures.yml> <site root>]", file=sys.stderr)
        return 2
    with_figures = len(argv) == 5
    try:
        with open(argv[1], encoding="utf-8") as f:
            cv = json.load(f)
        with open(argv[2], encoding="utf-8") as f:
            links = yaml.safe_load(f)
        figures = None
        if with_figures:
            with open(argv[3], encoding="utf-8") as f:
                figures = yaml.safe_load(f)
            if not os.path.isdir(argv[4]):
                raise OSError(f"site root is not a directory: {argv[4]}")
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as error:
        print(f"cannot read input: {error}".replace("\n", " "), file=sys.stderr)
        return 1
    # A data file of another schema version has an unknown shape: report that alone.
    version = cv.get("schema_version") if isinstance(cv, dict) else None
    if version != SCHEMA_VERSION or isinstance(version, bool):
        print(f"unsupported cv.json schema_version: {version}", file=sys.stderr)
        return 1
    try:
        entry_ids(cv)  # the structure every later check walks; a wrong one is reported on one line
        found = data_problems(cv)
        found += problems(cv, links)
        if with_figures:
            found += figure_problems(cv, figures, argv[4])
            found += settings_problems(cv, argv[4])
    except (ValueError, TypeError, AttributeError) as error:
        print(f"unexpected cv.json shape: {error}".replace("\n", " "), file=sys.stderr)
        return 1
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as error:
        print(f"cannot read _pages/cv.md: {error}".replace("\n", " "), file=sys.stderr)
        return 1
    for line in found:
        print(line, file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
