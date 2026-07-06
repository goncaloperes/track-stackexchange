"""Markdown generation for community and root files."""

import html
from datetime import UTC, datetime

from lib.utils import escape_markdown, format_date, format_number, format_tags


def generate_answers_md(community_name, site_url, answers, question_details):
    """Generate the answers.md content."""
    lines = [
        f"# {community_name} \u2014 Answers",
        "",
        "| # | Score | Accepted | Title | Tags | Date |",
        "|---|-------|----------|-------|------|------|",
    ]
    for i, a in enumerate(answers, 1):
        score = format_number(a["score"])
        accepted = "\u2713" if a.get("is_accepted", False) else ""
        qid = a.get("question_id", 0)
        details = question_details.get(qid, {})
        title = escape_markdown(details.get("title", "Untitled"))
        link = f"{site_url}/a/{a['answer_id']}"
        tags_str = format_tags(details.get("tags", []))
        date = format_date(a["creation_date"])
        lines.append(
            f"| {i} | {score} | {accepted} | [{title}]({link}) | {tags_str} | {date} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_questions_md(community_name, site_url, questions):
    """Generate the questions.md content."""
    lines = [
        f"# {community_name} \u2014 Questions",
        "",
        "| # | Score | Views | Answers | Accepted | Title | Tags | Date |",
        "|---|-------|-------|---------|----------|-------|------|------|",
    ]
    for i, q in enumerate(questions, 1):
        score = format_number(q["score"])
        views = format_number(q.get("view_count", 0))
        ans_count = format_number(q.get("answer_count", 0))
        accepted = "\u2713" if q.get("accepted_answer_id") else ""
        title = escape_markdown(q.get("title", "Untitled"))
        link = f"{site_url}/q/{q['question_id']}"
        tags_str = format_tags(q.get("tags", []))
        date = format_date(q["creation_date"])
        lines.append(
            f"| {i} | {score} | {views} | {ans_count} | {accepted} | [{title}]({link}) | {tags_str} | {date} |"
        )
    lines.append("")
    return "\n".join(lines)


def generate_community_readme(account, site_name, answer_count, question_count):
    """Generate the community README.md content."""
    site_url = account["site_url"]
    user_id = account["user_id"]
    community_name = html.unescape(account.get("site_name", site_name))
    reputation = format_number(account.get("reputation", 0))
    creation_date = format_date(account["creation_date"])
    badges = account.get("badge_counts", {})
    gold = badges.get("gold", 0)
    silver = badges.get("silver", 0)
    bronze = badges.get("bronze", 0)

    lines = [
        f"# {community_name}",
        "",
        f"[Profile]({site_url}/users/{user_id}) | Reputation: {reputation} | Member since: {creation_date}",
        "",
        "| | Count |",
        "|---|---|",
        f"| Answers | {format_number(answer_count)} |",
        f"| Questions | {format_number(question_count)} |",
        f"| Gold Badges | {format_number(gold)} |",
        f"| Silver Badges | {format_number(silver)} |",
        f"| Bronze Badges | {format_number(bronze)} |",
        "",
    ]
    return "\n".join(lines)


def generate_root_readme(community_data):
    """Generate the root README.md content."""
    now = datetime.now(UTC).strftime("%Y-%m-%d")

    lines = [
        "# Stack Exchange Activity Tracker",
        "",
        "My Q&A across every Stack Exchange community, refreshed weekly by"
        " [`track.py`](track.py) and stored per community under"
        " [`data/`](data/).",
        "",
        "## Setup",
        "",
        "Add a free [Stack Apps key](https://stackapps.com/apps/oauth/register)"
        " as the `STACKEXCHANGE_KEY` repo secret. Without it the unauthenticated"
        " [quota](https://api.stackexchange.com/docs/throttle) (300 requests/day"
        " per IP) throttles CI; the key raises it to 10,000/day.",
        "",
        "## Summary",
        "",
        f"> Updated {now}",
        "",
        "| Community | Reputation | Answers | Questions | Gold | Silver | Bronze |",
        "|-----------|-----------|---------|-----------|------|--------|--------|",
    ]

    total_rep = 0
    total_answers = 0
    total_questions = 0
    total_gold = 0
    total_silver = 0
    total_bronze = 0

    # Sort by reputation descending
    sorted_data = sorted(
        community_data, key=lambda x: x["account"].get("reputation", 0), reverse=True
    )

    for entry in sorted_data:
        account = entry["account"]
        site_url = account["site_url"]
        user_id = account["user_id"]
        community_name = html.unescape(account.get("site_name", entry["site"]))
        rep = account.get("reputation", 0)
        ans = entry["answer_count"]
        qs = entry["question_count"]
        badges = account.get("badge_counts", {})
        gold = badges.get("gold", 0)
        silver = badges.get("silver", 0)
        bronze = badges.get("bronze", 0)

        total_rep += rep
        total_answers += ans
        total_questions += qs
        total_gold += gold
        total_silver += silver
        total_bronze += bronze

        lines.append(
            f"| [{community_name}]({site_url}/users/{user_id}) "
            f"| {format_number(rep)} | {format_number(ans)} | {format_number(qs)} "
            f"| {format_number(gold)} | {format_number(silver)} | {format_number(bronze)} |"
        )

    lines.append(
        f"| **Total** | **{format_number(total_rep)}** | **{format_number(total_answers)}** "
        f"| **{format_number(total_questions)}** | **{format_number(total_gold)}** "
        f"| **{format_number(total_silver)}** | **{format_number(total_bronze)}** |"
    )
    lines.append("")
    return "\n".join(lines)
