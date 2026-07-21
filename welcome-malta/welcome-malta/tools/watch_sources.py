#!/usr/bin/env python3
"""
watch_sources.py — watched-facts monitor for Welcome Malta.

check_links.py answers "does the page still exist?" — this answers the more
dangerous question: "does the page still SAY the same thing?" (e.g. DIER
announces the new minimum wage every January; the URL never changes).

How it works
------------
Each WATCH entry pins one or more literal strings to an official source page.
On every run, the page is fetched and checked; a missing pin means the value
on the official page has changed (or the page was restructured) → a human must
review and, if the change is legitimate, update BOTH the app copy and the pin.

Entries flagged `manual: True` are never fetched — gov.mt sites bot-block
datacenter traffic (403), so they are printed as a human review checklist
instead. Run this on the 1st of each month; exit code 1 = review required.

Usage:
    python3 tools/watch_sources.py            # check everything, keep a state log
    python3 tools/watch_sources.py --state .watch-state.json
"""

import argparse
import json
import re
import ssl
import sys
import urllib.request
from datetime import date
from html import unescape

HDR = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                  "Version/17.0 Mobile/15E148 Safari/604.1 WelcomeMalta-Watch/1.0"
}

# ---------------------------------------------------------------------------
# WATCH LIST — the app's most volatile facts, pinned to their sources.
# `pin`: literal strings that MUST be present in the page HTML.
# ---------------------------------------------------------------------------
WATCH = [
    {
        "key": "minWage",
        "why": "Minimum wage + COLA are re-set every January (Budget measure)",
        "url": "https://dier.gov.mt/en/services/employment-conditions/wages/national-minimum-wage/",
        "pin": ["229.44"],          # 2026 rate, age 18+ whole-time
    },
    {
        "key": "tallinja",
        "manual": True,
        "why": "MyTallinja plan names/prices changed in 2026 (site is JS-rendered → manual check)",
        "url": "https://www.publictransport.com.mt",
    },
    {
        "key": "eResidence",
        "why": "Identità response-time promise",
        "url": "https://identita.gov.mt/expatriates-unit-main-page/eu-nationals/eresidence-document-application/",
        "pin": ["48"],
    },
    {
        "key": "tms",
        "why": "TMS scheme existence/URL",
        "url": "https://eures.europa.eu/eures-services/eures-targeted-mobility-scheme-tms_en",
        "pin": ["Targeted Mobility"],
    },
    # ---- carried over to the human checklist (bot-blocked from scripts) ----
    {
        "key": "minWage-manual",
        "manual": True,
        "why": "Annual minimum wage change (announcement ~Oct Budget, effective 1 Jan)",
        "url": "https://dier.gov.mt",
    },
    {
        "key": "taxId-manual",
        "manual": True,
        "why": "Tax registration process for EU nationals",
        "url": "https://cfr.gov.mt",
    },
    {
        "key": "qualsRegulated-manual",
        "manual": True,
        "why": "MFHEA regulated-professions list changes",
        "url": "https://mfhea.mt",
    },
]

def fetch(url: str, timeout: float = 10.0) -> str:
    req = urllib.request.Request(url, headers=HDR)
    with urllib.request.urlopen(req, timeout=timeout, context=ssl.create_default_context()) as r:
        raw = r.read().decode("utf-8", errors="replace")
    return unescape(re.sub(r"<[^>]+>", " ", raw))  # strip tags for text matching


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=".watch-state.json")
    args = ap.parse_args()

    try:
        state = json.load(open(args.state))
    except FileNotFoundError:
        state = {}

    problems, manual_queue = [], []
    print(f"Watched-facts monitor — {date.today().isoformat()}\n")

    for w in WATCH:
        if w.get("manual"):
            manual_queue.append(w)
            continue
        try:
            text = fetch(w["url"])
        except Exception as e:
            print(f"🛡️  {w['key']}: unreachable — likely bot-blocked ({getattr(e,'code',str(e)[:40])}) "
                  f"→ moved to manual checklist")
            manual_queue.append(w)
            continue
        missing = [p for p in w["pin"] if p not in text]
        if missing:
            print(f"⚠️  {w['key']}: CHANGED — pins not found: {missing}")
            print(f"    why it matters: {w['why']}")
            print(f"    review: {w['url']}\n")
            problems.append(w["key"])
        else:
            print(f"✅ {w['key']}: pins intact ({', '.join(w['pin'])})")
        state.setdefault(w["key"], {})[date.today().isoformat()] = "changed" if missing else "ok"

    if manual_queue:
        print("\nManual spot-check queue (bot-blocked for automation — open in a browser):")
        for w in manual_queue:
            print(f"  □ {w['key']}: {w['why']}\n    {w['url']}")

    json.dump(state, open(args.state, "w"), indent=2)
    print(f"\nState logged to {args.state} · {len(problems)} changed topic(s) need review")

    if problems:
        print("\nACTION: open the flagged pages, and if the change is genuine, "
              "update the card copy AND pin in tools/watch_sources.py and the "
              "`verified:` date in the REGISTRY in index.html.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
