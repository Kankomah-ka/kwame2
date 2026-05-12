import io
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

from .charts import (
    chart_cumulative_forecast,
    chart_decline_curve,
    chart_eur_vs_decline,
    chart_production_rates,
    chart_production_split_by_phase,
    chart_residuals,
)
from .config import WELL_COLOURS
from .dca_models import best_model, calculate_eur
from .theme import _html, get_C, _themed_fig, get_plotly_bg
from .utils import insight_item, kpi_card, result_row
from .session import _run_dca_all


def page_dashboard():
    C = get_C()
    _html('<div class="page-title">Dashboard Overview</div>')
    wells_data = st.session_state.wells
    selected = st.session_state.selected
    eur_res = st.session_state.eur_results
    smooth = st.session_state.settings["smooth"]
    if not selected:
        st.info("⬅️  Select wells in the sidebar to begin analysis.")
        return
    if any(w not in st.session_state.eur_results or not st.session_state.eur_results[w]
           for w in selected):
        with st.spinner("⚙️ Calculating EUR and decline metrics for selected wells…"):
            _run_dca_all()
        eur_res = st.session_state.eur_results

    latest_oil = latest_gas = latest_water = cum_oil = 0.0
    all_dis = []
    all_eurs = []
    for well in selected:
        df = wells_data.get(well)
        if df is None or len(df) == 0:
            continue
        last = df.iloc[-1]
        latest_oil += float(last.get("Oil_bbl", 0))
        latest_gas += float(last.get("Gas_mscf", 0))
        latest_water += float(last.get("Water_bbl", 0))
        cum_oil += float(df["Oil_bbl"].sum())
        er = eur_res.get(well, {})
        if er.get("Di_year"):
            all_dis.append(er["Di_year"])
        if er.get("eur_mmbbl"):
            all_eurs.append(er["eur_mmbbl"])
    avg_di = float(np.mean(all_dis)) if all_dis else 0.0
    est_eur = float(np.sum(all_eurs)) if all_eurs else 0.0
    cols = st.columns(6, gap="small")
    kpis = [
        ("🛢️", "Current Oil Rate", f"{latest_oil:,.0f}", "STB/day", ""),
        ("🔥", "Current Gas Rate", f"{latest_gas:,.0f}", "Mscf/day", ""),
        ("💧", "Current Water Rate", f"{latest_water:,.0f}", "STB/day", ""),
        ("⚖️", "Cumulative Oil", f"{cum_oil/1e6:.2f}", "MM STB", ""),
        ("📊", "Estimated EUR", f"{est_eur:.2f}", "MM STB", ""),
        ("📉", "Avg Decline Rate", f"{avg_di:.3f}", "1/yr", ""),
    ]
    for col, (icon, label, val, unit, delta) in zip(cols, kpis):
        with col:
            _html(kpi_card(icon, label, val, unit, delta))
    _html("<br>")

    phases = ["Oil_bbl", "Gas_mscf", "Water_bbl"]
    for i, well in enumerate(selected):
        fig = chart_production_rates(wells_data, [well], phases, smooth)
        fig.update_layout(title=dict(text=well, font=dict(size=13, color=C["heading"])),
                          height=360)
        st.plotly_chart(fig, use_container_width=True)
        if i < len(selected) - 1:
            st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    w0 = selected[0]
    df0 = wells_data[w0]
    er0 = eur_res.get(w0)
    if er0:
        st.plotly_chart(chart_cumulative_forecast(df0, er0, w0), use_container_width=True)
    else:
        cum = df0["Oil_bbl"].cumsum()
        fig = _themed_fig()
        fig.add_trace(go.Scatter(x=df0["Date"], y=cum/1e6, name="Cumulative Oil",
                                 mode="lines", line=dict(color=C["green"], width=2.5)))
        fig.update_layout(title="Cumulative Oil Production", yaxis_title="MM STB",
                          height=520, **get_plotly_bg())
        st.plotly_chart(fig, use_container_width=True)

    _html(f'<p style="font-weight:600;color:{C["heading"]};margin-bottom:8px">Latest Day Production by Phase</p>')
    phase_figs = chart_production_split_by_phase(wells_data, selected)
    for phase_name, fig in phase_figs.items():
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<br>", unsafe_allow_html=True)

    _html(f'<p style="font-weight:600;color:{C["heading"]};margin-bottom:8px">Well Performance Summary</p>')
    rows = []
    for well in selected:
        df = wells_data.get(well, pd.DataFrame())
        er = eur_res.get(well, {})
        rows.append({
            "Well": well,
            "Curr. Oil (STB/d)": f"{df['Oil_bbl'].iloc[-1]:,.0f}" if len(df) else "—",
            "Cum. Oil (MM STB)": f"{df['Oil_bbl'].sum()/1e6:.3f}" if len(df) else "—",
            "Di (1/yr)": f"{er.get('Di_year', 0):.3f}" if er else "—",
            "EUR P50 (MM STB)": f"{er.get('eur_mmbbl', 0):.2f}" if er else "—",
            "R²": f"{er.get('r2', 0):.3f}" if er else "—",
        })
    tbl = pd.DataFrame(rows)
    st.dataframe(tbl, use_container_width=True, hide_index=True,
                 height=min(200, 36 * len(rows) + 38))
    _html("<br>")
    _html(f'<p style="font-weight:600;color:{C["heading"]};margin-bottom:8px">Insights & Alerts</p>')
    insights_html = ""
    for well in selected[:3]:
        er = eur_res.get(well, {})
        di = er.get("Di_year", 0)
        if di > 0.4:
            insights_html += insight_item("⚠️", f"{well}: Decline rate {di:.3f}/yr is above field average.", "#f59e0b")
        else:
            insights_html += insight_item("✅", f"{well}: Performing within expected decline range.", C["green"])
    if latest_water > latest_oil * 0.5:
        insights_html += insight_item("ℹ️", "High water cut detected. Review water injection operations.", C["blue"])
    _html(insights_html)


def page_production_data():
    C = get_C()
    _html('<div class="page-title">Production Data</div>')
    wells_data = st.session_state.wells
    selected = st.session_state.selected
    smooth = st.session_state.settings["smooth"]
    if not selected:
        st.info("⬅️  Select wells in the sidebar.")
        return
    tabs = st.tabs(["📋 Data Table", "📈 Charts", "🔍 Data Quality"])
    with tabs[0]:
        well_sel = st.selectbox("Select Well", selected, key="prod_table_well")
        df = wells_data[well_sel].copy()
        df_disp = df[["Date", "OnStreamHrs", "Oil_bbl", "Gas_mscf", "Water_bbl"]].copy()
        df_disp.columns = ["Date", "On-Stream Hrs", "Oil (STB/d)", "Gas (Mscf/d)", "Water (STB/d)"]
        df_disp["Date"] = df_disp["Date"].dt.strftime("%Y-%m-%d")
        for c in ["Oil (STB/d)", "Gas (Mscf/d)", "Water (STB/d)"]:
            df_disp[c] = df_disp[c].map("{:,.1f}".format)
        c1, c2 = st.columns([3, 1])
        with c1:
            st.dataframe(df_disp, use_container_width=True, height=420, hide_index=True)
        with c2:
            df_raw = wells_data[well_sel]
            st.markdown("**Summary Statistics**")
            stats = {
                "Total Days": f"{len(df_raw)}",
                "Start Date": df_raw["Date"].min().strftime("%Y-%m-%d"),
                "End Date": df_raw["Date"].max().strftime("%Y-%m-%d"),
                "Peak Oil (STB/d)": f"{df_raw['Oil_bbl'].max():,.0f}",
                "Avg Oil (STB/d)": f"{df_raw['Oil_bbl'].mean():,.0f}",
                "Cum Oil (MM STB)": f"{df_raw['Oil_bbl'].sum()/1e6:.3f}",
                "Avg GOR": f"{(df_raw['Gas_mscf']/df_raw['Oil_bbl'].replace(0,np.nan)).mean():.2f}",
                "Peak Water (STB/d)": f"{df_raw['Water_bbl'].max():,.0f}",
            }
            html = "".join(result_row(k, str(v)) for k, v in stats.items())
            _html(f'<div class="panel-card">{html}</div>')
    with tabs[1]:
        st.markdown("**Production Rates Overview**")
        phases = ["Oil_bbl", "Gas_mscf", "Water_bbl"]
        fig = chart_production_rates(wells_data, selected, phases, smooth)
        st.plotly_chart(fig, use_container_width=True)
        well_sel2 = st.selectbox("Well (monthly bar)", selected, key="prod_bar_well")
        df2 = wells_data[well_sel2].copy()
        monthly = (df2.set_index("Date")[['Oil_bbl', 'Water_bbl', 'Gas_mscf']]
                   .resample('ME').mean().reset_index())
        PBG = get_plotly_bg()
        fig2 = go.Figure()
        fig2.add_bar(x=monthly["Date"], y=monthly["Oil_bbl"],
                     name="Oil (STB/d)", marker_color=C["green"])
        fig2.add_bar(x=monthly["Date"], y=monthly["Water_bbl"],
                     name="Water (STB/d)", marker_color=C["blue"])
        fig2.update_layout(title="Monthly Average Rates", barmode="group",
                           height=300, **PBG)
        st.plotly_chart(fig2, use_container_width=True)
    with tabs[2]:
        well_sel3 = st.selectbox("Well (quality check)", selected, key="qual_well")
        df3 = wells_data[well_sel3]
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Rows", f"{len(df3):,}")
        c2.metric("Missing Oil", f"{(df3['Oil_bbl']==0).sum():,}")
        c3.metric("Missing Gas", f"{(df3['Gas_mscf']==0).sum():,}")
        PBG = get_plotly_bg()
        fig3 = px.histogram(df3, x="OnStreamHrs", nbins=25,
                            title="On-Stream Hours Distribution",
                            color_discrete_sequence=[C["blue"]])
        fig3.update_layout(height=250, **PBG)
        st.plotly_chart(fig3, use_container_width=True)
        zero_mask = df3["Oil_bbl"] == 0
        if zero_mask.any():
            fig4 = _themed_fig()
            fig4.add_trace(go.Scatter(
                x=df3.loc[zero_mask, "Date"],
                y=np.ones(zero_mask.sum()),
                mode="markers",
                marker=dict(color=C["red"], size=5, symbol="x"),
                name="Shut-in / Zero Oil",
            ))
            fig4.update_layout(title="Shut-in / Zero-Rate Days", yaxis_visible=False,
                               height=150,
                               **{k:v for k,v in PBG.items() if k!="margin"},
                               margin=dict(l=20,r=20,t=40,b=20))
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.success("✅ No zero-oil-rate days detected in selected well.")


def page_dca():
    C = get_C()
    _html('<div class="page-title">Decline Curve Analysis (DCA)</div>')
    wells_data = st.session_state.wells
    selected = st.session_state.selected
    if not selected:
        st.info("⬅️  Select wells in the sidebar.")
        return
    well = st.selectbox("Select Well", selected, key="dca_well")
    if well not in st.session_state.dca_results or not st.session_state.dca_results.get(well):
        with st.spinner(f"⚙️ Fitting models for {well}…"):
            _run_dca_all()
    dca_res = st.session_state.dca_results
    eur_res = st.session_state.eur_results

    _html('<div class="panel-card">')
    st.markdown("**Input Parameters**")
    model_sel = st.selectbox("View Model", ["Hyperbolic","Exponential","Harmonic"], key="dca_model")
    st.caption("All three DCA models are fitted automatically on well selection.")
    log_scale = st.checkbox("Log Scale Y-axis", value=True, key="dca_log")
    fore_yrs = st.slider("Forecast Horizon (Years)", 5, 50, 15, key="dca_fore")
    econ_lim = st.number_input("Economic Limit (STB/day)", 1.0, 500.0,
                                value=st.session_state.settings["econ_limit"] * 6.28981,
                                step=5.0, key="dca_econ")
    if st.button("🔄 Re-fit All Models", key="dca_run", use_container_width=True):
        with st.spinner("⚙️ Re-fitting all three decline models…"):
            _run_dca_all()
        dca_res = st.session_state.dca_results
        eur_res = st.session_state.eur_results
        st.success("✅ Models re-fitted successfully!")
    _html("</div>")

    er = eur_res.get(well, {})
    dr = dca_res.get(well, {}).get(model_sel, {})
    res_w = dca_res.get(well, {})

    if res_w:
        _html("<br>")
        _html('<div class="panel-card">')
        _html(f'<div class="section-header" style="margin-bottom:12px;padding-bottom:0;border-bottom:none;font-size:1rem">All Model Fits (DCA Results)</div>')
        model_rows = []
        for model_name, model_res in res_w.items():
            model_rows.append({
                "Model": model_name,
                "qi (STB/d)": f"{model_res['qi']:,.0f}",
                "Di (1/yr)": f"{model_res['Di_year']:.4f}",
                "b": f"{model_res['b']:.3f}",
                "R²": f"{model_res['r2']:.4f}",
                "RMSE": f"{model_res['rmse']:.1f}",
                "AIC": f"{model_res['AIC']:.1f}",
            })
        model_df = pd.DataFrame(model_rows)
        st.dataframe(model_df, use_container_width=True, hide_index=True, height=160)
        _html("</div>")

    if dr:
        _html("<br>")
        _html('<div class="panel-card">')
        _html(f'<div class="section-header" style="margin-bottom:12px;padding-bottom:0;border-bottom:none;font-size:1rem">Selected Model Summary</div>')
        rows_html = "".join([
            result_row("Model", model_sel),
            result_row("qi (STB/day)", f"{dr['qi']:,.0f}"),
            result_row("Di (1/yr)", f"{dr['Di_year']:.4f}"),
            result_row("b", f"{dr['b']:.3f}"),
            result_row("R²", f"{dr['r2']:.4f}"),
            result_row("RMSE (STB/d)", f"{dr['rmse']:.1f}"),
            result_row("AIC", f"{dr['AIC']:.1f}"),
            result_row("Forecast (yrs)", f"{fore_yrs}"),
        ])
        _html(rows_html)
        _html("</div>")
        df_w = wells_data[well]
        _html("<br>")
        _html('<div class="panel-card">')
        _html(f'<div class="section-header" style="margin-bottom:12px;padding-bottom:0;border-bottom:none;font-size:1rem">Well Information</div>')
        info_html = "".join([
            result_row("Well", well),
            result_row("Field", st.session_state.field_name),
            result_row("Start Date", df_w["Date"].min().strftime("%Y-%m-%d")),
            result_row("End Date", df_w["Date"].max().strftime("%Y-%m-%d")),
            result_row("Econ. Limit", f"{econ_lim:.0f} STB/d"),
        ])
        _html(info_html)
        _html("</div>")

    df_w = wells_data.get(well, pd.DataFrame())
    res_w = dca_res.get(well, {})
    if not res_w:
        st.warning("⚠️ Decline models could not be fitted. Need ≥ 20 days and ≥ 8 months of positive oil production.")
    else:
        if dr:
            eur_fore = calculate_eur(
                qi=dr['qi'], Di_day=dr['Di_day'], b=dr['b'], model=model_sel,
                econ_limit_bbl=econ_lim, horizon_years=fore_yrs,
                peak_date=dr['peak_date'], cum_to_date_bbl=float(df_w['Oil_bbl'].sum()),
            )
        else:
            eur_fore = eur_res.get(well)
        st.session_state.eur_results[well] = dict(
            model=model_sel,
            **(eur_fore or {}),
            **{k: dr[k] for k in ("qi","Di_year","b","r2","rmse","AIC")} if dr else {}
        )
        monthly = (df_w.set_index("Date")["Oil_bbl"]
                   .resample("ME").mean().dropna().reset_index())
        monthly.columns = ["Date", "Oil_bbl"]
        if model_sel in res_w:
            fig_dc = chart_decline_curve(
                res_w, model_sel,
                actual_dates=monthly["Date"],
                actual_q=monthly["Oil_bbl"],
                log_scale=log_scale,
                forecast_years=fore_yrs,
                eur_dict=eur_fore,
            )
            st.plotly_chart(fig_dc, use_container_width=True)
            PBG = get_plotly_bg()
            model_names = list(res_w.keys())
            r2_vals = [res_w[m]["r2"] for m in model_names]
            rmse_vals = [res_w[m]["rmse"] for m in model_names]
            col_bars = [C["green"] if m == model_sel else C["muted"] for m in model_names]
            fig_cmp = make_subplots(rows=1, cols=2, subplot_titles=["R² Comparison","RMSE Comparison"])
            fig_cmp.add_trace(go.Bar(x=model_names, y=r2_vals, marker_color=col_bars, name="R²"), row=1, col=1)
            fig_cmp.add_trace(go.Bar(x=model_names, y=rmse_vals, marker_color=col_bars, name="RMSE"), row=1, col=2)
            fig_cmp.update_layout(height=200, showlegend=False,
                                  **{k:v for k,v in PBG.items() if k!="margin"},
                                  margin=dict(l=40,r=20,t=30,b=30))
            st.plotly_chart(fig_cmp, use_container_width=True)
            st.plotly_chart(chart_residuals(res_w, model_sel), use_container_width=True)
        else:
            st.warning(f"Model '{model_sel}' could not be fitted for this well.")


def page_eur():
    C = get_C()
    _html('<div class="page-title">EUR Prediction</div>')
    wells_data = st.session_state.wells
    selected = st.session_state.selected
    if not selected:
        st.info("⬅️  Select wells in the sidebar.")
        return
    if any(w not in st.session_state.dca_results or not st.session_state.dca_results.get(w)
           for w in selected):
        with st.spinner("⚙️ Fitting decline curves…"):
            _run_dca_all()
    dca_res = st.session_state.dca_results
    eur_res = st.session_state.eur_results
    analyzed_wells = [w for w in selected if w in dca_res and dca_res[w]]
    if not analyzed_wells:
        st.warning("⚠️ Decline models could not be fitted for any selected well.")
        return
    default_well = st.session_state.get("eur_well")
    if default_well not in analyzed_wells:
        default_well = analyzed_wells[0]
    well = st.selectbox("Select Well", analyzed_wells,
                          index=analyzed_wells.index(default_well), key="eur_well")
    dr_all = dca_res.get(well, {})
    df_w = wells_data.get(well, pd.DataFrame())
    if not dr_all:
        st.warning("⚠️ No DCA results for this well.")
        return
    ic1, ic2, ic3 = st.columns(3)
    with ic1:
        model_sel = st.selectbox("Model", list(dr_all.keys()), key="eur_model_sel",
                                 index=list(dr_all.keys()).index(best_model(dr_all)))
    with ic2:
        econ_lim = st.number_input("Economic Limit (STB/day)", 1.0, 500.0,
                                    value=50.0 * 6.28981, step=5.0, key="eur_econ2")
    with ic3:
        horizon = st.slider("Forecast Horizon (Years)", 5, 50, 10, key="eur_horizon2")
    dr = dr_all.get(model_sel, {})
    if not dr:
        st.error("Selected model unavailable.")
        return
    eur = calculate_eur(
        qi=dr["qi"], Di_day=dr["Di_day"], b=dr["b"], model=model_sel,
        econ_limit_bbl=econ_lim, horizon_years=horizon,
        peak_date=dr["peak_date"], cum_to_date_bbl=float(df_w["Oil_bbl"].sum()),
    )
    st.session_state.eur_results[well] = dict(
        model=model_sel, **eur,
        **{k: dr[k] for k in ("qi","Di_year","b","r2","rmse","AIC")}
    )
    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_data = [
        (k1, "📊", "EUR (P50)", f"{eur['eur_mmbbl']:.2f}", "MM STB"),
        (k2, "📦", "Cum. Production", f"{eur['cum_to_date_mmbbl']:.2f}", "MM STB"),
        (k3, "🔋", "Remaining Recovery", f"{eur['remaining_mmbbl']:.2f}", "MM STB"),
        (k4, "⏱️", "Time to Econ. Limit", f"{eur['t_econ_years']:.1f}", "yrs"),
        (k5, "⛽", "Peak Rate", f"{eur['peak_rate']:,.0f}", "STB/d"),
    ]
    for col, icon, label, val, unit in kpi_data:
        with col:
            _html(kpi_card(icon, label, val, unit))
    _html("<br>")
    st.plotly_chart(chart_cumulative_forecast(df_w, eur, well), use_container_width=True)
    _html("<br>")
    PBG = get_plotly_bg()
    fig_rate = _themed_fig()
    monthly = (df_w.set_index("Date")["Oil_bbl"].resample("ME").mean()
                .dropna().reset_index())
    monthly.columns = ["Date", "Oil_bbl"]
    fig_rate.add_trace(go.Scatter(x=monthly["Date"], y=monthly["Oil_bbl"],
                                  name="Actual", mode="lines",
                                  line=dict(color=C["green"], width=2)))
    fig_rate.add_trace(go.Scatter(
        x=eur["dates_forecast"][:horizon*365:30],
        y=eur["q_forecast"][:horizon*365:30],
        name="Forecast (P50)", mode="lines",
        line=dict(color=C["orange"], width=2, dash="dash"),
    ))
    fig_rate.add_hline(y=econ_lim, line_dash="dot", line_color=C["red"],
                       annotation_text="Economic Limit",
                       annotation_font_color=C["red"])
    fig_rate.update_layout(
        title="Production Rate Forecast",
        xaxis_title="Date", yaxis_title="Oil Rate (STB/day)",
        height=320, hovermode="x unified",
        **{k:v for k,v in PBG.items() if k!="margin"},
        margin=dict(l=55,r=20,t=50,b=40),
    )
    st.plotly_chart(fig_rate, use_container_width=True)
    _html(f'<p style="font-weight:600;color:{C["heading"]}">EUR Results (Base Case)</p>')
    res_cols = st.columns(2)
    res_data = {
        "Estimated Ultimate Recovery (EUR)": f"{eur['eur_mmbbl']:.3f} MM STB",
        "Cumulative Production to Date": f"{eur['cum_to_date_mmbbl']:.3f} MM STB",
        "Remaining Recovery": f"{eur['remaining_mmbbl']:.3f} MM STB",
        "Time to Economic Limit": f"{eur['t_econ_years']:.1f} years",
        "Peak Rate (qi)": f"{eur['peak_rate']:,.0f} STB/day",
        "Economic Limit": f"{econ_lim:.0f} STB/day",
        "Decline Rate (Di)": f"{dr['Di_year']:.4f} /yr",
        "Arps Exponent (b)": f"{dr['b']:.3f}",
        "Model R²": f"{dr['r2']:.4f}",
        "Forecast Model": model_sel,
    }
    items = list(res_data.items())
    half = len(items) // 2
    with res_cols[0]:
        _html('<div class="panel-card">' + "".join(result_row(k,v) for k,v in items[:half]) + "</div>")
    with res_cols[1]:
        _html('<div class="panel-card">' + "".join(result_row(k,v) for k,v in items[half:]) + "</div>")


def page_model_settings():
    C = get_C()
    _html('<div class="page-title">Model Settings</div>')
    s = st.session_state.settings
    t1, t2, t3 = st.tabs(["Decline Model", "Advanced Settings", "Units & Display"])
    with t1:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown("**Decline Model Options**")
            s["model"] = st.selectbox(
                "Default Decline Model", ["Hyperbolic","Exponential","Harmonic"],
                index=["Hyperbolic","Exponential","Harmonic"].index(s.get("model","Hyperbolic")),
            )
            s["auto_model"] = st.checkbox("Automatic Model Selection (best R²)",
                                          value=s.get("auto_model", True), key="auto_model")
            st.markdown("**Available Models**")
            available_models = s.get("available_models",
                                     {"Exponential": True, "Harmonic": True, "Hyperbolic": True})
            for m in ["Exponential","Harmonic","Hyperbolic"]:
                available_models[m] = st.checkbox(m, value=available_models.get(m, True),
                                                   key=f"model_chk_{m}")
            s["available_models"] = available_models
        with c2:
            st.markdown("**Curve Fitting Method**")
            st.selectbox("Method", ["Nonlinear Least Squares (scipy)",
                                    "Differential Evolution"], key="fit_method")
            st.checkbox("Robust Fitting (Huber loss)", value=False, key="robust_fit")
            st.checkbox("Outlier Detection", value=True, key="outlier_det")
            st.slider("Outlier Threshold (Std Dev)", 1.0, 5.0, 3.0, key="outlier_std")
    with t2:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown("**Forecast Settings**")
            s["econ_limit"] = st.number_input(
                "Economic Limit (Sm³/day)", 1.0, 500.0,
                value=float(s.get("econ_limit", 50.0)), step=5.0,
            )
            s["horizon"] = st.slider("Forecast Horizon (Years)", 5, 50,
                                     int(s.get("horizon", 30)))
        with c2:
            st.markdown("**Data Smoothing**")
            s["smooth"] = st.checkbox("Apply Smoothing", value=bool(s.get("smooth", True)), key="apply_smoothing")
            smooth_method = st.selectbox("Smoothing Method",
                                         ["Moving Average","Exponential Weighted","Savitzky-Golay"],
                                         key="smooth_method")
            if smooth_method == "Moving Average":
                st.slider("Window Size (Days)", 7, 90, 30, key="smooth_window")
    with t3:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Unit System**")
            st.info("✅ Field Units  (STB/day, Mscf/day)  – fixed for this session")
            unit_data = pd.DataFrame([
                {"Fluid": "Oil", "Input Unit": "Sm³/day", "Output Unit": "STB/day", "Factor": "6.2898"},
                {"Fluid": "Gas", "Input Unit": "Sm³/day", "Output Unit": "Mscf/day", "Factor": "0.0353"},
                {"Fluid": "Water", "Input Unit": "Sm³/day", "Output Unit": "STB/day", "Factor": "6.2898"},
            ])
            st.table(unit_data)
        with c2:
            st.markdown("**Display Preferences**")
            st.selectbox("Time Axis Format", ["Calendar Date","Days from Peak","Years from Peak"], key="time_axis")
            st.selectbox("Rate Scale Default", ["Linear","Logarithmic"], key="rate_scale")
            st.selectbox("Volume Unit for EUR", ["MM STB","STB","BOE"], key="eur_unit")


def page_insights():
    C = get_C()
    _html('<div class="page-title">Field Insights</div>')
    wells_data = st.session_state.wells
    selected = st.session_state.selected
    eur_res = st.session_state.eur_results
    if not selected:
        st.info("⬅️  Select wells and run DCA first.")
        return
    if any(w not in eur_res or not eur_res[w] for w in selected):
        with st.spinner("⚙️ Calculating field-level EUR and decline metrics…"):
            _run_dca_all()
        eur_res = st.session_state.eur_results
    eur_wells = [w for w in selected if w in eur_res]
    total_eur = sum(eur_res.get(w, {}).get("eur_mmbbl", 0) for w in eur_wells)
    avg_di = float(np.mean([eur_res[w].get("Di_year", 0) for w in eur_wells])) if eur_wells else 0.0
    avg_eur = total_eur / max(1, len(eur_wells)) if eur_wells else 0.0
    k1, k2, k3, k4 = st.columns(4)
    with k1: _html(kpi_card("🏭","Total Wells", f"{len(selected)}", "", ""))
    with k2: _html(kpi_card("📊","Total Oil EUR", f"{total_eur:.2f}", "MM STB", ""))
    with k3: _html(kpi_card("📉","Avg Decline Rate", f"{avg_di:.3f}", "1/yr", ""))
    with k4: _html(kpi_card("⛽","Avg EUR per Well", f"{avg_eur:.2f}", "MM STB", ""))
    _html("<br>")
    c1, c2 = st.columns([3, 2], gap="medium")
    with c1:
        if len(eur_res) >= 2:
            st.plotly_chart(chart_eur_vs_decline(eur_res), use_container_width=True)
        else:
            st.info("Run DCA on 2+ wells to see EUR vs Decline Rate scatter.")
    with c2:
        _html(f'<p style="font-weight:600;color:{C["heading"]};margin-bottom:8px">Top Performing Wells</p>')
        rows = []
        for well in selected:
            er = eur_res.get(well, {})
            rows.append({
                "Well": well,
                "EUR (MM STB)": round(er.get("eur_mmbbl", 0), 2),
                "Di (1/yr)": round(er.get("Di_year", 0), 3),
                "R²": round(er.get("r2", 0), 3),
            })
        rows_df = pd.DataFrame(rows).sort_values("EUR (MM STB)", ascending=False)
        st.dataframe(rows_df, use_container_width=True, hide_index=True)
    _html(f'<p style="font-weight:600;color:{C["heading"]};margin:16px 0 8px">Cumulative Oil Comparison</p>')
    PBG = get_plotly_bg()
    fig_cum = _themed_fig()
    for i, well in enumerate(selected):
        df = wells_data.get(well)
        if df is None:
            continue
        cum = df["Oil_bbl"].cumsum() / 1e6
        fig_cum.add_trace(go.Scatter(
            x=df["Date"], y=cum, name=well, mode="lines",
            line=dict(color=WELL_COLOURS[i % len(WELL_COLOURS)], width=2),
        ))
    fig_cum.update_layout(
        xaxis_title="Date", yaxis_title="Cumulative Oil (MM STB)",
        height=300, hovermode="x unified",
        **{k:v for k,v in PBG.items() if k!="margin"},
        margin=dict(l=55,r=20,t=10,b=40),
    )
    st.plotly_chart(fig_cum, use_container_width=True)
    _html(f'<p style="font-weight:600;color:{C["heading"]};margin:16px 0 8px">Insights & Recommendations</p>')
    if eur_res:
        best_w = max(eur_res, key=lambda w: eur_res[w].get("eur_mmbbl", 0))
        hi_di = [w for w in eur_res if eur_res[w].get("Di_year", 0) > avg_di * 1.3]
        _html(
            insight_item("🏆", f"{best_w} has the highest EUR at "
                               f"{eur_res[best_w].get('eur_mmbbl',0):.2f} MM STB.", C["green"]) +
            insight_item("📉", f"Average field decline rate: {avg_di:.3f}/yr.", C["orange"]) +
            ("".join(insight_item("⚠️",
                f"{w}: Decline rate {eur_res[w]['Di_year']:.3f}/yr is 30% above field average.",
                C["red"]) for w in hi_di[:2]) if hi_di else "")
        )


def page_reports():
    C = get_C()
    _html('<div class="page-title">Reports & Export</div>')
    wells_data = st.session_state.wells
    selected = st.session_state.selected
    eur_res = st.session_state.eur_results
    c1, c2 = st.columns([2, 1], gap="medium")
    with c1:
        st.markdown("**Generate Report**")
        report_type = st.selectbox("Report Type",
            ["DCA Summary Report","EUR Forecast Report",
             "Well Performance Report","Executive Summary"], key="report_type")
        wells_for_report = st.multiselect("Select Wells", selected, default=selected[:3], key="report_wells")
        inc_col1, inc_col2 = st.columns(2)
        with inc_col1:
            inc_prod = st.checkbox("Production Data & Charts", True, key="inc_prod")
            inc_dca = st.checkbox("DCA Results", True, key="inc_dca")
        with inc_col2:
            inc_eur = st.checkbox("EUR Forecast", True, key="inc_eur")
            inc_fi = st.checkbox("Field Insights", True, key="inc_fi")
        if st.button("📄 Generate Excel Report", use_container_width=True, key="generate_report"):
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                if wells_data and selected and wells_for_report:
                    all_rows = []
                    for well in wells_for_report:
                        df = wells_data.get(well, pd.DataFrame())
                        if len(df):
                            monthly = (df.set_index("Date")[['Oil_bbl','Gas_mscf','Water_bbl']]
                                       .resample("ME").mean().reset_index())
                            monthly.insert(0, "Well", well)
                            all_rows.append(monthly)
                    if all_rows:
                        pd.concat(all_rows).to_excel(writer, sheet_name="Production", index=False)
                if eur_res and wells_for_report:
                    eur_rows = []
                    for well in wells_for_report:
                        er = eur_res.get(well, {})
                        if er:
                            eur_rows.append({
                                "Well": well,
                                "Model": er.get("model", ""),
                                "qi (STB/d)": round(er.get("qi", 0), 1),
                                "Di (1/yr)": round(er.get("Di_year", 0), 4),
                                "b": round(er.get("b", 0), 3),
                                "R2": round(er.get("r2", 0), 4),
                                "EUR (MM STB)": round(er.get("eur_mmbbl", 0), 3),
                                "Remaining (MM STB)": round(er.get("remaining_mmbbl", 0), 3),
                                "Econ Limit (yrs)": er.get("t_econ_years", ""),
                            })
                    if eur_rows:
                        pd.DataFrame(eur_rows).to_excel(writer, sheet_name="DCA_EUR", index=False)
            buf.seek(0)
            st.download_button(
                label="⬇️ Download Excel Report",
                data=buf.getvalue(),
                file_name=f"PetroDCA_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_report",
            )
    with c2:
        st.markdown("**Export Data**")
        if selected and wells_data:
            all_dfs = []
            for w in selected:
                df = wells_data.get(w, pd.DataFrame())
                if len(df):
                    d = df[["Date","Oil_bbl","Gas_mscf","Water_bbl"]].copy()
                    d.insert(0, "Well", w)
                    all_dfs.append(d)
            if all_dfs:
                csv_str = pd.concat(all_dfs).to_csv(index=False)
                st.download_button("📥 Export to CSV", csv_str,
                                   file_name="production_data.csv",
                                   mime="text/csv", use_container_width=True,
                                   key="download_csv")
        if eur_res:
            eur_rows = [{
                "Well": w,
                "EUR (MM STB)": round(eur_res[w].get("eur_mmbbl", 0), 3),
                "Di (1/yr)": round(eur_res[w].get("Di_year", 0), 4),
                "R2": round(eur_res[w].get("r2", 0), 4),
            } for w in selected if eur_res.get(w)]
            if eur_rows:
                st.download_button("📥 Export EUR Results",
                                   pd.DataFrame(eur_rows).to_csv(index=False),
                                   file_name="eur_results.csv",
                                   mime="text/csv", use_container_width=True,
                                   key="download_eur")
        st.markdown("**Field Summary**")
        if eur_res and selected:
            total_eur = sum(eur_res.get(w, {}).get("eur_mmbbl", 0) for w in selected)
            avg_r2 = np.mean([eur_res.get(w, {}).get("r2", 0) for w in selected
                              if eur_res.get(w, {}).get("r2")])
            html = (result_row("Wells Analysed", str(len(selected))) +
                    result_row("Total EUR", f"{total_eur:.2f} MM STB") +
                    result_row("Avg Model R²", f"{avg_r2:.4f}"))
            _html(f'<div class="panel-card">{html}</div>')


def page_ai_log():
    C = get_C()
    _html('<div class="page-title">AI Interaction Log</div>')
    tab1, tab2 = st.tabs(["💬 Prompts & Responses", "📋 Summary"])
    with tab1:
        _html(f"""
        <div class="panel-card" style="margin-bottom:12px">
          <p style="color:{C['muted']};font-size:0.85rem">
          AI is used for code generation, debugging, optimisation, documentation,
          and idea generation. All DCA fitting is performed using rigorous
          scipy non-linear least squares — AI suggestions are advisory only.
          </p>
        </div>""")
        prompt = st.text_area("Ask a question about your production data or DCA results…",
                              placeholder="e.g. Why is my decline rate unusually high for well 15/9-F-11?",
                              height=80, key="ai_prompt")
        if st.button("Send", key="ai_send") and prompt.strip():
            eur_res = st.session_state.eur_results
            well = st.session_state.selected[0] if st.session_state.selected else None
            er = eur_res.get(well, {}) if well else {}
            resp = _ai_advisor(prompt, er, well)
            st.session_state.ai_log.append({"role":"user", "text": prompt})
            st.session_state.ai_log.append({"role":"ai", "text": resp})
        for entry in reversed(st.session_state.ai_log[-20:]):
            if entry["role"] == "user":
                _html(f"""
                <div style="background:{C['card2']};border:1px solid {C['border']};border-radius:10px;
                            padding:10px 14px;margin-bottom:8px;font-size:0.87rem">
                  <span style="color:{C['muted']};font-size:0.75rem">You</span><br>
                  <span style="color:{C['text']}">{entry['text']}</span>
                </div>""")
            else:
                _html(f"""
                <div style="background:{C['card']};border:1px solid {C['border']};border-radius:10px;
                            padding:10px 14px;margin-bottom:8px;font-size:0.87rem">
                  <span style="color:{C['green']};font-size:0.75rem">AI Response</span><br>
                  <span style="color:{C['text']}">{entry['text']}</span>
                </div>""")
        if st.session_state.ai_log:
            st.caption(f"Total Interactions: {len(st.session_state.ai_log)//2}")
    with tab2:
        st.markdown("**How AI is Used in PetroDCA**")
        st.info("""
        **PetroDCA** uses data-driven analysis powered by:

        • **scipy curve_fit** – non-linear least squares for Arps model fitting  
        • **Automatic model selection** – best R² across Exponential / Harmonic / Hyperbolic  
        • **AIC scoring** – penalises over-parameterised models  
        • **AI advisor** – interprets results and flags anomalies  

        All computations are deterministic and reproducible.
        """)


def _ai_advisor(prompt, er, well) -> str:
    prompt_l = prompt.lower()
    if any(w in prompt_l for w in ["decline rate", "high decline", "di"]):
        di = er.get("Di_year", 0)
        if di > 0.5:
            return (f"The decline rate for <b>{well}</b> is <b>{di:.3f}/yr</b>, "
                    "which is relatively high (>0.5/yr). Consider reviewing reservoir "
                    "pressure data and evaluating artificial lift or infill drilling options.")
        elif di > 0.2:
            return (f"The decline rate for <b>{well}</b> is <b>{di:.3f}/yr</b> — "
                    "moderate. Continue monitoring monthly trends.")
        else:
            return f"Decline rate {di:.3f}/yr is relatively low — typical for high-permeability reservoirs."
    if "eur" in prompt_l or "ultimate recovery" in prompt_l:
        eur = er.get("eur_mmbbl", 0)
        return (f"Estimated Ultimate Recovery for <b>{well}</b> is <b>{eur:.2f} MM STB</b>. "
                "This is calculated by integrating the fitted Arps decline curve to the economic limit.")
    if "hyperbolic" in prompt_l or "model" in prompt_l:
        r2 = er.get("r2", 0)
        return (f"The Hyperbolic Arps model achieved R²={r2:.4f} for <b>{well}</b>. "
                "Hyperbolic decline is the most general Arps form.")
    if "water" in prompt_l or "wor" in prompt_l:
        return "Rising WOR suggests water influx or coning. Check aquifer material balance."
    if "r2" in prompt_l or "fit" in prompt_l or "accuracy" in prompt_l:
        r2 = er.get("r2", 0)
        rmse = er.get("rmse", 0)
        return (f"Model fit for <b>{well}</b>: R²={r2:.4f}, RMSE={rmse:,.0f} STB/d. "
                "R² > 0.90 indicates a reliable fit.")
    return ("I can help analyse your decline curve results. Ask me about: "
            "decline rates, EUR estimates, model selection, water cut trends, "
            "R² fit quality, or forecast sensitivity.")
