"""Tests for pure helpers in lib.api."""

from lib.api import site_name_from_url


def test_stackoverflow_dot_com():
    assert site_name_from_url("https://stackoverflow.com") == "stackoverflow"


def test_other_dot_com_sites():
    assert site_name_from_url("https://superuser.com") == "superuser"
    assert site_name_from_url("https://askubuntu.com") == "askubuntu"
    assert site_name_from_url("https://serverfault.com") == "serverfault"


def test_stackexchange_subdomain():
    assert site_name_from_url("https://cooking.stackexchange.com") == "cooking"
    assert (
        site_name_from_url("https://hermeneutics.stackexchange.com") == "hermeneutics"
    )


def test_trailing_slash_is_stripped():
    assert site_name_from_url("https://cooking.stackexchange.com/") == "cooking"


def test_multi_label_host_maps_to_data_dir_name():
    # e.g. the pt.stackoverflow community lives under data/pt.stackoverflow/
    assert site_name_from_url("https://pt.stackoverflow.com") == "pt.stackoverflow"
