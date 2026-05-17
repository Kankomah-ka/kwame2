# AI Interaction Log

This file documents how AI assistance was used to set up, debug, and describe the PetroDCA application. It is intended to make the development process transparent and reproducible.

## Session Date

May 17, 2026

## Summary

AI assistance was used to inspect the project, create a local virtual environment, install dependencies, identify setup blockers, and produce project documentation. The app's numerical calculations remain deterministic Python logic using pandas, NumPy, SciPy, and Plotly.

## Interactions

| Area | Issue or Goal | AI Contribution | Result |
| --- | --- | --- | --- |
| Environment setup | Create a virtual environment inside the project workspace. | Inspected the repository structure, located `requirements.txt`, and created `.venv` inside `kwame2`. | A local Python virtual environment now exists at `.venv/`. |
| Dependency installation | Install all packages from `requirements.txt`. | Used `uv pip install -r requirements.txt` after creating the venv. | Streamlit, pandas, NumPy, SciPy, Plotly, Excel libraries, and transitive dependencies were installed. |
| Python launcher bug | `python` and `py` commands pointed to inaccessible Microsoft Store aliases. | Diagnosed the launcher issue and found a usable managed Python interpreter through `uv`. | The venv was created with CPython 3.14.4. |
| Cache permissions bug | `uv` could not initialize its default cache under `AppData`. | Redirected `UV_CACHE_DIR` to a local project cache folder. | Dependency tooling worked without relying on the blocked cache path. |
| Network install restriction | Package download attempts initially failed because network access was blocked. | Retried the install with explicit approval for network access. | Dependencies were successfully resolved and installed. |
| App architecture documentation | Explain the purpose and major modules of the Streamlit app. | Reviewed `app.py` and summarized its production data loading, decline curve fitting, EUR forecasting, visualization, export, and AI advisor features. | Added `README.md` with setup, run instructions, and feature overview. |
| AI advisor architecture | Clarify how AI-like guidance is used inside the app. | Identified that the in-app advisor is rule-based and responds to keywords such as decline rate, EUR, model fit, water, and R2. | Documented that the advisor is advisory only and does not replace deterministic calculations. |

## Notes on AI Use

- AI was used as a development assistant for setup, documentation, and troubleshooting.
- AI did not change the app's mathematical formulas or production forecasting logic in this session.
- The decline curve calculations are performed by deterministic functions in `app.py`, especially the Arps model fitting and EUR estimation routines.
- Human review is still required for petroleum engineering assumptions, input data quality, and business decisions based on forecast outputs.

