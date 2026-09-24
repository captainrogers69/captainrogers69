"""Scrape the public contribution calendar and write data/contributions.json.

No token needed: reads https://github.com/users/<user>/contributions.
"""
import json
import os
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GH_USER", "captainrogers69")
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "contributions.json"

COUNT_RE = re.compile(r"^([\d,]+) contributions?")


def fetch_days():
    url = f"https://github.com/users/{USERNAME}/contributions"
    resp = requests.get(url, headers={"User-Agent": "profile-art-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    tips = {}
    for tip in soup.find_all("tool-tip"):
        m = COUNT_RE.match(tip.get_text(strip=True))
        tips[tip.get("for")] = int(m.group(1).replace(",", "")) if m else 0

    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({
            "date": td["data-date"],
            "count": tips.get(td.get("id"), 0),
            "level": int(td.get("data-level", 0)),
        })
    if not days:
        raise SystemExit("no contribution cells found; GitHub markup changed?")
    days.sort(key=lambda d: d["date"])
    return days


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["count"] else 0
        longest = max(longest, run)

    # Current streak may start yesterday: today not over yet.
    current = 0
    rev = list(reversed(days))
    if rev and rev[0]["count"] == 0:
        rev = rev[1:]
    for d in rev:
        if not d["count"]:
            break
        current += 1
    return current, longest


def main():
    days = fetch_days()
    current, longest = streaks(days)

    monthly = defaultdict(int)
    for d in days:
        monthly[d["date"][:7]] += d["count"]
    best_day = max(days, key=lambda d: d["count"])
    busiest = max(monthly.items(), key=lambda kv: kv[1])

    data = {
        "user": USERNAME,
        "generated": date.today().isoformat(),
        "days": days,
        "stats": {
            "total": sum(d["count"] for d in days),
            "active_days": sum(1 for d in days if d["count"]),
            "current_streak": current,
            "longest_streak": longest,
            "best_day": {"date": best_day["date"], "count": best_day["count"]},
            "busiest_month": {"month": busiest[0], "count": busiest[1]},
            "monthly": dict(sorted(monthly.items())),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2) + "\n")
    s = data["stats"]
    print(f"{len(days)} days, {s['total']} contributions, "
          f"streak {s['current_streak']} (longest {s['longest_streak']})")


if __name__ == "__main__":
    main()
