"""
convert_timedata.py — Reads docs/TimeData.csv, parses dates,
writes docs/received_report.csv with columns: datetime, postcards_received
Then calls build_dashboard.py to regenerate docs/index.html.

Run once locally:
    python convert_timedata.py
"""

import csv
import os
import subprocess
import sys

DOCS_DIR   = os.path.join(os.path.dirname(__file__), "docs")
INPUT_CSV  = os.path.join(DOCS_DIR, "TimeData.csv")
OUTPUT_CSV = os.path.join(DOCS_DIR, "received_report.csv")


def parse_date(date_str: str, time_str: str) -> str | None:
    """
    Convert TimeData.csv date format to ISO-like string.
    Date column: '01/09/19 Sun'  ->  DD/MM/YY
    Time column: '23:15'
    Returns: '2019-09-01 23:15:00 UTC'
    """
    try:
        date_part = date_str.strip().split()[0]   # '01/09/19'
        d, m, y  = date_part.split("/")
        year     = 2000 + int(y) if int(y) < 100 else int(y)
        time_str = time_str.strip()
        return f"{year:04d}-{int(m):02d}-{int(d):02d} {time_str}:00 UTC"
    except Exception:
        return None


def main() -> None:
    if not os.path.exists(INPUT_CSV):
        print(f"[convert] ERROR: {INPUT_CSV} not found")
        sys.exit(1)

    rows_out = []
    skipped  = 0

    with open(INPUT_CSV, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            dt  = parse_date(row.get("Date", ""), row.get("UTC", ""))
            try:
                val = int(float(row.get("Received", "0")))
            except ValueError:
                val = 0
            if dt is None or val <= 0:
                skipped += 1
                continue
            rows_out.append({"datetime": dt, "postcards_received": val})

    # Sort by datetime
    rows_out.sort(key=lambda r: r["datetime"])

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["datetime", "postcards_received"])
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"[convert] Written {len(rows_out)} rows to {OUTPUT_CSV}  (skipped {skipped})")
    print(f"[convert] First: {rows_out[0]}")
    print(f"[convert] Last:  {rows_out[-1]}")

    # Rebuild dashboard
    print("[convert] Rebuilding dashboard...")
    result = subprocess.run(
        [sys.executable, os.path.join(os.path.dirname(__file__), "build_dashboard.py")],
        capture_output=False
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
