"""
update_timedata.py — Fetches current postcards_received from postcrossing.com
and appends a new row to docs/TimeData.csv.

Row format (matches Daily Growth data):
    Date,UTC,JD,Days of PC,Received
    MM/DD/YYYY,HH:MM:SS AM/PM,<julian>,<days_since_start>,<received>

Postcrossing started: 2005-07-04 (JD 38534, Days of PC 0)
Julian Day base: 2005-07-04 = JD 38534 (Excel serial date)
"""

import csv
import os
import random
import re
import time
from datetime import datetime, timezone, date

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
URL        = "https://www.postcrossing.com/"
USER_AGENT = (
    "Mozilla/5.0 (compatible; PostcrossingBot/1.0; "
    "+https://github.com/kam1k88/postcrossing)"
)
TIMEOUT    = 10

DOCS_DIR      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
TIMEDATA_PATH = os.path.join(DOCS_DIR, "TimeData.csv")

# Postcrossing epoch: 2005-07-04 as Excel serial date
PC_EPOCH_DATE    = date(2005, 7, 4)
EXCEL_EPOCH_DATE = date(1899, 12, 30)   # Excel day 0

FIELDNAMES = ["Date", "UTC", "JD", "Days of PC", "Received"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def excel_serial(d: date) -> float:
    """Convert a date to Excel serial date number (same as JD column in TimeData)."""
    return (d - EXCEL_EPOCH_DATE).days


def days_of_pc(d: date) -> float:
    """Days since Postcrossing started (2005-07-04)."""
    return (d - PC_EPOCH_DATE).days


def fetch_received() -> int | None:
    """Fetch postcards_received from postcrossing.com. Returns int or None."""
    time.sleep(random.uniform(1, 3))
    try:
        resp = requests.get(URL, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"[update_timedata] Network error: {exc}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    # Try "postcards received" pattern (handles both km and miles variants)
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
                if val > 1_000_000:   # sanity check
                    print(f"[update_timedata] Parsed postcards_received = {val:,}")
                    return val

    print("[update_timedata] ERROR: could not parse postcards_received from page")
    return None


def last_received_in_csv() -> int | None:
    """Return the Received value of the last row in TimeData.csv, or None."""
    if not os.path.exists(TIMEDATA_PATH):
        return None
    try:
        with open(TIMEDATA_PATH, newline="", encoding="utf-8-sig") as fh:
            rows = list(csv.DictReader(fh))
        if not rows:
            return None
        last = rows[-1]
        return int(float(last.get("Received", "0") or "0"))
    except Exception:
        return None


def append_row(received: int, now: datetime) -> None:
    """Append one new row to TimeData.csv (create with headers if missing)."""
    os.makedirs(DOCS_DIR, exist_ok=True)
    file_exists = os.path.exists(TIMEDATA_PATH)

    d = now.date()
    jd    = excel_serial(d)
    dopc  = float((d - PC_EPOCH_DATE).days)

    # Date: MM/DD/YYYY   UTC: HH:MM:SS AM/PM
    date_str = now.strftime("%m/%d/%Y")
    utc_str  = now.strftime("%I:%M:%S %p")   # 12-hour with AM/PM

    row = {
        "Date":        date_str,
        "UTC":         utc_str,
        "JD":          f"{jd + now.hour/24 + now.minute/1440 + now.second/86400:.7f}",
        "Days of PC":  f"{dopc + now.hour/24 + now.minute/1440 + now.second/86400:.7f}",
        "Received":    str(received),
    }

    with open(TIMEDATA_PATH, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        if not file_exists or os.path.getsize(TIMEDATA_PATH) == 0:
            writer.writeheader()
        writer.writerow(row)

    print(f"[update_timedata] Appended row: {row}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    now = datetime.now(timezone.utc)
    print(f"[update_timedata] Starting at {now.strftime('%Y-%m-%dT%H:%M:%SZ')}")

    received = fetch_received()
    if received is None:
        print("[update_timedata] Skipping update — could not fetch data.")
        return

    last = last_received_in_csv()
    if last is not None and last == received:
        print(f"[update_timedata] No change (last={last:,}) — skipping duplicate.")
        return

    append_row(received, now)
    print("[update_timedata] Done.")


if __name__ == "__main__":
    main()
