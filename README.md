# PetroDCA

PetroDCA is a Streamlit application for petroleum production analysis, decline curve analysis, EUR forecasting, field insights, and report export.

## Project Structure

- `app.py` - Main Streamlit application.
- `requirements.txt` - Python dependencies required to run the app.
- `.venv/` - Local virtual environment created for this project.
- `AI_INTERACTION_LOG.md` - Record of how AI support was used during setup, debugging, and architecture documentation.

## Setup

From the `kwame2` folder:

```powershell
.\.venv\Scripts\activate
```

The environment has already been created with Python 3.14.4 and dependencies installed from `requirements.txt`.

To reinstall dependencies later:

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

## Main Features

- Upload and parse production data from CSV or Excel files.
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

