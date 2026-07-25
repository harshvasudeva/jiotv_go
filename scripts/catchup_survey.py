#!/usr/bin/env python3
"""Survey catchup (and optionally live) availability channel by channel.

Deliberately paced: one request at a time with a delay between them, so the
survey looks like ordinary browsing rather than a burst that could get the
client rate-limited or blocked.

Usage:
    python scripts/catchup_survey.py                     # 40 channels, catchup
    python scripts/catchup_survey.py --limit 0           # every channel
    python scripts/catchup_survey.py --delay 2.5         # slower
    python scripts/catchup_survey.py --mode live         # survey live instead
    python scripts/catchup_survey.py --only-catchup-flag # skip channels the API
                                                         # marks as no-catchup
    python scripts/catchup_survey.py --csv out.csv
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

DEFAULT_BASE = "http://127.0.0.1:5001"

# A catchup programme link as rendered on /catchup/<id>.
PLAY_LINK = re.compile(
    r"catchup/play/(?P<id>\d+)\?start=(?P<start>\d+)&(?:amp;)?end=(?P<end>\d+)&(?:amp;)?srno=(?P<srno>\d+)"
)


def fetch(url: str, timeout: int, follow: bool = True):
    """Return (status, body, final_url). Never raises for HTTP errors."""
    opener = urllib.request.build_opener()
    if not follow:
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *_args, **_kwargs):
                return None

        opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": "catchup-survey/1.0"})
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, response.read(), response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), getattr(exc, "url", url)
    except Exception as exc:  # noqa: BLE001 - network/timeout/DNS all reported the same way
        return None, str(exc).encode(), url


def classify(status, body: bytes) -> str:
    """Turn an HTTP result into a short verdict."""
    if status is None:
        return "network-error"
    if status in (301, 302, 303, 307, 308):
        return "redirect-not-followed"
    if status != 200:
        return f"http-{status}"
    if not body:
        return "empty-body"
    head = body.lstrip()[:7]
    if head.startswith(b"#EXTM3U"):
        return "ok"
    if body.lstrip()[:1] == b"<":
        return "html-not-manifest"
    return "unknown-payload"


def load_channels(base: str, timeout: int):
    status, body, _ = fetch(f"{base}/channels", timeout)
    if status != 200:
        sys.exit(f"could not read {base}/channels (HTTP {status})")
    payload = json.loads(body)
    return payload.get("result") or payload.get("channels") or []


def first_programme(base: str, channel_id: str, timeout: int):
    """Return (start, end, srno) for a past programme, or None."""
    status, body, _ = fetch(f"{base}/catchup/{channel_id}", timeout)
    if status != 200:
        return None
    matches = PLAY_LINK.findall(body.decode("utf-8", "replace"))
    if not matches:
        return None
    # Pick a middle entry: the newest may not be fully packaged yet, and the
    # oldest may have aged out of the catchup window.
    _cid, start, end, srno = matches[len(matches) // 2]
    return start, end, srno


def survey(args) -> int:
    channels = load_channels(args.base, args.timeout)
    if not channels:
        sys.exit("no channels returned")

    rows = [
        {
            "id": str(c.get("channel_id") or c.get("id")),
            "name": c.get("channel_name") or c.get("name") or "",
            "catchup_flag": bool(c.get("isCatchupAvailable")),
            "needs_subscription": bool(c.get("requiresSubscription")),
        }
        for c in channels
    ]

    if args.only_catchup_flag:
        rows = [r for r in rows if r["catchup_flag"]]
    if args.skip_locked:
        rows = [r for r in rows if not r["needs_subscription"]]

    random.seed(args.seed)
    if args.limit and args.limit < len(rows):
        rows = random.sample(rows, args.limit)
    rows.sort(key=lambda r: int(r["id"]))

    total = len(rows)
    delay_note = f"{args.delay}s between requests"
    print(f"surveying {total} channels in {args.mode} mode ({delay_note})\n")
    print(f"{'id':>6}  {'channel':<30} {'flag':<5} {'verdict':<22} detail")
    print("-" * 96)

    verdicts = Counter()
    results = []

    for index, row in enumerate(rows, 1):
        detail = ""
        if args.mode == "live":
            status, body, _ = fetch(f"{args.base}/live/{row['id']}.m3u8", args.timeout)
            verdict = classify(status, body)
        else:
            programme = first_programme(args.base, row["id"], args.timeout)
            if not programme:
                verdict, status = "no-programmes-listed", None
            else:
                time.sleep(args.delay)  # pace the second call too
                start, end, srno = programme
                query = urllib.parse.urlencode({"start": start, "end": end, "srno": srno})
                status, body, _ = fetch(
                    f"{args.base}/catchup/stream/{row['id']}?{query}", args.timeout
                )
                verdict = classify(status, body)
                if verdict == "ok":
                    rewritten = body.count(b"/render.m3u8?auth=")
                    detail = f"{len(body)}B, {rewritten} rewritten"
                    if rewritten == 0:
                        verdict = "ok-but-unrewritten"
                elif status not in (None, 200):
                    detail = body[:60].decode("utf-8", "replace").replace("\n", " ")

        verdicts[verdict] += 1
        results.append({**row, "verdict": verdict, "status": status, "detail": detail})
        flag = "yes" if row["catchup_flag"] else "no"
        print(f"{row['id']:>6}  {row['name'][:30]:<30} {flag:<5} {verdict:<22} {detail[:34]}")

        if index < total:
            time.sleep(args.delay)

    print("\n" + "=" * 96)
    print("summary")
    for verdict, count in verdicts.most_common():
        print(f"  {verdict:<24} {count:>4}  ({100 * count / total:.0f}%)")

    # Does the API's catchup flag actually predict success?
    flagged = [r for r in results if r["catchup_flag"]]
    unflagged = [r for r in results if not r["catchup_flag"]]
    if flagged and unflagged:
        ok_flagged = sum(1 for r in flagged if r["verdict"] == "ok")
        ok_unflagged = sum(1 for r in unflagged if r["verdict"] == "ok")
        print("\nisCatchupAvailable as a predictor:")
        print(f"  flag=true : {ok_flagged}/{len(flagged)} playable")
        print(f"  flag=false: {ok_unflagged}/{len(unflagged)} playable")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["id", "name", "catchup_flag", "needs_subscription", "verdict", "status", "detail"]
            )
            writer.writeheader()
            writer.writerows(results)
        print(f"\nwrote {args.csv}")

    return 0 if verdicts["ok"] else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--base", default=DEFAULT_BASE, help="server base URL")
    parser.add_argument("--mode", choices=["catchup", "live"], default="catchup")
    parser.add_argument("--limit", type=int, default=40, help="channels to sample; 0 = all")
    parser.add_argument("--delay", type=float, default=1.5, help="seconds between requests")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--seed", type=int, default=7, help="sampling seed, for reproducible runs")
    parser.add_argument("--only-catchup-flag", action="store_true", help="only channels with isCatchupAvailable")
    parser.add_argument("--skip-locked", action="store_true", help="skip channels needing a subscription")
    parser.add_argument("--csv", help="also write results to this CSV file")
    return survey(parser.parse_args())


if __name__ == "__main__":
    sys.exit(main())
