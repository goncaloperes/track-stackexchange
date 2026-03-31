"""Constants, paths, and formatting helpers."""

import html
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")

NETWORK_USER_ID = 9572673
REQUEST_DELAY = 0.5
MAX_RETRIES = 3


def format_number(n):
    """Format a number with commas."""
    return f"{n:,}"


def format_date(timestamp):
    """Convert a Unix timestamp to YYYY-MM-DD."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%d")


def format_tags(tags):
    """Format tags as inline code."""
    return ", ".join(f"`{t}`" for t in tags)


def escape_markdown(text):
    """Unescape HTML entities and escape pipe characters for markdown tables."""
    text = html.unescape(text)
    return text.replace("|", "\\|")
