# AI Interaction Log

This file documents how AI assistance was used to set up, debug, describe, and update the PetroDCA application. It is intended to make the development process transparent and reproducible.

## Session Dates

- May 17, 2026
- May 19, 2026

## Summary

AI assistance was used to inspect the project, create a local virtual environment, install dependencies, identify setup blockers, update data-loading behavior, and maintain project documentation.

The app's numerical calculations remain deterministic Python logic using pandas, NumPy, SciPy, and Plotly. The in-app AI advisor is rule-based and advisory only; it does not call an external AI model or replace the decline curve calculations.

## Interactions

| Date | Area | Issue or Goal | AI Contribution | Result |
| --- | --- | --- | --- | --- |
| 2026-05-17 | Environment setup | Create a virtual environment inside the project workspace. | Inspected the repository structure, located `requirements.txt`, and created `.venv` inside `kwame2`. | A local Python virtual environment exists at `.venv/`. |
| 2026-05-17 | Dependency installation | Install all packages from `requirements.txt`. | Used `uv pip install -r requirements.txt` after creating the venv. | Streamlit, pandas, NumPy, SciPy, Plotly, Excel libraries, and transitive dependencies were installed. |
| 2026-05-17 | Python launcher issue | `python` and `py` commands pointed to inaccessible Microsoft Store aliases. | Diagnosed the launcher issue and used a managed Python interpreter through `uv`. | Python commands for project checks were run through `uv`. |
| 2026-05-17 | Cache permissions issue | `uv` could not initialize its default cache under `AppData`. | Redirected `UV_CACHE_DIR` to a local project cache folder when needed. | Dependency tooling and compile checks worked without relying on the blocked cache path. |
| 2026-05-17 | Network install restriction | Package download attempts initially failed because network access was blocked. | Retried the install with explicit approval for network access. | Dependencies were successfully resolved and installed. |
| 2026-05-17 | App architecture documentation | Explain the purpose and major modules of the Streamlit app. | Reviewed `app.py` and summarized data loading, decline curve fitting, EUR forecasting, visualization, export, and AI advisor features. | Added project documentation in `README.md`. |
| 2026-05-17 | AI advisor architecture | Clarify how AI-like guidance is used inside the app. | Identified that the in-app advisor is rule-based and responds to keywords such as decline rate, EUR, model fit, water, and R2. | Documented that the advisor is advisory only and does not replace deterministic calculations. |
| 2026-05-19 | Google Sheets loading | Allow URL-based loading across multiple worksheets. | Added direct Google Sheets XLSX export loading, with CSV fallback for individual tabs. | One public Google Sheets URL can load all visible worksheet tabs; multiple URLs can be pasted and combined. |
| 2026-05-19 | Cross-source merging | Merge local upload data with Google Sheet URL data without sync interference. | Split loaded data into local and Google Sheet buckets, then rebuilt a combined `wells` dataset from both. | Local uploads are preserved while 3-second Google Sheet sync refreshes only the Google Sheet bucket. |
| 2026-05-19 | Duplicate well handling | Support same well names across local and Google Sheet sources. | Added date-based merge behavior for wells with matching names. | Duplicate dates are resolved with Google Sheet rows taking precedence after sync. |
| 2026-05-19 | Real-time sync | Remove manual interval choices and make sync faster. | Replaced the 15s/30s/1m/5m/15m selector with a fixed 3-second sync interval. | Real-Time Sync now refreshes Google Sheet data every 3 seconds. |
| 2026-05-19 | Well inclusion filter | Let the user choose which wells participate in analysis. | Added a sidebar **Wells to Include** multiselect with Select All and Clear actions. | Selected wells drive dashboards, DCA, EUR, insights, and reports while unselected wells remain loaded. |
| 2026-05-19 | Verification | Confirm edited Python remains syntactically valid. | Ran `uv run python -m py_compile kwame2/app.py` with a local `UV_CACHE_DIR`. | `app.py` passed syntax compilation after the updates. |
| 2026-05-19 | Documentation refresh | Bring docs and dependency notes up to date. | Updated `README.md`, `requirements.txt`, and this interaction log. | Project documentation now reflects current data source, sync, merge, and filter behavior. |

## Notes on AI Use

- AI was used as a development assistant for setup, documentation, troubleshooting, and scoped code changes.
- AI did not replace the app's mathematical formulas or production forecasting logic.
- Decline curve calculations are performed by deterministic functions in `app.py`, especially the Arps model fitting and EUR estimation routines.
- Human review is still required for petroleum engineering assumptions, input data quality, and business decisions based on forecast outputs.
- Public Google Sheets must be accessible to the app environment for URL loading and real-time sync to work.
