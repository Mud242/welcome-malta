#!/usr/bin/env python3
"""
check_links.py — dead-link guard for Welcome Malta.

Crawls every external URL (href / src="https…") found in the given HTML file(s),
issues HEAD (falls back to GET) requests, and reports:
  - hard failures (DNS / connection / 4xx / 5xx)
  - redirects (often harmless, but flagged so you can update to the final URL)

Usage:
    python3 tools/check_links.py index.html
    python3 tools/check_links.py index.html --timeout 8 --verbose

Exit code: 0 = all good (redirects only), 1 = at least one hard failure.
Hook it into a monthly cron / GitHub Action; non-zero exit breaks the build,
which is exactly the notification channel you want when a ministry reorganises
its website (again).
"""

import re
import sys
import ssl
import socket
import argparse
import urllib.request
import urllib.error
from urllib.parse import urlparse

URL_RE = re.compile(r'(?:href|src)\s*=\s*"(https?://[^"]+)"', re.I)

# Some gov sites block default curl/python UAs; look like a normal browser.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0 Safari/537.36 WelcomeMalta-LinkCheck/1.0"
}


def check(url: str, timeout: float, ctx: ssl.SSLContext):
    """Return (status_label, final_url_or_error)."""
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
            final = r.geturl()
            note = "redirect" if final.rstrip("/") != url.rstrip("/") else "ok"
            return note, final
    except urllib.error.HTTPError as e:
        if e.code == 405:  # HEAD not allowed -> try GET
            try:
                req = urllib.request.Request(url, headers=HEADERS)
                with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                    final = r.geturl()
                    note = "redirect" if final.rstrip("/") != url.rstrip("/") else "ok"
                    return note, final
            except Exception as ge:  # noqa: BLE001
                return "fail", f"GET after 405 failed: {ge}"
        if e.code in (301, 302, 303, 307, 308):
            loc = e.headers.get("Location", "?")
            return "redirect", loc
        # 403 from datacenter IPs is almost always WAF bot-blocking
        # (Cloudflare/Imperva on cfr.gov.mt, dier.gov.mt, jobsplus.gov.mt…),
        # NOT a dead link. Report for manual spot-check, don't fail CI.
        if e.code == 403:
            return "blocked", "HTTP 403 — likely bot-blocked; spot-check manually in a browser"
        return "fail", f"HTTP {e.code}"
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, OSError) as e:
        return "fail", str(e.reason if hasattr(e, "reason") else e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+", help="HTML files to scan")
    ap.add_argument("--timeout", type=float, default=10.0)
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    urls: set[str] = set()
    for path in args.files:
        with open(path, encoding="utf-8") as fh:
            urls.update(m.group(1) for m in URL_RE.finditer(fh.read()))

    urls = {u for u in urls if urlparse(u).netloc not in ("example.org",)}
    if not urls:
        print("No external URLs found.")
        return 0

    ctx = ssl.create_default_context()
    fails, redirects, blocked = [], [], []
    print(f"Checking {len(urls)} unique external links…\n")
    for u in sorted(urls):
        status, detail = check(u, args.timeout, ctx)
        icon = {"ok": "✅", "redirect": "↪️ ", "fail": "❌", "blocked": "🛡️ "}[status]
        if args.verbose or status != "ok":
            print(f"{icon} {u}")
            if status != "ok":
                print(f"    → {detail}")
        if status == "fail":
            fails.append(u)
        elif status == "redirect":
            redirects.append((u, detail))
        elif status == "blocked":
            blocked.append(u)

    print(f"\nSummary: {len(urls) - len(fails) - len(redirects) - len(blocked)} ok · "
          f"{len(redirects)} redirected · {len(blocked)} bot-blocked · {len(fails)} FAILED")
    if blocked:
        print("Bot-blocked (fine in browsers — spot-check occasionally):")
        for u in blocked:
            print(f"  🛡️  {u}")
    if redirects:
        print("Redirects to update (copy final URL into content registry):")
        for u, f in redirects:
            print(f"  {u}\n    → {f}")
    if fails:
        print("\nACTION REQUIRED — dead links:", *fails, sep="\n  ❌ ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
