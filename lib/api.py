"""Stack Exchange API client with retry, backoff, and pagination."""

import gzip
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from lib.utils import MAX_RETRIES, REQUEST_DELAY

BASE_URL = "https://api.stackexchange.com/2.3"

# A registered Stack Apps key raises the request quota from 300/day (shared per
# IP, which is easily exhausted on shared CI runners) to 10,000/day.
# Register at https://stackapps.com/apps/oauth/register and expose the key via
# the STACKEXCHANGE_KEY environment variable.
API_KEY = os.environ.get("STACKEXCHANGE_KEY", "").strip()


def _read_body(resp_or_err):
    """Read and gunzip a response/error body, returning parsed JSON or None."""
    try:
        raw = resp_or_err.read()
        if resp_or_err.headers.get("Content-Encoding") == "gzip":
            raw = gzip.decompress(raw)
        return json.loads(raw)
    except Exception:
        return None


def api_get(endpoint, params=None):
    """Make a GET request to the Stack Exchange API with backoff and retry."""
    if params is None:
        params = {}
    if API_KEY:
        params = {**params, "key": API_KEY}
    query = urllib.parse.urlencode(params)
    url = f"{BASE_URL}{endpoint}"
    if query:
        url += f"?{query}"
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(url)
            req.add_header("Accept-Encoding", "gzip")
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = _read_body(resp)
            if data is None:
                raise ValueError("Could not parse API response")
            if "backoff" in data:
                print(f"  Backoff requested: {data['backoff']}s")
                time.sleep(data["backoff"])
            time.sleep(REQUEST_DELAY)
            return data
        except urllib.error.HTTPError as e:
            # The SE API returns a JSON error body even on 4xx. A 400 with
            # error_id 502 is a throttle_violation (quota exhausted); anything
            # else is a genuinely bad request that won't self-heal on retry.
            err = _read_body(e) or {}
            error_id = err.get("error_id")
            error_msg = err.get("error_message", str(e))
            throttled = e.code == 400 and error_id == 502
            if throttled and attempt < MAX_RETRIES - 1:
                wait = err.get("backoff") or 2 ** (attempt + 1)
                print(f"  Throttled (quota exhausted): {error_msg}; "
                      f"waiting {wait}s...")
                time.sleep(wait)
                continue
            hint = ""
            if throttled and not API_KEY:
                hint = (" — set the STACKEXCHANGE_KEY env var with a Stack Apps "
                        "key to raise the quota to 10,000/day")
            raise RuntimeError(
                f"Stack Exchange API error {e.code} "
                f"(error_id={error_id}): {error_msg}{hint}"
            ) from e
        except (urllib.error.URLError, ConnectionError, OSError) as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                print(f"  Request failed ({e}), retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise


def fetch_all_pages(endpoint, params):
    """Fetch all pages of a paginated API endpoint."""
    all_items = []
    page = 1
    while True:
        p = {**params, "page": page, "pagesize": 100}
        data = api_get(endpoint, p)
        all_items.extend(data.get("items", []))
        if not data.get("has_more", False):
            break
        page += 1
    return all_items


def fetch_associated_accounts(network_user_id):
    """Fetch all associated accounts for the network user."""
    print("Fetching associated accounts...")
    accounts = fetch_all_pages(
        f"/users/{network_user_id}/associated",
        {"pagesize": 100},
    )
    print(f"  Found {len(accounts)} associated accounts")
    return accounts


def site_name_from_url(site_url):
    """Extract the API site name from a site URL.

    Examples:
        https://stackoverflow.com -> stackoverflow
        https://cooking.stackexchange.com -> cooking
        https://hermeneutics.stackexchange.com -> hermeneutics
    """
    host = site_url.rstrip("/").replace("https://", "").replace("http://", "")
    if host.endswith(".stackexchange.com"):
        return host.replace(".stackexchange.com", "")
    # For sites like stackoverflow.com, superuser.com, askubuntu.com, etc.
    return host.replace(".com", "")


def fetch_answers(site, user_id):
    """Fetch all answers for a user on a given site."""
    print(f"  Fetching answers on {site}...")
    answers = fetch_all_pages(
        f"/users/{user_id}/answers",
        {"site": site, "sort": "votes", "order": "desc"},
    )
    print(f"    Found {len(answers)} answers")
    return answers


def fetch_questions(site, user_id):
    """Fetch all questions for a user on a given site."""
    print(f"  Fetching questions on {site}...")
    questions = fetch_all_pages(
        f"/users/{user_id}/questions",
        {"site": site, "sort": "votes", "order": "desc"},
    )
    print(f"    Found {len(questions)} questions")
    return questions


def fetch_question_details(site, question_ids):
    """Fetch question titles and tags for a list of question IDs in batches of 100."""
    details = {}
    for i in range(0, len(question_ids), 100):
        batch = question_ids[i : i + 100]
        ids_str = ";".join(str(qid) for qid in batch)
        print(f"    Fetching question details batch {i // 100 + 1}...")
        data = api_get(
            f"/questions/{ids_str}",
            {"site": site, "pagesize": 100},
        )
        for item in data.get("items", []):
            details[item["question_id"]] = {
                "title": item.get("title", "Untitled"),
                "tags": item.get("tags", []),
            }
    return details
