"""
build_received_report.py — Reads docs/history.csv and produces:
  - docs/received_report.csv  (datetime, postcards_received) — 2 snapshots/day
  - Updates docs/index.html with the received-growth chart (via build_dashboard)

Snapshot windows (UTC):
  Morning : 06:00 – 08:00
  Evening : 20:00 – 22:00

For each window the record closest to the window centre is selected.
If no record falls inside the window, nothing is written for that slot.
"""

import csv
import os
from datetime import datetime, timezone, date, timedelta

import pandas as pd

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
HISTORY_CSV  = os.path.join(DOCS_DIR, "history.csv")
REPORT_CSV   = os.path.join(DOCS_DIR, "received_report.csv")
REPORT_FIELDS = ["datetime", "postcards_received"]

# Window definitions: (start_hour_UTC, end_hour_UTC, centre_hour)
WINDOWS = [
    (6,  8,  7),   # morning
    (20, 22, 21),  # evening
]


def pick_snapshot(df: pd.DataFrame, target_date: date, h_start: int, h_end: int) -> dict | None:
    """
    From df, pick the row inside [h_start, h_end) UTC on target_date
    that is closest to the window centre.
    Returns a dict or None.
    """
    lo = datetime(target_date.year, target_date.month, target_date.day,
                  h_start, 0, 0, tzinfo=timezone.utc)
    hi = datetime(target_date.year, target_date.month, target_date.day,
                  h_end,   0, 0, tzinfo=timezone.utc)
    centre = lo + (hi - lo) / 2

    mask = (df["timestamp"] >= lo) & (df["timestamp"] < hi)
    window_df = df[mask].copy()
    if window_df.empty:
        return None

    window_df["_dist"] = (window_df["timestamp"] - centre).abs()
    best = window_df.loc[window_df["_dist"].idxmin()]

    val = best["postcards_received"]
    if pd.isna(val):
        return None

    return {
        "datetime": best["timestamp"].strftime("%Y-%m-%d %H:%M:%S UTC"),
        "postcards_received": int(val),
    }


def build_report() -> None:
    if not os.path.exists(HISTORY_CSV):
        print("[report] history.csv not found — skipping.")
        return

    df = pd.read_csv(HISTORY_CSV, parse_dates=["timestamp"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.dropna(subset=["postcards_received"]).copy()
    df["postcards_received"] = pd.to_numeric(df["postcards_received"], errors="coerce")
    df = df.dropna(subset=["postcards_received"])

    if df.empty:
        print("[report] No valid postcards_received data.")
        return

    # --- Load existing report to avoid duplicates ---
    existing: dict[str, int] = {}  # datetime_str -> value
    if os.path.exists(REPORT_CSV):
        with open(REPORT_CSV, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                existing[row["datetime"]] = int(row["postcards_received"])

    # --- Iterate over all dates present in history ---
    dates = sorted(df["timestamp"].dt.date.unique())
    new_rows = 0
    for d in dates:
        for h_start, h_end, _ in WINDOWS:
            snap = pick_snapshot(df, d, h_start, h_end)
            if snap and snap["datetime"] not in existing:
                existing[snap["datetime"]] = snap["postcards_received"]
                new_rows += 1

    if new_rows == 0:
        print("[report] No new snapshots.")
        return

    # --- Write report sorted by datetime ---
    os.makedirs(DOCS_DIR, exist_ok=True)
    sorted_rows = [
        {"datetime": k, "postcards_received": v}
        for k, v in sorted(existing.items())
    ]
    with open(REPORT_CSV, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(sorted_rows)

    print(f"[report] Written {len(sorted_rows)} rows (+{new_rows} new) → {REPORT_CSV}")


if __name__ == "__main__":
    build_report()
