# PetroDCA

PetroDCA is a Streamlit application for petroleum production analysis, decline curve analysis, EUR forecasting, field insights, and report export.

## Project Structure

- `app.py` - Main Streamlit application.
- `requirements.txt` - Python dependencies required to run the app.
- `AI_INTERACTION_LOG.md` - Record of how AI support was used during setup, debugging, and feature updates.
- `Field Data/` - Optional local production data files.
- `.venv/` - Local virtual environment for this project.

## Setup

From the `kwame2` folder:

```powershell
.\.venv\Scripts\activate
```

To install or refresh dependencies with `uv`:

```powershell
uv pip install -r requirements.txt
```

If you are not using `uv`, install with pip after activating the environment:

```powershell
python -m pip install -r requirements.txt
```

## Run the App

```powershell
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Data Sources

PetroDCA can load production data from:

- Local Excel files (`.xlsx`, `.xls`) with one worksheet per well.
- Local CSV files with columns such as `date`, `oil`, `gas`, `water`, and optionally `well`.
- Public Google Sheets URLs.

For Google Sheets:

- Paste one spreadsheet URL to load all visible worksheet tabs.
- Paste multiple Google Sheets URLs on separate lines to combine them.
- Enable **Real-Time Sync every 3s** to refresh Google Sheet data automatically.
- Local uploads and Google Sheet data are kept as separate sources internally, then merged into one combined dataset for analysis.
- If the same well exists in local and Google Sheet data, rows are merged by date, with synced Google Sheet rows taking precedence on duplicate dates.
A Google-sheet link to use for illustration is given below;
[Google_sheet link](https://docs.google.com/spreadsheets/d/16owoXpOY7s2koGbrdhdtAqSwoANYk2l4FBID-t6XPJ8/edit?gid=1854687645#gid=1854687645) 

## Well Selection

After loading data, use **Wells to Include** in the sidebar to choose which wells are included in dashboards, DCA, EUR forecasting, insights, and reports.

The filter is non-destructive: hidden wells remain loaded and can be reselected later. New wells introduced by a later upload or Google Sheet sync are automatically included.

## Main Features

- Upload and parse production data from CSV, Excel, or public Google Sheets.
- Cross-examine multiple worksheets and multiple well sources in one combined analysis.
- Convert oil, gas, and water production rates into field units.
- Fit Arps decline models using SciPy.
- Compare exponential, harmonic, and hyperbolic decline behavior.
- Estimate EUR and remaining recoverable volumes.
- Visualize production trends, DCA results, and field-level insights with Plotly.
- Export production and DCA results to CSV or Excel.
- Use the in-app AI advisor page for deterministic, rule-based guidance on decline rates, EUR, model fit, water trends, and forecast quality.

## Dependencies

Core packages include:

- Streamlit
- pandas
- NumPy
- SciPy
- Plotly
- openpyxl
- xlsxwriter
- xlrd

Standard-library modules are also used for Google Sheets URL parsing and workbook downloads.
