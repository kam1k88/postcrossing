"""
build_dashboard.py — Reads docs/history.csv and generates docs/index.html
with an improved dark-themed interactive Plotly dashboard for all 7 metrics.
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
    ("members",             "Members",                  "#4FC3F7", "👥"),
    ("countries",           "Countries",                "#81C784", "🌍"),
    ("postcards_received",  "Postcards Received",       "#FFB74D", "📬"),
    ("received_last_hour",  "Received Last Hour",       "#F06292", "⏱️"),
    ("postcards_traveling", "Postcards Traveling",      "#CE93D8", "✈️"),
    ("km_traveled",         "KM Traveled",              "#4DB6AC", "🗺️"),
    ("laps_around_world",   "Laps Around the World",    "#FFF176", "🌐"),
]

PLOTLY_CDN = "https://cdn.plot.ly/plotly-2.32.0.min.js"

CHART_BG   = "#1E2130"
PAPER_BG   = "#1E2130"
GRID_COLOR = "#2D3250"
FONT_COLOR = "#E0E0E0"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_number(val) -> str:
    """Format a number with thousands separators, return '—' if missing."""
    try:
        f = float(val)
        if f == int(f):
            return f"{int(f):,}"
        return f"{f:,.2f}"
    except (TypeError, ValueError):
        return "—"


def build_chart_html(df: pd.DataFrame, col: str, title: str, color: str) -> str:
    """Return Plotly chart HTML (no full page wrapper, no CDN re-include)."""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df[col],
        mode="lines+markers",
        name=title,
        line=dict(color=color, width=2.5, shape="spline"),
        marker=dict(size=5, color=color, line=dict(width=1, color=CHART_BG)),
        fill="tozeroy",
        fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba") if "rgb" in color
                   else color + "14",  # hex alpha
    ))

    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=FONT_COLOR, family="Inter, Segoe UI, sans-serif"),
        title=dict(text=title, font=dict(size=16, color=color), x=0.02),
        xaxis=dict(
            title="",
            showgrid=True, gridcolor=GRID_COLOR, gridwidth=1,
            showline=False, zeroline=False,
            tickfont=dict(size=11, color="#9E9E9E"),
        ),
        yaxis=dict(
            title="",
            showgrid=True, gridcolor=GRID_COLOR, gridwidth=1,
            showline=False, zeroline=False,
            tickfont=dict(size=11, color="#9E9E9E"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#2D3250",
            bordercolor=color,
            font=dict(color="#FFFFFF", size=12),
        ),
        height=300,
        margin=dict(l=50, r=20, t=50, b=40),
        showlegend=False,
    )

    return fig.to_html(full_html=False, include_plotlyjs=False,
                       div_id=f"chart_{col}", config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Stat cards
# ---------------------------------------------------------------------------

def build_stat_cards(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    last = df.iloc[-1]
    cards = ""
    for col, title, color, icon in METRICS:
        val = fmt_number(last.get(col))
        cards += f"""
        <div class="stat-card">
          <div class="stat-icon">{icon}</div>
          <div class="stat-value" style="color:{color}">{val}</div>
          <div class="stat-label">{title}</div>
        </div>"""
    return cards


# ---------------------------------------------------------------------------
# Page assembly
# ---------------------------------------------------------------------------

def generate_dashboard(df: pd.DataFrame) -> str:
    total_records = len(df)
    last_updated = "No data yet"
    if total_records > 0:
        try:
            ts = str(df["timestamp"].iloc[-1]).replace("Z", "+00:00")
            last_updated = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M UTC")
        except (ValueError, AttributeError):
            last_updated = str(df["timestamp"].iloc[-1])

    stat_cards_html = build_stat_cards(df)

    charts_html = ""
    for col, title, color, icon in METRICS:
        if col not in df.columns:
            continue
        chart_df = df[["timestamp", col]].dropna(subset=[col]).copy()
        if chart_df.empty:
            charts_html += f'<div class="no-data">{icon} No data yet for: {title}</div>\n'
            continue
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")
        charts_html += f'<div class="chart-card">{build_chart_html(chart_df, col, title, color)}</div>\n'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Postcrossing Stats Dashboard</title>
  <script src="{PLOTLY_CDN}"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: #12141F;
      color: #E0E0E0;
      font-family: 'Inter', 'Segoe UI', sans-serif;
      min-height: 100vh;
    }}

    /* ── Header ── */
    header {{
      background: linear-gradient(135deg, #1a1d2e 0%, #12141F 100%);
      border-bottom: 1px solid #2D3250;
      padding: 2rem 2rem 1.6rem;
      text-align: center;
    }}
    header .logo {{
      font-size: 2rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      color: #fff;
    }}
    header .logo span {{ color: #F06292; }}
    header p {{
      margin-top: 0.4rem;
      color: #9E9E9E;
      font-size: 0.9rem;
    }}
    header .badge {{
      display: inline-block;
      margin-top: 0.8rem;
      background: #2D3250;
      border: 1px solid #3D4470;
      border-radius: 20px;
      padding: 0.25rem 0.9rem;
      font-size: 0.78rem;
      color: #B0BEC5;
    }}
    header .badge span {{ color: #4FC3F7; font-weight: 600; }}

    /* ── Layout ── */
    main {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 2rem 1.5rem 4rem;
    }}

    /* ── Stat cards ── */
    .stats-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
      margin-bottom: 2.5rem;
    }}
    .stat-card {{
      background: #1E2130;
      border: 1px solid #2D3250;
      border-radius: 12px;
      padding: 1.2rem 1rem;
      text-align: center;
      transition: transform 0.15s, border-color 0.15s;
    }}
    .stat-card:hover {{
      transform: translateY(-2px);
      border-color: #4D5580;
    }}
    .stat-icon {{ font-size: 1.6rem; margin-bottom: 0.5rem; }}
    .stat-value {{ font-size: 1.35rem; font-weight: 700; line-height: 1.2; }}
    .stat-label {{
      margin-top: 0.35rem;
      font-size: 0.72rem;
      color: #9E9E9E;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }}

    /* ── Section title ── */
    .section-title {{
      font-size: 0.78rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #9E9E9E;
      margin-bottom: 1rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .section-title::after {{
      content: '';
      flex: 1;
      height: 1px;
      background: #2D3250;
    }}

    /* ── Chart cards ── */
    .chart-card {{
      background: #1E2130;
      border: 1px solid #2D3250;
      border-radius: 12px;
      padding: 0.75rem 0.5rem 0.25rem;
      margin-bottom: 1.25rem;
      overflow: hidden;
    }}
    .no-data {{
      background: #1E2130;
      border: 1px dashed #2D3250;
      border-radius: 12px;
      padding: 2rem;
      text-align: center;
      color: #9E9E9E;
      margin-bottom: 1.25rem;
    }}

    /* ── Download bar ── */
    .download-bar {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
      margin-bottom: 2rem;
    }}
    .download-bar .label {{
      font-size: 0.8rem;
      color: #9E9E9E;
      font-weight: 500;
    }}
    .download-bar a {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      background: #2D3250;
      color: #E0E0E0;
      text-decoration: none;
      border: 1px solid #3D4470;
      border-radius: 8px;
      padding: 0.4rem 0.9rem;
      font-size: 0.82rem;
      font-weight: 500;
      transition: background 0.15s, border-color 0.15s;
    }}
    .download-bar a:hover {{ background: #3D4470; border-color: #5D6AA0; }}

    /* ── Footer ── */
    footer {{
      margin-top: 3rem;
      border-top: 1px solid #2D3250;
      padding-top: 1.2rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 0.5rem;
      font-size: 0.8rem;
      color: #9E9E9E;
    }}
    footer strong {{ color: #B0BEC5; }}
    footer a {{ color: #4FC3F7; text-decoration: none; }}
    footer a:hover {{ text-decoration: underline; }}

    @media (max-width: 600px) {{
      .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
      header .logo {{ font-size: 1.5rem; }}
    }}
  </style>
</head>
<body>

<header>
  <div class="logo">📬 Post<span>crossing</span> Stats</div>
  <p>Live metrics collected automatically every hour from postcrossing.com</p>
  <div class="badge">
    Last updated: <span>{last_updated}</span> &nbsp;·&nbsp; <span>{total_records}</span> records collected
  </div>
</header>

<main>

  <!-- Stat cards -->
  <div class="section-title">Current Values</div>
  <div class="stats-grid">
    {stat_cards_html}
  </div>

  <!-- Download -->
  <div class="download-bar">
    <span class="label">Download data:</span>
    <a href="history.csv" download>⬇ history.csv</a>
    <a href="history.json" download>⬇ history.json</a>
  </div>

  <!-- Charts -->
  <div class="section-title">Historical Trends</div>
  {charts_html}

  <footer>
    <div>
      <strong>Last updated:</strong> {last_updated} &nbsp;·&nbsp;
      <strong>Records:</strong> {total_records}
    </div>
    <div>
      Data auto-collected via GitHub Actions ·
      <a href="https://www.postcrossing.com/" target="_blank" rel="noopener">postcrossing.com</a>
    </div>
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
        print("[dashboard] history.csv not found — creating placeholder page.")
        df = pd.DataFrame(columns=["timestamp"] + [col for col, *_ in METRICS])
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
