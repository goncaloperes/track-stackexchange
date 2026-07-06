"""Tests for the formatting helpers in lib.utils."""

from lib.utils import escape_markdown, format_date, format_number, format_tags


def test_format_number_adds_thousands_separators():
    assert format_number(1000) == "1,000"
    assert format_number(25903) == "25,903"
    assert format_number(0) == "0"


def test_format_date_is_utc():
    # 1609459200 == 2021-01-01T00:00:00Z
    assert format_date(1609459200) == "2021-01-01"


def test_format_tags_wraps_each_in_code():
    assert format_tags(["python", "json"]) == "`python`, `json`"
    assert format_tags([]) == ""


def test_escape_markdown_unescapes_entities_and_escapes_pipes():
    assert escape_markdown("a | b") == "a \\| b"
    assert escape_markdown("Tom &amp; Jerry") == "Tom & Jerry"
