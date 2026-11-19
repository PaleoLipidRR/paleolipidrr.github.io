"""Tests for bin/check_cv_links.py (run: pytest test/test_check_cv_links.py)."""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "check_cv_links.py"

CV = {
    "sections": [
        {
            "id": "teaching",
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
    for cv in ({}, {"sections": "x"}, {"sections": [1]}, {"sections": [{"groups": [1]}]}, {"sections": [{"groups": [{"entries": [1]}]}]}):
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
