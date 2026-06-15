"""
convert_timedata.py — Reads docs/TimeData.csv (Daily Growth data),
parses dates, and writes docs/received_report.csv with columns:
    datetime, postcards_received

Expected input format (docs/TimeData.csv):
    Date,UTC,JD,Days of PC,Received
    MM/DD/YYYY,HH:MM:SS AM/PM,...,...,53518665

Then rebuilds docs/index.html via build_dashboard.py.

Run locally:
    python convert_timedata.py

Also called automatically by GitHub Actions workflow.
"""

import csv
import os
import subprocess
import sys
from datetime import datetime

DOCS_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")
INPUT_CSV  = os.path.join(DOCS_DIR, "TimeData.csv")
OUTPUT_CSV = os.path.join(DOCS_DIR, "received_report.csv")


def parse_row(row: dict) -> tuple[str, int] | None:
    """
    Parse one row of Daily Growth CSV.
    Returns (datetime_str, received) or None if invalid.

    Date column: 'MM/DD/YYYY' or 'MM/DD/YYYY HH:MM:SS' (some rows have combined)
    UTC  column: 'HH:MM:SS AM/PM' or 'HH:MM:SS'
    """
    date_raw = row.get("Date", "").strip()
    utc_raw  = row.get("UTC",  "").strip()

    # Skip header-like or zero rows
    try:
        received = int(float(row.get("Received", "0")))
    except (ValueError, TypeError):
        return None
    if received <= 0:
        return None

    # --- Parse date ---
    # Some rows have date+time merged: "MM/DD/YYYY HH:MM:SS"
    date_part = date_raw.split()[0]   # take only the date part
    try:
        # Try MM/DD/YYYY
        dt_date = datetime.strptime(date_part, "%m/%d/%Y")
    except ValueError:
        try:
            # Try DD/MM/YYYY (TimeData.xls legacy)
            dt_date = datetime.strptime(date_part, "%d/%m/%Y")
        except ValueError:
            return None

    # --- Parse time ---
    # UTC column can be: "11:15:00 PM", "23:15", "01:22:00 AM", "19:15:03.168"
    time_str = utc_raw.strip()
    dt_time  = None
    for fmt in ("%I:%M:%S %p", "%I:%M %p", "%H:%M:%S", "%H:%M", "%H:%M:%S.%f"):
        try:
            dt_time = datetime.strptime(time_str, fmt)
            break
        except ValueError:
            continue

    if dt_time is None:
        # fallback: midnight
        dt_time = datetime.strptime("00:00:00", "%H:%M:%S")

    # --- Combine ---
    dt = dt_date.replace(
        hour=dt_time.hour,
        minute=dt_time.minute,
        second=dt_time.second,
    )
    dt_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    return dt_str, received


def main() -> None:
    if not os.path.exists(INPUT_CSV):
        print(f"[convert] ERROR: {INPUT_CSV} not found")
        print("[convert] Please copy your Daily Growth CSV as docs/TimeData.csv")
        sys.exit(1)

    rows_out: list[dict] = []
    skipped = 0
    errors  = 0

    with open(INPUT_CSV, newline="", encoding="utf-8-sig") as fh:
        # Detect delimiter
        sample = fh.read(2048)
        fh.seek(0)
        delimiter = "\t" if "\t" in sample.split("\n")[0] else ","
        reader = csv.DictReader(fh, delimiter=delimiter)
        for i, row in enumerate(reader):
            result = parse_row(row)
            if result is None:
                skipped += 1
                continue
            dt_str, received = result
            rows_out.append({"datetime": dt_str, "postcards_received": received})

    if not rows_out:
        print(f"[convert] ERROR: no valid rows found (skipped={skipped})")
        sys.exit(1)

    # Sort by datetime
    rows_out.sort(key=lambda r: r["datetime"])

    # Remove duplicates (keep last)
    seen: dict[str, int] = {}
    for r in rows_out:
        seen[r["datetime"]] = r["postcards_received"]
    rows_out = [{"datetime": k, "postcards_received": v} for k, v in sorted(seen.items())]

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["datetime", "postcards_received"])
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"[convert] Written {len(rows_out)} rows → {OUTPUT_CSV}  (skipped {skipped})")
    print(f"[convert] First: {rows_out[0]}")
    print(f"[convert] Last:  {rows_out[-1]}")

    # Rebuild dashboard
    dashboard_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_dashboard.py")
    print("[convert] Rebuilding dashboard...")
    result = subprocess.run([sys.executable, dashboard_script])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
