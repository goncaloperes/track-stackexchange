#!/usr/bin/env python3
"""Stack Exchange activity tracker.

Fetches all Q&A activity for a user across all Stack Exchange communities
and generates organized markdown files.
"""

import html
import os
import shutil

from lib.utils import SCRIPT_DIR, DATA_DIR, NETWORK_USER_ID
from lib.api import (
    fetch_associated_accounts,
    fetch_answers,
    fetch_questions,
    fetch_question_details,
    site_name_from_url,
)
from lib.markdown import (
    generate_root_readme,
    generate_community_readme,
    generate_answers_md,
    generate_questions_md,
)


def main():
    os.chdir(SCRIPT_DIR)
    os.makedirs(DATA_DIR, exist_ok=True)

    accounts = fetch_associated_accounts(NETWORK_USER_ID)

    # Filter to accounts with at least 1 question or 1 answer
    active_accounts = [
        a
        for a in accounts
        if a.get("answer_count", 0) > 0 or a.get("question_count", 0) > 0
    ]
    print(f"Active communities (with posts): {len(active_accounts)}")

    community_data = []

    for account in active_accounts:
        site_url = account["site_url"]
        site = site_name_from_url(site_url)
        user_id = account["user_id"]
        community_name = html.unescape(account.get("site_name", site))
        answer_count = account.get("answer_count", 0)
        question_count = account.get("question_count", 0)

        print(f"\nProcessing {community_name} ({site})...")

        # Fetch answers
        answers = []
        question_details = {}
        if answer_count > 0:
            answers = fetch_answers(site, user_id)
            qids = [a["question_id"] for a in answers if "question_id" in a]
            if qids:
                question_details = fetch_question_details(site, qids)

        # Fetch questions
        questions = []
        if question_count > 0:
            questions = fetch_questions(site, user_id)

        # Skip communities with no actual posts fetched
        if not answers and not questions:
            print(f"  Skipping {community_name} — no posts found")
            continue

        # Create community directory inside data/
        community_dir = os.path.join(DATA_DIR, site)
        os.makedirs(community_dir, exist_ok=True)

        # Write community README
        readme_content = generate_community_readme(
            account, site, len(answers), len(questions)
        )
        with open(os.path.join(community_dir, "README.md"), "w") as f:
            f.write(readme_content)

        # Write answers.md
        if answers:
            answers_content = generate_answers_md(
                community_name, site_url, answers, question_details
            )
            with open(os.path.join(community_dir, "answers.md"), "w") as f:
                f.write(answers_content)

        # Write questions.md
        if questions:
            questions_content = generate_questions_md(
                community_name, site_url, questions
            )
            with open(os.path.join(community_dir, "questions.md"), "w") as f:
                f.write(questions_content)

        community_data.append(
            {
                "site": site,
                "account": account,
                "answer_count": len(answers),
                "question_count": len(questions),
            }
        )

    # Clean up directories for communities that are no longer active
    existing_dirs = {
        d
        for d in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, d)) and not d.startswith(".")
    }
    active_dirs = {entry["site"] for entry in community_data}
    for stale_dir in existing_dirs - active_dirs:
        stale_path = os.path.join(DATA_DIR, stale_dir)
        print(f"Removing stale directory: {stale_dir}")
        shutil.rmtree(stale_path)

    # Write root README
    root_readme = generate_root_readme(community_data)
    with open(os.path.join(SCRIPT_DIR, "README.md"), "w") as f:
        f.write(root_readme)

    print(f"\nDone! Updated {len(community_data)} communities.")


if __name__ == "__main__":
    main()
