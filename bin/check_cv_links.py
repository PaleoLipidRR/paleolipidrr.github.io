#!/usr/bin/env python3
"""Check _data/cv_links.yml (and optionally _data/cv_figures.yml) against _data/cv.json.

Usage: check_cv_links.py <cv.json> <cv_links.yml> [<cv_figures.yml> <site root>]

Every key of the links file must be an entry id in cv.json, and every value must be a non-empty list of
mappings with exactly the keys `label` and `url`, both non-empty strings. An empty or comment-only file
passes.

With the two extra arguments the figures file is checked too: every key must be an entry id, every value a
non-empty list of mappings with exactly the keys `src`, `alt` and `caption` (non-empty strings; an empty
or null alt is reported as "figure without alt text"). `src` is a path relative to the site root, with no leading
slash and no `..` segment, and must be an existing regular file under that root. An empty or comment-only
figures file passes.

Exit status: 0 when the files are fine, 1 when there are problems (one line per problem on stderr),
2 on a wrong argument count (anything but two or four arguments).
"""

import json
import os
import sys

import yaml


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
    try:
        found = problems(cv, links)
        if with_figures:
            found += figure_problems(cv, figures, argv[4])
    except (ValueError, TypeError, AttributeError) as error:
        print(f"unexpected cv.json shape: {error}".replace("\n", " "), file=sys.stderr)
        return 1
    for line in found:
        print(line, file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
