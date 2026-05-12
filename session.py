import streamlit as st
from .dca_models import calculate_eur, fit_arps_models, best_model
from .config import SM3_TO_BBL


def _init_state():
    defaults = dict(
        wells={},
        selected=[],
        dca_results={},
        eur_results={},
        data_uploaded=False,
        theme="Dark",
        settings=dict(
            econ_limit=50.0,
            horizon=10,
            phase="Oil_bbl",
            smooth=True,
            auto_model=True,
            model="Hyperbolic",
            available_models={"Exponential": True, "Harmonic": True, "Hyperbolic": True},
        ),
        ai_log=[],
        page="Dashboard Overview",
        field_name="Field",
    )
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _run_dca_all():
    available_models = st.session_state.settings.get(
        "available_models", {"Exponential": True, "Harmonic": True, "Hyperbolic": True}
    )
    for well in st.session_state.selected:
        df = st.session_state.wells.get(well)
        if df is None:
            continue
        phase = st.session_state.settings["phase"]
        res = fit_arps_models(df, phase=phase)
        if available_models:
            res = {m: r for m, r in res.items() if available_models.get(m, True)}
        st.session_state.dca_results[well] = res
        if not res:
            continue
        bm = best_model(res)
        r = res[bm]
        eu = calculate_eur(
            qi=r["qi"], Di_day=r["Di_day"], b=r["b"], model=bm,
            econ_limit_bbl=st.session_state.settings["econ_limit"] * SM3_TO_BBL,
            horizon_years=st.session_state.settings["horizon"],
            peak_date=r["peak_date"],
            cum_to_date_bbl=float(df[phase].sum()),
        )
        st.session_state.eur_results[well] = dict(
            model=bm,
            **eu,
            **{k: r[k] for k in ("qi", "Di_year", "b", "r2", "rmse", "AIC")}
        )
