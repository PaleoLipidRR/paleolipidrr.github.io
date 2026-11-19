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
