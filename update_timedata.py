"""
update_timedata.py — Fetches current postcards_received from postcrossing.com
and appends a new row to docs/TimeData.csv (2x per day via GitHub Actions).

TimeData.csv format:
    datetime,postcards_received
    2026-06-15 06:40:12,87076078
"""

import csv
import os
import random
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

try:
    from fake_useragent import UserAgent as _UA
    _ua_gen = _UA()
    def _random_ua() -> str:
        return _ua_gen.random
except Exception:
    import random as _random
    _FALLBACK_UAS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    ]
    def _random_ua() -> str:
        return _random.choice(_FALLBACK_UAS)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
URL        = "https://www.postcrossing.com/"
TIMEOUT    = 10

DOCS_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
TIMEDATA_PATH = os.path.join(DOCS_DIR, "TimeData.csv")
FIELDNAMES    = ["datetime", "postcards_received"]


# ---------------------------------------------------------------------------
# Fetch
# ---------------------------------------------------------------------------

def fetch_received() -> int | None:
    """Fetch postcards_received from postcrossing.com. Returns int or None."""
    time.sleep(random.uniform(1, 3))
    try:
        resp = requests.get(URL, headers={"User-Agent": _random_ua()}, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[update_timedata] Network error: {exc}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    patterns = [
        r"([\d,]+)\s+postcards?\s+received",
        r"received\s+([\d,]+)\s+postcards?",
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            val_str = re.sub(r"[^\d]", "", m.group(1))
            if val_str:
                val = int(val_str)
                if val > 1_000_000:
                    print(f"[update_timedata] Parsed postcards_received = {val:,}")
                    return val

    print("[update_timedata] ERROR: could not parse postcards_received from page")
    return None


# ---------------------------------------------------------------------------
# TimeData.csv helpers
# ---------------------------------------------------------------------------

def last_received_in_csv() -> int | None:
    """Return the postcards_received of the last non-zero row, or None."""
    if not os.path.exists(TIMEDATA_PATH):
        return None
    try:
        with open(TIMEDATA_PATH, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        # Walk backwards to find last valid row
        for row in reversed(rows):
            val = row.get("postcards_received", "0") or "0"
            try:
                n = int(float(val))
                if n > 0:
                    return n
            except (ValueError, TypeError):
                continue
    except Exception:
        pass
    return None


def append_row(received: int, now: datetime) -> None:
    """Append one new row to TimeData.csv. Creates file with header if missing."""
    os.makedirs(DOCS_DIR, exist_ok=True)
    file_exists = os.path.exists(TIMEDATA_PATH) and os.path.getsize(TIMEDATA_PATH) > 0

    # Check if header already present (could be old format)
    needs_header = not file_exists
    if file_exists:
        with open(TIMEDATA_PATH, encoding="utf-8-sig") as fh:
            first_line = fh.readline().strip()
        if "datetime" not in first_line:
            # Old format — don't append, just warn
            print("[update_timedata] WARNING: TimeData.csv has old format header. Skipping append.")
            print(f"[update_timedata] Header found: {first_line}")
            return

    dt_str = now.strftime("%Y-%m-%d %H:%M:%S")

    row = {
        "datetime":           dt_str,
        "postcards_received": str(received),
    }

    with open(TIMEDATA_PATH, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        if needs_header:
            writer.writeheader()
        writer.writerow(row)

    print(f"[update_timedata] Appended: {row}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    now = datetime.now(timezone.utc)
    print(f"[update_timedata] Starting at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}")

    received = fetch_received()
    if received is None:
        print("[update_timedata] Skipping — could not fetch data.")
        return

    last = last_received_in_csv()
    if last is not None and last == received:
        print(f"[update_timedata] No change (last={last:,}) — skipping duplicate.")
        return

    append_row(received, now)
    print("[update_timedata] Done.")


if __name__ == "__main__":
    main()
