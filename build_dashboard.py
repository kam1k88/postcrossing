"""
build_dashboard.py — Reads docs/history.csv and generates docs/index.html
with an improved dark-themed interactive Plotly dashboard for all 7 metrics,
plus a daily received-growth chart from docs/received_report.csv.
"""

import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
CSV_PATH      = os.path.join(DOCS_DIR, "history.csv")
REPORT_PATH   = os.path.join(DOCS_DIR, "TimeData.csv")
OUTPUT_PATH   = os.path.join(DOCS_DIR, "index.html")

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
    if val is None or (isinstance(val, float) and (val != val)):  # NaN check
        return "—"
    try:
        # Try int first to avoid float precision loss on large numbers
        f = float(val)
        if f != f:  # NaN
            return "—"
        i = int(f)
        if abs(f - i) < 0.5:
            return f"{i:,}"
        return f"{f:,.2f}"
    except (TypeError, ValueError):
        return "—"


def hex_to_rgba(hex_color: str, alpha: float = 0.1) -> str:
    """Convert a #RRGGBB hex color to rgba(r,g,b,alpha) string."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


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
        fillcolor=hex_to_rgba(color, 0.1),
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
# Received-growth chart (with range buttons)
# ---------------------------------------------------------------------------

def build_received_chart(rdf: pd.DataFrame) -> str:
    """Build the bi-daily postcards-received chart with day/week/month buttons."""
    color = "#FFB74D"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rdf["datetime"],
        y=rdf["postcards_received"],
        mode="lines+markers",
        name="Postcards Received",
        line=dict(color=color, width=2.5, shape="spline"),
        marker=dict(size=6, color=color, line=dict(width=1, color=CHART_BG)),
        fill="tozeroy",
        fillcolor=hex_to_rgba(color, 0.1),
        hovertemplate="%{x}<br><b>%{y:,}</b><extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=FONT_COLOR, family="Inter, Segoe UI, sans-serif"),
        title=dict(
            text="📬 Postcards Received — Growth (2× daily snapshots)",
            font=dict(size=16, color=color), x=0.02
        ),
        xaxis=dict(
            title="",
            showgrid=True, gridcolor=GRID_COLOR, gridwidth=1,
            showline=False, zeroline=False,
            tickfont=dict(size=11, color="#9E9E9E"),
            rangeselector=dict(
                bgcolor="#2D3250",
                activecolor="#4D5580",
                bordercolor="#3D4470",
                borderwidth=1,
                font=dict(color="#E0E0E0", size=12),
                buttons=[
                    dict(count=1,  label="Day",   step="day",   stepmode="backward"),
                    dict(count=7,  label="Week",  step="day",   stepmode="backward"),
                    dict(count=1,  label="Month", step="month", stepmode="backward"),
                    dict(step="all", label="All"),
                ],
                x=0.0, y=1.08,
            ),
            rangeslider=dict(visible=False),
            type="date",
        ),
        yaxis=dict(
            title="",
            showgrid=True, gridcolor=GRID_COLOR, gridwidth=1,
            showline=False, zeroline=False,
            tickfont=dict(size=11, color="#9E9E9E"),
            tickformat=",d",
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#2D3250",
            bordercolor=color,
            font=dict(color="#FFFFFF", size=12),
        ),
        height=380,
        margin=dict(l=50, r=20, t=80, b=40),
        showlegend=False,
    )

    return fig.to_html(full_html=False, include_plotlyjs=False,
                       div_id="chart_received_growth",
                       config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Stat cards
# ---------------------------------------------------------------------------

def build_stat_cards(df: pd.DataFrame) -> str:
    if df.empty:
        return ""
    cards = ""
    for col, title, color, icon in METRICS:
        # Use last non-null value so a single failed scrape doesn't blank the card
        series = df[col].dropna() if col in df.columns else pd.Series([], dtype=float)
        val = fmt_number(series.iloc[-1]) if not series.empty else "—"
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

def generate_dashboard(df: pd.DataFrame, rdf: pd.DataFrame | None = None) -> str:
    total_records = len(df)
    last_updated = "No data yet"
    if total_records > 0:
        try:
            ts = str(df["timestamp"].iloc[-1]).replace("Z", "+00:00")
            last_updated = datetime.fromisoformat(ts).strftime("%Y-%m-%d %H:%M UTC")
        except (ValueError, AttributeError):
            last_updated = str(df["timestamp"].iloc[-1])

    stat_cards_html = build_stat_cards(df)

    # Only build "Received Last Hour" chart
    charts_html = ""
    received_last_hour_col = "received_last_hour"
    received_last_hour_title = "Received Last Hour"
    received_last_hour_color = "#F06292"
    received_last_hour_icon = "⏱️"
    
    if received_last_hour_col in df.columns:
        chart_df = df[["timestamp", received_last_hour_col]].dropna(subset=[received_last_hour_col]).copy()
        if not chart_df.empty:
            chart_df[received_last_hour_col] = pd.to_numeric(chart_df[received_last_hour_col], errors="coerce")
            charts_html = f'<div class="chart-card">{build_chart_html(chart_df, received_last_hour_col, received_last_hour_title, received_last_hour_color)}</div>\n'
        else:
            charts_html = f'<div class="no-data">{received_last_hour_icon} No data yet for: {received_last_hour_title}</div>\n'
    
    # Read forecast data
    forecast_html = ""
    forecast_file = os.path.join(DOCS_DIR, "forecast_results.txt")
    if os.path.exists(forecast_file):
        try:
            with open(forecast_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
                if len(lines) >= 2:
                    # Get last two lines
                    analysis_line = lines[-2]
                    forecast_line = lines[-1]
                    forecast_html = f"""
  <div class="forecast-box">
    <div class="forecast-icon">🔮</div>
    <div class="forecast-content">
      <div class="forecast-title">Прогноз достижения 88 млн открыток</div>
      <div class="forecast-analysis">{analysis_line}</div>
      <div class="forecast-prediction">{forecast_line}</div>
      <a href="https://www.kaggle.com/code/arkadymaximov/ctulhufagn2" target="_blank" class="forecast-link">
        📊 Ноутбук с анализом на Kaggle
      </a>
    </div>
  </div>
"""
        except Exception as e:
            print(f"[dashboard] Failed to load forecast: {e}")

    # Received-growth section
    received_section = ""
    if rdf is not None and not rdf.empty:
        rdf2 = rdf.copy()
        rdf2["postcards_received"] = pd.to_numeric(rdf2["postcards_received"], errors="coerce")
        rdf2 = rdf2.dropna(subset=["postcards_received", "datetime"])
        if not rdf2.empty:
            received_section = f"""
  <div class="section-title">Postcards Received — Daily Growth</div>
  <div class="download-bar" style="margin-bottom:1rem;">
    <span class="label">Download:</span>
    <a href="TimeData.csv" download class="btn-received"><span class="btn-icon">📊</span> TimeData.csv</a>
  </div>
  {forecast_html}
  <div class="chart-card">{build_received_chart(rdf2)}</div>
"""

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
      gap: 0.85rem;
      flex-wrap: nowrap;
      margin-bottom: 2rem;
    }}
    .download-bar .label {{
      font-size: 0.82rem;
      color: #9E9E9E;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      white-space: nowrap;
      margin-right: 0.25rem;
    }}
    .download-bar a {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.4rem;
      text-decoration: none;
      border-radius: 10px;
      padding: 0.6rem 1.2rem;
      font-size: 0.88rem;
      font-weight: 600;
      letter-spacing: 0.01em;
      white-space: nowrap;
      flex: 1;
      transition: transform 0.15s, box-shadow 0.15s, filter 0.15s;
      box-shadow: 0 2px 8px rgba(0,0,0,0.35);
    }}
    .download-bar a:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0,0,0,0.45);
      filter: brightness(1.12);
    }}
    .download-bar a:active {{ transform: translateY(0); }}
    .btn-csv     {{ background: linear-gradient(135deg, #1565C0, #1E88E5); color: #fff; }}
    .btn-json    {{ background: linear-gradient(135deg, #E65100, #FF7043); color: #fff; }}
    .btn-parquet {{ background: linear-gradient(135deg, #4A148C, #8E24AA); color: #fff; }}
    .btn-received {{ background: linear-gradient(135deg, #1B5E20, #43A047); color: #fff; flex: unset; }}
    .btn-icon    {{ font-size: 1rem; }}

    /* ── Forecast box ── */
    .forecast-box {{
      background: linear-gradient(135deg, #1E2845 0%, #1a1d2e 100%);
      border: 1px solid #4D5580;
      border-left: 4px solid #FFB74D;
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      display: flex;
      gap: 1.2rem;
      align-items: flex-start;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }}
    .forecast-icon {{
      font-size: 2.5rem;
      flex-shrink: 0;
      line-height: 1;
    }}
    .forecast-content {{
      flex: 1;
    }}
    .forecast-title {{
      font-size: 1.1rem;
      font-weight: 700;
      color: #FFB74D;
      margin-bottom: 0.8rem;
      letter-spacing: -0.01em;
    }}
    .forecast-analysis {{
      font-size: 0.85rem;
      color: #B0BEC5;
      margin-bottom: 0.5rem;
      line-height: 1.5;
    }}
    .forecast-prediction {{
      font-size: 0.95rem;
      color: #E0E0E0;
      font-weight: 600;
      margin-bottom: 0.8rem;
      line-height: 1.5;
    }}
    .forecast-link {{
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      color: #4FC3F7;
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 500;
      transition: color 0.15s;
    }}
    .forecast-link:hover {{
      color: #81D4FA;
      text-decoration: underline;
    }}

    @media (max-width: 600px) {{
      .forecast-box {{
        flex-direction: column;
        gap: 0.8rem;
        padding: 1.2rem;
      }}
      .forecast-icon {{
        font-size: 2rem;
      }}
      .forecast-title {{
        font-size: 1rem;
      }}
    }}

    @media (max-width: 480px) {{
      .download-bar {{ gap: 0.5rem; }}
      .download-bar .label {{ display: none; }}
      .download-bar a {{
        padding: 0.55rem 0.5rem;
        font-size: 0.78rem;
        gap: 0.25rem;
        border-radius: 8px;
      }}
      .btn-icon {{ font-size: 0.85rem; }}
    }}

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

  <!-- Download -->
  <div class="download-bar">
    <span class="label">Download:</span>
    <a href="history.csv"     download class="btn-csv"><span class="btn-icon">📄</span> CSV</a>
    <a href="history.json"    download class="btn-json"><span class="btn-icon">&#123; &#125;</span> JSON</a>
    <a href="history.parquet" download class="btn-parquet"><span class="btn-icon">🗜️</span> Parquet</a>
  </div>

  <!-- Stat cards -->
  <div class="section-title">Current Values</div>
  <div class="stats-grid">
    {stat_cards_html}
  </div>

  <!-- Charts -->
  <div class="section-title">Historical Trends</div>
  {charts_html}

  {received_section}

  <footer>
    <div>
      <strong>Last updated:</strong> {last_updated} &nbsp;·&nbsp;
      <strong>Records:</strong> {total_records}
    </div>
    <div>
      Data auto-collected via GitHub Actions ·
      <a href="https://www.postcrossing.com/" target="_blank" rel="noopener">postcrossing.com</a>
      &nbsp;·&nbsp;
      <a href="https://github.com/kam1k88/postcrossing" target="_blank" rel="noopener">⭐ GitHub Repository</a>
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
        df = pd.DataFrame(columns=["timestamp"] + [col for col, _title, _color, _icon in METRICS])
    else:
        df = pd.read_csv(CSV_PATH, parse_dates=["timestamp"])
        print(f"[dashboard] Loaded {len(df)} records.")

    # Load TimeData.csv (datetime, postcards_received) — ISO 8601 format
    rdf = None
    if os.path.exists(REPORT_PATH):
        try:
            rdf = pd.read_csv(REPORT_PATH)
            rdf["datetime"] = pd.to_datetime(rdf["datetime"], format="%Y-%m-%d %H:%M:%S", utc=True, errors="coerce")
            rdf["postcards_received"] = pd.to_numeric(rdf["postcards_received"], errors="coerce")
            rdf = rdf.dropna(subset=["datetime", "postcards_received"])
            rdf = rdf[rdf["postcards_received"] > 0]
            print(f"[dashboard] Loaded {len(rdf)} TimeData rows.")
        except Exception as e:
            print(f"[dashboard] Failed to load TimeData.csv: {e}")
            rdf = None

    html = generate_dashboard(df, rdf)

    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(html)

    print(f"[dashboard] Dashboard written → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
