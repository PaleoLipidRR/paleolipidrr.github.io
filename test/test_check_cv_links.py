"""Tests for bin/check_cv_links.py (run: pytest test/test_check_cv_links.py)."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "check_cv_links.py"

CV = {
    "schema_version": 1,
    "sections": [
        {
            "id": "teaching",
            "title": "Teaching",
            "groups": [
                {
                    "id": None,
                    "entries": [{"id": "teaching-a"}, {"id": "teaching-b"}],
                },
                {"id": "more", "entries": [{"id": "pub-X"}]},
            ],
        }
    ]
}


def run(tmp_path, links_text, *, cv=CV):
    cv_file = tmp_path / "cv.json"
    cv_file.write_text(json.dumps(cv), encoding="utf-8")
    links_file = tmp_path / "cv_links.yml"
    links_file.write_text(links_text, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(cv_file), str(links_file)],
        capture_output=True,
        text=True,
    )


def test_matching_keys_pass(tmp_path):
    result = run(tmp_path, "teaching-a:\n  - { label: Course page, url: /courses/a/ }\npub-X:\n  - { label: A, url: 'https://x.org' }\n")
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_empty_file_passes(tmp_path):
    assert run(tmp_path, "").returncode == 0


def test_comment_only_file_passes(tmp_path):
    assert run(tmp_path, "# nothing yet\n").returncode == 0


def test_orphan_key_fails(tmp_path):
    result = run(tmp_path, "nope:\n  - { label: A, url: /a/ }\n")
    assert result.returncode == 1
    assert "orphan key: nope" in result.stderr.splitlines()


def test_one_line_per_orphan(tmp_path):
    result = run(tmp_path, "nope:\n  - { label: A, url: /a/ }\nteaching-a:\n  - { label: A, url: /a/ }\nalso-no:\n  - { label: A, url: /a/ }\n")
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["orphan key: nope", "orphan key: also-no"]


def test_value_not_a_list_fails(tmp_path):
    result = run(tmp_path, "teaching-a: /courses/a/\n")
    assert result.returncode == 1
    assert "teaching-a" in result.stderr


def test_empty_list_fails(tmp_path):
    result = run(tmp_path, "teaching-a: []\n")
    assert result.returncode == 1


def test_null_value_fails(tmp_path):
    assert run(tmp_path, "teaching-a:\n").returncode == 1


def test_item_not_a_mapping_fails(tmp_path):
    assert run(tmp_path, "teaching-a:\n  - /courses/a/\n").returncode == 1


def test_missing_key_fails(tmp_path):
    assert run(tmp_path, "teaching-a:\n  - { label: A }\n").returncode == 1


def test_extra_key_fails(tmp_path):
    assert run(tmp_path, "teaching-a:\n  - { label: A, url: /a/, icon: x }\n").returncode == 1


def test_non_string_or_empty_values_fail(tmp_path):
    assert run(tmp_path, "teaching-a:\n  - { label: 3, url: /a/ }\n").returncode == 1
    assert run(tmp_path, "teaching-a:\n  - { label: A, url: '' }\n").returncode == 1
    assert run(tmp_path, "teaching-a:\n  - { label: '  ', url: /a/ }\n").returncode == 1


def test_top_level_not_a_mapping_fails(tmp_path):
    assert run(tmp_path, "- teaching-a\n").returncode == 1
    assert run(tmp_path, "just a string\n").returncode == 1


def test_invalid_yaml_fails(tmp_path):
    assert run(tmp_path, "a: [unclosed\n").returncode == 1


def test_non_string_key_fails(tmp_path):
    assert run(tmp_path, "123:\n  - { label: A, url: /a/ }\n").returncode == 1


def test_wrong_argument_count(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "only-one"], capture_output=True, text=True)
    assert result.returncode == 2
    assert "usage" in result.stderr.lower()


def run_files(cv_path, links_path):
    return subprocess.run([sys.executable, str(SCRIPT), str(cv_path), str(links_path)], capture_output=True, text=True)


def test_top_level_list_cv_json_fails_cleanly(tmp_path):
    result = run(tmp_path, "teaching-a:\n  - { label: A, url: /a/ }\n", cv=[1, 2])
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert len(result.stderr.splitlines()) == 1


def test_odd_shapes_in_cv_json_fail_cleanly(tmp_path):
    for cv in (
        {"schema_version": 1},
        {"schema_version": 1, "sections": "x"},
        {"schema_version": 1, "sections": [1]},
        {"schema_version": 1, "sections": [{"id": "s", "title": "S", "groups": [1]}]},
        {"schema_version": 1, "sections": [{"id": "s", "title": "S", "groups": [{"entries": [1]}]}]},
    ):
        result = run(tmp_path, "", cv=cv)
        assert result.returncode == 1, cv
        assert "Traceback" not in result.stderr
        assert len(result.stderr.splitlines()) == 1


def test_missing_cv_json_fails_cleanly(tmp_path):
    links = tmp_path / "cv_links.yml"
    links.write_text("", encoding="utf-8")
    result = run_files(tmp_path / "nope.json", links)
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert result.stderr.strip()


def test_missing_links_file_fails_cleanly(tmp_path):
    cv_file = tmp_path / "cv.json"
    cv_file.write_text(json.dumps(CV), encoding="utf-8")
    result = run_files(cv_file, tmp_path / "nope.yml")
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert result.stderr.strip()


# Figures file (four arguments: cv.json, cv_links.yml, cv_figures.yml, site root).
def run_figures(tmp_path, figures_text, *, files=("img/a.png",), extra_args=None):
    cv_file = tmp_path / "cv.json"
    cv_file.write_text(json.dumps(CV), encoding="utf-8")
    links_file = tmp_path / "cv_links.yml"
    links_file.write_text("", encoding="utf-8")
    figures_file = tmp_path / "cv_figures.yml"
    figures_file.write_text(figures_text, encoding="utf-8")
    root = tmp_path / "site"
    for name in files:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"png")
    args = [str(cv_file), str(links_file), str(figures_file), str(root)] if extra_args is None else extra_args
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


GOOD = "pub-X:\n  - { src: img/a.png, alt: A plot, caption: A caption }\n"


def clean_failure(result):
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert result.stderr.strip()


def test_valid_figures_pass(tmp_path):
    result = run_figures(tmp_path, GOOD)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_empty_and_comment_only_figures_pass(tmp_path):
    assert run_figures(tmp_path, "").returncode == 0
    assert run_figures(tmp_path, "# nothing yet\n").returncode == 0


def test_figures_orphan_key_fails(tmp_path):
    result = run_figures(tmp_path, "nope:\n  - { src: img/a.png, alt: A, caption: B }\n")
    assert result.returncode == 1
    assert "orphan figure key: nope" in result.stderr.splitlines()


def test_missing_figure_file_fails(tmp_path):
    result = run_figures(tmp_path, "pub-X:\n  - { src: img/gone.png, alt: A, caption: B }\n")
    assert result.returncode == 1
    assert "missing figure file: img/gone.png" in result.stderr.splitlines()


def test_directory_is_not_a_figure_file(tmp_path):
    result = run_figures(tmp_path, "pub-X:\n  - { src: img, alt: A, caption: B }\n")
    assert result.returncode == 1
    assert "missing figure file: img" in result.stderr.splitlines()


def test_empty_or_missing_alt_fails(tmp_path):
    for item in ("{ src: img/a.png, alt: '', caption: B }", "{ src: img/a.png, alt: '  ', caption: B }"):
        result = run_figures(tmp_path, f"pub-X:\n  - {item}\n")
        assert result.returncode == 1
        assert "figure without alt text: pub-X" in result.stderr.splitlines()
    result = run_figures(tmp_path, "pub-X:\n  - { src: img/a.png, caption: B }\n")
    assert result.returncode == 1


def test_paths_outside_the_site_fail(tmp_path):
    (tmp_path / "secret.png").write_bytes(b"x")
    for src in ("../secret.png", "img/../../secret.png", "/etc/passwd", "img/./../../secret.png"):
        result = run_figures(tmp_path, f"pub-X:\n  - {{ src: '{src}', alt: A, caption: B }}\n")
        assert result.returncode == 1, src
        assert f"figure path outside the site: {src}" in result.stderr.splitlines()


def test_null_alt_is_reported_as_missing_alt_text(tmp_path):
    for item in ("{ src: img/a.png, alt: null, caption: B }", "{ src: img/a.png, alt: ~, caption: B }"):
        result = run_figures(tmp_path, f"pub-X:\n  - {item}\n")
        assert result.returncode == 1
        assert "figure without alt text: pub-X" in result.stderr.splitlines()
        assert "Traceback" not in result.stderr
    result = run_figures(tmp_path, "pub-X:\n  - src: img/a.png\n    alt:\n    caption: B\n")
    assert result.returncode == 1
    assert "figure without alt text: pub-X" in result.stderr.splitlines()


def test_symlink_resolving_outside_the_site_fails(tmp_path):
    (tmp_path / "secret.png").write_bytes(b"x")
    (tmp_path / "site" / "img").mkdir(parents=True)
    (tmp_path / "site" / "img" / "link.png").symlink_to(tmp_path / "secret.png")
    result = run_figures(tmp_path, "pub-X:\n  - { src: img/link.png, alt: A, caption: B }\n")
    assert result.returncode == 1
    assert "figure path outside the site: img/link.png" in result.stderr.splitlines()


def test_bad_figure_shapes_fail_cleanly(tmp_path):
    for text in (
        "pub-X: img/a.png\n",
        "pub-X: []\n",
        "pub-X:\n",
        "pub-X:\n  - img/a.png\n",
        "pub-X:\n  - { src: img/a.png, alt: A }\n",
        "pub-X:\n  - { src: img/a.png, alt: A, caption: B, extra: C }\n",
        "pub-X:\n  - { src: img/a.png, alt: 3, caption: B }\n",
        "pub-X:\n  - { src: img/a.png, alt: A, caption: '' }\n",
        "pub-X:\n  - { src: '', alt: A, caption: B }\n",
        "- pub-X\n",
        "just a string\n",
        "123:\n  - { src: img/a.png, alt: A, caption: B }\n",
        "a: [unclosed\n",
    ):
        clean_failure(run_figures(tmp_path, text))


def test_missing_figures_file_or_root_fails_cleanly(tmp_path):
    clean_failure(run_figures(tmp_path, GOOD, extra_args=[str(tmp_path / "cv.json"), str(tmp_path / "cv_links.yml"), str(tmp_path / "nope.yml"), str(tmp_path)]))
    clean_failure(run_figures(tmp_path, GOOD, extra_args=[str(tmp_path / "cv.json"), str(tmp_path / "cv_links.yml"), str(tmp_path / "cv_figures.yml"), str(tmp_path / "no-root")]))


def test_three_arguments_exit_2(tmp_path):
    result = run_figures(tmp_path, GOOD, extra_args=[str(tmp_path / "cv.json"), str(tmp_path / "cv_links.yml"), str(tmp_path / "cv_figures.yml")])
    assert result.returncode == 2
    assert "usage" in result.stderr.lower()


# The data file's own shape (checked in every invocation, two or four arguments).
def cv_with(**changes):
    """A copy of CV with one entry replaced or extended; `entry` updates teaching-a, `section` updates the section."""
    cv = json.loads(json.dumps(CV))
    cv["sections"][0]["groups"][0]["entries"][0].update(changes.get("entry", {}))
    cv["sections"][0].update(changes.get("section", {}))
    return cv


def data_failure(tmp_path, cv, line):
    result = run(tmp_path, "", cv=cv)
    assert result.returncode == 1, result.stderr
    assert "Traceback" not in result.stderr
    assert line in result.stderr.splitlines(), result.stderr


REAL_SHAPED = {
    "schema_version": 1,
    "updated": "2026-11-01",
    "stats": {"funding": "$1", "citations": "2", "hindex": "1", "students": "3"},
    "sections": [
        {
            "id": "publications",
            "title": "Publications",
            "intro_html": ["Names in <b>bold</b> are mine; <sup>*</sup> marks a student."],
            "footnotes_html": ["<i>Note</i>"],
            "groups": [
                {
                    "id": None,
                    "title": None,
                    "entries": [
                        {
                            "id": "pub-A2025",
                            "title_html": "<b>A</b>",
                            "roles": [{"title_html": "Lead <i>(PI)</i>", "when": "2025"}],
                            "notes_html": ["CO<sub>2</sub> and <code>x</code> and <em>y</em>"],
                            "detail": [
                                {"type": "p", "html": "See <a href=\"https://example.org\">this</a>."},
                                {"type": "ul", "items_html": ["<a href=\"/cv/\">here</a>", "<a href=\"#pub-A2025\">there</a>", "<a href=\"mailto:a@b.c\">mail</a>"]},
                                {"type": "table", "columns": ["Term", "Students (rating)"], "rows": [["Fall <b>2025</b>", "30 (4.5)"]]},
                            ],
                            "links": [],
                            "paper": None,
                            "pub": {
                                "key": "A2025",
                                "authors_short_html": "<b>Me</b>, You",
                                "title_html": "On U<sup>K'</sup><sub>37</sub>",
                                "venue_html": "<i>Journal</i>",
                                "abstract": "We use TEX<sub>86</sub> & more.",
                                "status": "published",
                                "first_author": True,
                            },
                        }
                    ],
                }
            ],
        }
    ],
}


def test_real_shaped_file_passes(tmp_path):
    result = run(tmp_path, "", cv=REAL_SHAPED)
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""


def test_real_data_file_passes():
    root = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(root / "_data/cv.json"), str(root / "_data/cv_links.yml"), str(root / "_data/cv_figures.yml"), str(root)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_schema_version_must_be_1(tmp_path):
    for version, shown in ((2, "2"), ("1", "1"), (None, "None")):
        cv = dict(CV, schema_version=version)
        result = run(tmp_path, "", cv=cv)
        assert result.returncode == 1
        assert result.stderr.splitlines() == [f"unsupported cv.json schema_version: {shown}"]
    cv = {k: v for k, v in CV.items() if k != "schema_version"}
    data_failure(tmp_path, cv, "unsupported cv.json schema_version: None")


def test_empty_sections_fail(tmp_path):
    data_failure(tmp_path, {"schema_version": 1, "sections": []}, "cv.json: sections must be a non-empty list")


def test_empty_sections_fail_in_four_argument_form(tmp_path):
    cv_file = tmp_path / "cv.json"
    cv_file.write_text(json.dumps({"schema_version": 1, "sections": []}), encoding="utf-8")
    (tmp_path / "l.yml").write_text("", encoding="utf-8")
    (tmp_path / "f.yml").write_text("", encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), str(cv_file), str(tmp_path / "l.yml"), str(tmp_path / "f.yml"), str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "cv.json: sections must be a non-empty list" in result.stderr.splitlines()


def test_section_needs_id_title_and_groups(tmp_path):
    data_failure(tmp_path, cv_with(section={"id": ""}), "section 1: id must be a non-empty string")
    data_failure(tmp_path, cv_with(section={"title": None}), "section teaching: title must be a non-empty string")
    data_failure(tmp_path, cv_with(section={"title": "  "}), "section teaching: title must be a non-empty string")
    data_failure(tmp_path, cv_with(section={"groups": None}), "section teaching: groups must be a list")


def test_entry_needs_an_id(tmp_path):
    data_failure(tmp_path, cv_with(entry={"id": ""}), "an entry in section teaching has no id (it must be a non-empty string)")
    data_failure(tmp_path, cv_with(entry={"id": 7}), "an entry in section teaching has no id (it must be a non-empty string)")


def test_duplicate_entry_id_fails(tmp_path):
    data_failure(tmp_path, cv_with(entry={"id": "pub-X"}), "duplicate entry id: pub-X")


def test_unknown_detail_block_type_fails(tmp_path):
    data_failure(tmp_path, cv_with(entry={"detail": [{"type": "p", "html": "ok"}, {"type": "dl", "items_html": []}]}), "unknown detail block type 'dl' in entry teaching-a")
    data_failure(tmp_path, cv_with(entry={"detail": [{"html": "no type"}]}), "unknown detail block type 'None' in entry teaching-a")


def test_disallowed_html_fails(tmp_path):
    cases = (
        ({"entry": {"title_html": "<script>alert(1)</script>"}}, "disallowed HTML in teaching-a: <script>"),
        ({"entry": {"notes_html": ["ok", "<img src=x onerror=alert(1)>"]}}, "disallowed HTML in teaching-a: <img>"),
        ({"entry": {"title_html": "<b onclick=\"x()\">A</b>"}}, "disallowed HTML in teaching-a: <b onclick>"),
        ({"entry": {"title_html": "<a href=\"javascript:alert(1)\">A</a>"}}, "disallowed HTML in teaching-a: <a href=\"javascript:alert(1)\">"),
        ({"entry": {"title_html": "<a href=\"https://x.org\" target=\"_blank\">A</a>"}}, "disallowed HTML in teaching-a: <a href target>"),
        ({"entry": {"title_html": "<a>A</a>"}}, "disallowed HTML in teaching-a: <a>"),
        ({"entry": {"detail": [{"type": "p", "html": "<iframe src=\"https://x.org\"></iframe>"}]}}, "disallowed HTML in teaching-a: <iframe>"),
        ({"entry": {"detail": [{"type": "ul", "items_html": ["<style>x</style>"]}]}}, "disallowed HTML in teaching-a: <style>"),
        ({"entry": {"detail": [{"type": "table", "columns": ["A"], "rows": [["<div>x</div>"]]}]}}, "disallowed HTML in teaching-a: <div>"),
        ({"entry": {"roles": [{"title_html": "<span>x</span>", "when": "2020"}]}}, "disallowed HTML in teaching-a: <span>"),
        ({"entry": {"pub": {"abstract": "<p>x</p>", "status": "published"}}}, "disallowed HTML in teaching-a: <p>"),
        ({"entry": {"pub": {"venue_html": "<!-- x -->", "status": "published"}}}, "disallowed HTML in teaching-a: <!--"),
        ({"section": {"intro_html": ["<object data=x></object>"]}}, "disallowed HTML in teaching: <object>"),
        ({"section": {"footnotes_html": ["<svg onload=x()>"]}}, "disallowed HTML in teaching: <svg>"),
    )
    for changes, line in cases:
        data_failure(tmp_path, cv_with(**changes), line)


def test_allowed_html_and_plain_fields_pass(tmp_path):
    cv = cv_with(
        entry={
            "title_html": "<b>A</b> <i>b</i> <em>c</em> H<sub>2</sub>O x<sup>2</sup> <code>f()</code> &amp; &lt;script&gt;",
            "notes_html": ["<a href=\"http://x.org\">1</a> <a href=\"mailto:a@b.c\">2</a> <a href=\"/p/\">3</a> <a href=\"#s\">4</a>"],
            # Plain fields are escaped by the page, so markup in them is not a problem for the check.
            "place": "<script>",
            "when": "<b>2020</b>",
        }
    )
    result = run(tmp_path, "", cv=cv)
    assert result.returncode == 0, result.stderr


# The page's own settings (_pages/cv.md under the site root, four-argument form only).
def run_settings(tmp_path, front_matter, cv=CV):
    cv_file = tmp_path / "cv.json"
    cv_file.write_text(json.dumps(cv), encoding="utf-8")
    (tmp_path / "cv_links.yml").write_text("", encoding="utf-8")
    (tmp_path / "cv_figures.yml").write_text("", encoding="utf-8")
    root = tmp_path / "site"
    root.mkdir(exist_ok=True)
    if front_matter is not None:
        (root / "_pages").mkdir(exist_ok=True)
        (root / "_pages" / "cv.md").write_text(front_matter, encoding="utf-8")
    args = [str(cv_file), str(tmp_path / "cv_links.yml"), str(tmp_path / "cv_figures.yml"), str(root)]
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


def test_page_settings_naming_real_sections_pass(tmp_path):
    result = run_settings(tmp_path, "---\nlayout: cv_page\nlanding_section: teaching\ncollapse_sections: [teaching]\ncollapse_after: 5\n---\n")
    assert result.returncode == 0, result.stderr


def test_missing_page_file_or_keys_pass(tmp_path):
    assert run_settings(tmp_path, None).returncode == 0
    assert run_settings(tmp_path, "---\nlayout: cv_page\n---\n").returncode == 0
    assert run_settings(tmp_path, "no front matter at all\n").returncode == 0


def test_unknown_landing_section_fails(tmp_path):
    result = run_settings(tmp_path, "---\nlanding_section: publications\n---\n")
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["unknown section id in _pages/cv.md: publications"]


def test_unknown_collapse_section_fails(tmp_path):
    result = run_settings(tmp_path, "---\nlanding_section: teaching\ncollapse_sections: [teaching, talks, workshops]\n---\n")
    assert result.returncode == 1
    assert result.stderr.splitlines() == ["unknown section id in _pages/cv.md: talks", "unknown section id in _pages/cv.md: workshops"]


def test_unreadable_page_front_matter_fails_cleanly(tmp_path):
    clean_failure(run_settings(tmp_path, "---\nlanding_section: [unclosed\n---\n"))
