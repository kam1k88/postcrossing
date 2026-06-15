# 📬 Postcrossing Statistics Dashboard

An autonomous project that collects and visualises live statistics from [postcrossing.com](https://www.postcrossing.com/) — powered by GitHub Actions and published via GitHub Pages for free.

---

## What it does

Every hour a GitHub Actions workflow:
1. Parses 7 key metrics from the Postcrossing homepage.
2. Appends the new record to `docs/history.csv` and `docs/history.json`.
3. Regenerates `docs/index.html` — an interactive Plotly dashboard.
4. Commits and pushes the updated files to the `main` branch.

---

## Collected Metrics

| Column | Description |
|---|---|
| `members` | Total registered members |
| `countries` | Number of participating countries |
| `postcards_received` | Total postcards received all-time |
| `received_last_hour` | Postcards received in the last hour |
| `postcards_traveling` | Postcards currently in transit |
| `km_traveled` | Total kilometres travelled by postcards |
| `laps_around_world` | Equivalent laps around the Earth |

---

## Data Formats

- **`docs/history.csv`** — A standard comma-separated file with a header row.
  Each subsequent row is one hourly record.

  ```
  timestamp,members,countries,postcards_received,received_last_hour,...
  2024-06-01T12:00:00Z,900000,214,250000000,1234,...
  ```

- **`docs/history.json`** — A JSON array of objects, one per record.

  ```json
  [
    {
      "timestamp": "2024-06-01T12:00:00Z",
      "members": 900000,
      ...
    }
  ]
  ```

---

## Requirements

- Python **3.12**
- Dependencies (see `requirements.txt`):
  - `requests` — HTTP requests
  - `beautifulsoup4` — HTML parsing
  - `pandas` — CSV/DataFrame handling
  - `plotly` — Interactive charts

---

## Setup

### 1. Fork / clone this repository

```bash
git clone https://github.com/kam1k88/postcrossing.git
cd postcrossing
```

### 2. Push to GitHub

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 4. Enable GitHub Pages

1. Go to your repository on GitHub.
2. Click **Settings** → **Pages** (in the left sidebar).
3. Under **Source**, select:
   - Branch: `main`
   - Folder: `/docs`
4. Click **Save**.

After the next workflow run (or a manual trigger), your dashboard will be live at:

```
https://kam1k88.github.io/postcrossing/
```

### 5. Grant Actions write permission (if needed)

1. Go to **Settings** → **Actions** → **General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Click **Save**.

---

## Triggering a Manual Run

1. Go to the **Actions** tab in your repository.
2. Click **Scrape Postcrossing & Deploy Dashboard** in the workflow list.
3. Click **Run workflow** → **Run workflow** (green button).

The workflow will execute immediately and push updated data and dashboard files.

---

## Running Locally

```bash
pip install -r requirements.txt
python scraper.py        # Fetches and saves a new record
python build_dashboard.py  # Rebuilds docs/index.html
open docs/index.html     # View the dashboard in your browser
```

---

## Repository Structure

```
.
├── scraper.py               # Fetches metrics and updates history files
├── build_dashboard.py       # Generates the interactive HTML dashboard
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── .github/
│   └── workflows/
│       └── scrape.yml       # GitHub Actions workflow (hourly + manual)
└── docs/                    # Published via GitHub Pages
    ├── index.html           # Interactive dashboard (auto-generated)
    ├── history.csv          # Full metric history in CSV format
    └── history.json         # Full metric history in JSON format
```

---

## License

MIT — do whatever you like with it.
