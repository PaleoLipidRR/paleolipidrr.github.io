#!/usr/bin/env python3
"""Check _data/cv_links.yml against _data/cv.json.

Usage: check_cv_links.py <cv.json> <cv_links.yml>

Every key of the links file must be an entry id in cv.json, and every value must be a non-empty list of
mappings with exactly the keys `label` and `url`, both non-empty strings. An empty or comment-only file
passes. Exit status: 0 when the file is fine, 1 when there are problems (one line per problem on stderr),
2 on a wrong argument count.
"""

import json
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


def main(argv):
    if len(argv) != 3:
        print("usage: check_cv_links.py <cv.json> <cv_links.yml>", file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as f:
            cv = json.load(f)
        with open(argv[2], encoding="utf-8") as f:
            links = yaml.safe_load(f)
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as error:
        print(f"cannot read input: {error}".replace("\n", " "), file=sys.stderr)
        return 1
    try:
        found = problems(cv, links)
    except (ValueError, TypeError, AttributeError) as error:
        print(f"unexpected cv.json shape: {error}".replace("\n", " "), file=sys.stderr)
        return 1
    for line in found:
        print(line, file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
