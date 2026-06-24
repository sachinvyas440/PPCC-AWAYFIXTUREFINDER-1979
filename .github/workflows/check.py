#!/usr/bin/env python3
"""
Checks thefixturelist.org.uk 'Home fixture offered' category for new listings,
and sends a free push notification (via ntfy.sh) when something new appears.

State (the list of listings already seen) is stored in state.json, which the
GitHub Actions workflow commits back to the repo after each run.
"""

import json
import os
import sys
import urllib.request

URL = "https://thefixturelist.org.uk/?page_id=209&acadp_category=home_fixture_offered"
STATE_FILE = "state.json"

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")


def fetch_page(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_listing_links(html: str):
    import re
    import html as html_module

    pattern = re.compile(
        r'<a[^>]+href="([^"]*\?acadp_listings=[^"]+)"[^>]*>(.*?)</a>',
        re.IGNORECASE | re.DOTALL,
    )
    listings = {}
    for href, text in pattern.findall(html):
        title = re.sub(r"<[^>]+>", "", text).strip()
        title = html_module.unescape(title)
        if title:
            listings[href] = title

    if not listings:
        items = re.findall(r'<li[^>]*class="[^"]*acadp[^"]*"[^>]*>(.*?)</li>',
                            html, re.IGNORECASE | re.DOTALL)
        for i, block in enumerate(items):
            title = re.sub(r"<[^>]+>", " ", block).strip()
            if title:
                listings[f"fallback-{i}-{hash(title)}"] = title[:200]

    return listings


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def notify(new_listings: dict):
    if not NTFY_TOPIC:
        print("NTFY_TOPIC not set — skipping notification, but new listings found:")
        for href, title in new_listings.items():
            print(f"  - {title} -> {href}")
        return

    lines = [f"- {title}" for title in new_listings.values()]
    message = "New 'Home fixture offered' listing(s):\n" + "\n".join(lines)
    message += f"\n\n{URL}"

    req = urllib.request.Request(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={
            "Title": "New fixture posted on TheFixtureList",
            "Priority": "high",
            "Tags": "cricket_bat",
        },
        method="POST",
    )
    try:
        urllib.request.urlopen(req, timeout=15)
        print("Notification sent.")
    except Exception as e:
        print(f"Failed to send notification: {e}", file=sys.stderr)


def main():
    html = fetch_page(URL)
    current = extract_listing_links(html)
    previous = load_state()

    if not previous:
        print(f"First run — recording {len(current)} existing listing(s) as baseline.")
        save_state(current)
        return

    new_hrefs = set(current.keys()) - set(previous.keys())
    new_listings = {h: current[h] for h in new_hrefs}

    if new_listings:
        print(f"Found {len(new_listings)} new listing(s).")
        notify(new_listings)
    else:
        print("No new listings.")

    save_state(current)


if __name__ == "__main__":
    main()
