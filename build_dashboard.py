"""
build_dashboard.py — Reads docs/history.csv and generates docs/index.html
with interactive Plotly charts for all 7 Postcrossing metrics.
"""

import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
CSV_PATH = os.path.join(DOCS_DIR, "history.csv")
OUTPUT_PATH = os.path.join(DOCS_DIR, "index.html")

METRICS = [
    ("members",            "Members"),
    ("countries",          "Countries"),
    ("postcards_received", "Postcards Received"),
    ("received_last_hour", "Received in the Last Hour"),
    ("postcards_traveling","Postcards Traveling"),
    ("km_traveled",        "KM Traveled"),
    ("laps_around_world",  "Laps Around the World"),
]

PLOTLY_CDN = (
    "https://cdn.plot.ly/plotly-2.32.0.min.js"
)

# ---------------------------------------------------------------------------
# Chart building
# ---------------------------------------------------------------------------

def build_chart_html(df: pd.DataFrame, col: str, title: str) -> str:
    """Return the HTML <div> + inline script for one Plotly chart."""
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=df[col],
            mode="lines+markers",
            name=title,
            line=dict(width=2),
            marker=dict(size=4),
        )
    )

    fig.update_layout(
        title=dict(text=title, font=dict(size=18)),
        xaxis_title="Timestamp (UTC)",
        yaxis_title=title,
        hovermode="x unified",
        height=380,
        margin=dict(l=60, r=30, t=60, b=60),
        template="plotly_white",
        xaxis=dict(showgrid=True, gridcolor="#e5e5e5"),
        yaxis=dict(showgrid=True, gridcolor="#e5e5e5"),
    )

    # include_plotlyjs=False because we load the CDN once in the page header
    return fig.to_html(full_html=False, include_plotlyjs=False, div_id=f"chart_{col}")


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def generate_dashboard(df: pd.DataFrame) -> str:
    """Build and return the complete HTML string."""

    # Meta info
    total_records = len(df)
    last_updated_raw = df["timestamp"].iloc[-1] if total_records > 0 else "N/A"
    # Pretty-print the timestamp if possible
    try:
        last_updated = datetime.fromisoformat(
            str(last_updated_raw).replace("Z", "+00:00")
        ).strftime("%Y-%m-%d %H:%M UTC")
    except (ValueError, AttributeError):
        last_updated = str(last_updated_raw)

    # Build chart HTML for each metric
    charts_html = ""
    for col, title in METRICS:
        if col not in df.columns:
            continue
        chart_df = df[["timestamp", col]].dropna(subset=[col]).copy()
        if chart_df.empty:
            charts_html += f'<p class="no-data">No data yet for: {title}</p>\n'
            continue
        # Ensure numeric type
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")
        charts_html += f'<div class="chart-wrapper">\n'
        charts_html += build_chart_html(chart_df, col, title)
        charts_html += "\n</div>\n"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Postcrossing Statistics Dashboard</title>
  <script src="{PLOTLY_CDN}"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{
      font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
      background: #f7f8fc;
      color: #333;
      margin: 0;
      padding: 0;
    }}
    header {{
      background: linear-gradient(135deg, #e83e3e 0%, #c0392b 100%);
      color: #fff;
      padding: 2rem 1.5rem 1.5rem;
      text-align: center;
    }}
    header h1 {{
      margin: 0 0 0.4rem;
      font-size: 2rem;
      letter-spacing: 0.03em;
    }}
    header p {{
      margin: 0;
      opacity: 0.85;
      font-size: 0.95rem;
    }}
    main {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 1.5rem 1rem 3rem;
    }}
    .chart-wrapper {{
      background: #fff;
      border-radius: 10px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
      margin-bottom: 1.8rem;
      padding: 0.5rem 0.5rem 0;
      overflow: hidden;
    }}
    .no-data {{
      background: #fff;
      border-radius: 10px;
      padding: 1.5rem;
      color: #999;
      text-align: center;
      margin-bottom: 1.8rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }}
    .download-bar {{
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 2rem;
      align-items: center;
    }}
    .download-bar span {{
      font-weight: 600;
      color: #555;
    }}
    .download-bar a {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      background: #e83e3e;
      color: #fff;
      text-decoration: none;
      border-radius: 6px;
      padding: 0.45rem 1rem;
      font-size: 0.88rem;
      font-weight: 600;
      transition: background 0.2s;
    }}
    .download-bar a:hover {{ background: #c0392b; }}
    footer {{
      margin-top: 3rem;
      border-top: 1px solid #e0e0e0;
      padding-top: 1rem;
      font-size: 0.83rem;
      color: #888;
      text-align: center;
    }}
    footer strong {{ color: #555; }}
  </style>
</head>
<body>
  <header>
    <h1>📬 Postcrossing Statistics Dashboard</h1>
    <p>Live metrics collected automatically every hour from postcrossing.com</p>
  </header>

  <main>
    <div class="download-bar">
      <span>Download data:</span>
      <a href="history.csv" download>⬇ history.csv</a>
      <a href="history.json" download>⬇ history.json</a>
    </div>

    {charts_html}

    <footer>
      <p>
        <strong>Last updated:</strong> {last_updated} &nbsp;|&nbsp;
        <strong>Total records:</strong> {total_records}
      </p>
      <p>Data collected automatically via GitHub Actions · Hosted on GitHub Pages</p>
    </footer>
  </main>
</body>
</html>
"""
    return html


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"[dashboard] Reading {CSV_PATH}")

    if not os.path.exists(CSV_PATH):
        print("[dashboard] history.csv not found — creating empty placeholder page.")
        df = pd.DataFrame(columns=["timestamp"] + [col for col, _ in METRICS])
    else:
        df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
        print(f"[dashboard] Loaded {len(df)} records.")

    html = generate_dashboard(df)

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"[dashboard] Dashboard written → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
