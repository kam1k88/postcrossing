"""
scraper.py — Parses 7 metrics from the Postcrossing homepage and appends
the new record to docs/history.csv and docs/history.json.
"""

import csv
import json
import os
import random
import re
import time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
URL = "https://www.postcrossing.com/"
USER_AGENT = (
    "Mozilla/5.0 (compatible; PostcrossingBot/1.0; "
    "+https://github.com/kam1k88/postcrossing)"
)
TIMEOUT = 10  # seconds

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
CSV_PATH = os.path.join(DOCS_DIR, "history.csv")
JSON_PATH = os.path.join(DOCS_DIR, "history.json")

CSV_FIELDS = [
    "timestamp",
    "members",
    "countries",
    "postcards_received",
    "received_last_hour",
    "postcards_traveling",
    "km_traveled",
    "laps_around_world",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _to_int(value: str | None) -> int | None:
    """Strip formatting and convert to int, return None on failure."""
    if value is None:
        return None
    cleaned = re.sub(r"[^\d]", "", value)
    return int(cleaned) if cleaned else None


def _to_float(value: str | None) -> float | None:
    """Strip formatting and convert to float, return None on failure."""
    if value is None:
        return None
    cleaned = re.sub(r"[^\d.]", "", value)
    try:
        return float(cleaned) if cleaned else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def fetch_page() -> str | None:
    """Fetch the Postcrossing homepage HTML. Returns None on any error."""
    # Polite random delay before the request
    delay = random.uniform(1, 3)
    time.sleep(delay)

    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(URL, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response.text
    except requests.RequestException as exc:
        print(f"[scraper] Network error: {exc}")
        return None


def parse_metrics(html: str | None) -> dict:
    """
    Extract the 7 metrics from the HTML.
    Returns a dict with all fields; missing values are None.
    """
    result = {field: None for field in CSV_FIELDS if field != "timestamp"}

    if html is None:
        return result

    # Use BeautifulSoup to get clean text, then regex for robustness
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)

    # Pattern helper: find a number that follows a keyword phrase
    def find_number(pattern: str) -> str | None:
        m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return m.group(1) if m else None

    # --- members ---
    result["members"] = _to_int(
        find_number(r"([\d,.\s]+)\s+members")
    )

    # --- countries ---
    result["countries"] = _to_int(
        find_number(r"([\d,.\s]+)\s+countries")
    )

    # --- postcards_received ---
    result["postcards_received"] = _to_int(
        find_number(r"([\d,.\s]+)\s+postcards?\s+received")
    )

    # --- received_last_hour ---
    result["received_last_hour"] = _to_int(
        find_number(r"([\d,.\s]+)\s+received\s+in\s+the\s+last\s+hour")
    )

    # --- postcards_traveling ---
    result["postcards_traveling"] = _to_int(
        find_number(r"([\d,.\s]+)\s+postcards?\s+traveling")
    )

    # --- km_traveled ---
    result["km_traveled"] = _to_int(
        find_number(r"([\d,.\s]+)\s+km\s+traveled")
    )

    # --- laps_around_world ---
    result["laps_around_world"] = _to_float(
        find_number(r"([\d,.\s]+)\s+laps?\s+around\s+the\s+world")
    )

    return result


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------

def update_history(new_record: dict) -> None:
    """
    Append new_record to docs/history.csv and docs/history.json.
    Creates files with headers on first run.
    """
    os.makedirs(DOCS_DIR, exist_ok=True)

    # ---- CSV ----------------------------------------------------------------
    records_csv: list[dict] = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            records_csv = list(reader)

    records_csv.append(new_record)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(records_csv)

    print(f"[scraper] CSV updated → {CSV_PATH} ({len(records_csv)} records)")

    # ---- JSON ---------------------------------------------------------------
    records_json: list[dict] = []
    if os.path.exists(JSON_PATH):
        try:
            with open(JSON_PATH, encoding="utf-8") as fh:
                records_json = json.load(fh)
        except (json.JSONDecodeError, ValueError):
            records_json = []

    records_json.append(new_record)

    with open(JSON_PATH, "w", encoding="utf-8") as fh:
        json.dump(records_json, fh, ensure_ascii=False, indent=2)

    print(f"[scraper] JSON updated → {JSON_PATH} ({len(records_json)} records)")

    # ---- Parquet ------------------------------------------------------------
    parquet_path = os.path.join(DOCS_DIR, "history.parquet")
    import pandas as pd
    df = pd.DataFrame(records_json)
    df.to_parquet(parquet_path, index=False)
    print(f"[scraper] Parquet updated → {parquet_path} ({len(df)} records)")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[scraper] Starting at {timestamp}")

    html = fetch_page()
    metrics = parse_metrics(html)

    new_record = {"timestamp": timestamp, **metrics}
    print(f"[scraper] Parsed record: {new_record}")

    update_history(new_record)
    print("[scraper] Done.")


if __name__ == "__main__":
    main()
