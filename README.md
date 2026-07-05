# 📬 Postcrossing Statistics Dashboard

An autonomous project that collects and visualises live statistics from [postcrossing.com](https://www.postcrossing.com/) — powered by GitHub Actions and published via GitHub Pages for free.

---

## What it does

Twice daily (06:00 UTC and 18:00 UTC) a GitHub Actions workflow:
1. Parses 7 key metrics from the Postcrossing homepage.
2. Appends the new record to `docs/history.csv` and `docs/history.json`.
3. Updates `docs/TimeData.csv` from the live Postcrossing site.
4. **Automatically uploads `TimeData.csv` to Hugging Face** dataset: [kamjke/postcrossing-daily-growth](https://huggingface.co/datasets/kamjke/postcrossing-daily-growth)
5. Regenerates `docs/index.html` — an interactive Plotly dashboard.
6. Commits and pushes the updated files to the `main` branch.

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

- **`docs/TimeData.csv`** — Time series data of postcards received (updated twice daily).
  Also available on [🤗 Hugging Face](https://huggingface.co/datasets/kamjke/postcrossing-daily-growth/raw/main/TimeData.csv)

  ```
  datetime,postcards_received
  2019-09-01 23:15:00,53518665
  2026-07-05 16:38:16,87351335
  ```

---

## Requirements

- Python **3.12**
- Dependencies (see `requirements.txt`):
  - `requests` — HTTP requests
  - `beautifulsoup4` — HTML parsing
  - `pandas` — CSV/DataFrame handling
  - `plotly` — Interactive charts
  - `pyarrow` — Parquet file support
  - `fake-useragent` — User-Agent generation
  - `huggingface_hub` — Upload to Hugging Face datasets

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

### 6. Set up Hugging Face integration (optional)

To enable automatic uploads to Hugging Face:

1. Create a Hugging Face account at https://huggingface.co/
2. Create a new dataset: https://huggingface.co/new-dataset
3. Generate a write token: https://huggingface.co/settings/tokens
4. Add the token to GitHub Secrets:
   - Go to **Settings** → **Secrets and variables** → **Actions**
   - Click **New repository secret**
   - Name: `HF_TOKEN`
   - Value: your Hugging Face token
5. Update `upload_to_hf.py` with your dataset name

**Verification:** Run `python verify_sync.py` to check if GitHub and Hugging Face datasets are in sync.

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
python scraper.py            # Fetches and saves a new record
python update_timedata.py    # Updates TimeData.csv from live site
python build_dashboard.py    # Rebuilds docs/index.html
python verify_sync.py        # Verifies sync with Hugging Face
open docs/index.html         # View the dashboard in your browser
```

---

## Repository Structure

```
.
├── scraper.py               # Fetches metrics and updates history files
├── build_dashboard.py       # Generates the interactive HTML dashboard
├── update_timedata.py       # Updates TimeData.csv from live site
├── upload_to_hf.py          # Uploads TimeData.csv to Hugging Face
├── verify_sync.py           # Verifies GitHub ↔ Hugging Face sync
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── SYNC_STATUS.md           # Latest sync status report
├── .github/
│   └── workflows/
│       └── scrape.yml       # GitHub Actions workflow (twice daily + manual)
└── docs/                    # Published via GitHub Pages
    ├── index.html           # Interactive dashboard (auto-generated)
    ├── history.csv          # Full metric history in CSV format
    ├── history.json         # Full metric history in JSON format
    ├── history.parquet      # Full metric history in Parquet format
    └── TimeData.csv         # Time series (synced with Hugging Face)
```

---

## External Links

- 📊 **Live Dashboard:** https://kam1k88.github.io/postcrossing/
- 🤗 **Hugging Face Dataset:** https://huggingface.co/datasets/kamjke/postcrossing-daily-growth
- 📦 **Direct CSV Download:** https://huggingface.co/datasets/kamjke/postcrossing-daily-growth/raw/main/TimeData.csv
- 🔄 **Sync Status:** See [SYNC_STATUS.md](SYNC_STATUS.md)

---

## License

MIT — do whatever you like with it.
