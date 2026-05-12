import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from .config import WELL_COLOURS
from .theme import get_C, get_plotly_bg


def _themed_fig(**kwargs) -> go.Figure:
    fig = go.Figure(**kwargs)
    fig.update_layout(**get_plotly_bg())
    return fig


def _phase_label(phase: str) -> tuple:
    return {
        "Oil_bbl": ("Oil Rate", "STB/day"),
        "Gas_mscf": ("Gas Rate", "Mscf/day"),
        "Water_bbl": ("Water Rate", "STB/day"),
    }.get(phase, (phase, ""))


def chart_production_rates(wells_data, selected, phases, smooth=True) -> go.Figure:
    phase_cfg = {
        "Oil_bbl": ("#10b981", "solid", "Oil (STB/day)"),
        "Gas_mscf": ("#ef4444", "dot", "Gas (Mscf/day)"),
        "Water_bbl": ("#3b82f6", "dashdot", "Water (STB/day)"),
    }
    PBG = get_plotly_bg()
    fig = _themed_fig()
    for i, well in enumerate(selected):
        df = wells_data.get(well)
        if df is None:
            continue
        col = WELL_COLOURS[i % len(WELL_COLOURS)]
        for phase, (ph_col, dash, lbl) in phase_cfg.items():
            if phase not in phases or phase not in df.columns:
                continue
            y = df[phase].rolling(30, min_periods=1).mean() if smooth else df[phase]
            nm = f"{lbl}" if len(selected) == 1 else f"{well} – {lbl}"
            fig.add_trace(go.Scatter(
                x=df["Date"], y=y, name=nm, mode="lines",
                line=dict(color=ph_col if len(selected) == 1 else col,
                          dash=dash, width=1.8),
            ))
    fig.update_layout(
        showlegend=True, height=280,
        legend=dict(orientation="v", font=dict(size=11, color=PBG["font"]["color"])),
        **{k: v for k, v in PBG.items() if k not in ["margin", "legend"]},
        margin=dict(l=10, r=10, t=50, b=10),
    )
    return fig


def chart_decline_curve(res, model, actual_dates, actual_q,
                        log_scale=False, forecast_years=10, eur_dict=None) -> go.Figure:
    C = get_C()
    PBG = get_plotly_bg()
    r = res[model]
    dates_fit = pd.to_datetime(r["dates"])
    fig = _themed_fig()
    fig.add_trace(go.Scatter(
        x=actual_dates, y=actual_q,
        name="Actual", mode="markers",
        marker=dict(color=C["muted"], size=4, opacity=0.7),
    ))
    fig.add_trace(go.Scatter(
        x=dates_fit, y=r["q_fitted"],
        name=f"Fitted ({model})", mode="lines",
        line=dict(color=C["green"], width=2.5),
    ))
    if eur_dict:
        fore_dates = eur_dict["dates_forecast"][:forecast_years * 365]
        fore_q = eur_dict["q_forecast"][:forecast_years * 365]
        fig.add_trace(go.Scatter(
            x=fore_dates, y=fore_q,
            name="Forecast", mode="lines",
            line=dict(color=C["orange"], width=2, dash="dash"),
        ))
        fig.add_hline(
            y=eur_dict["econ_limit"], line_dash="dot",
            line_color=C["red"], line_width=1,
            annotation_text=f"Econ. Limit {eur_dict['econ_limit']:.0f} STB/d",
            annotation_font_color=C["red"],
        )
    fig.update_layout(
        title=dict(text=f"Decline Curve ({model})", font=dict(size=14, color=C["heading"])),
        xaxis_title="Date", yaxis_title="Oil Rate (STB/day)",
        yaxis_type="log" if log_scale else "linear",
        hovermode="x unified", height=380,
        **{k: v for k, v in PBG.items() if k != "margin"},
        margin=dict(l=50, r=20, t=60, b=40),
    )
    return fig


def chart_residuals(res, model) -> go.Figure:
    C = get_C()
    PBG = get_plotly_bg()
    r = res[model]
    resid = r["q_actual"] - r["q_fitted"]
    dates = pd.to_datetime(r["dates"])
    fig = _themed_fig()
    fig.add_hline(y=0, line_color=C["border"], line_width=1)
    fig.add_trace(go.Scatter(
        x=dates, y=resid, mode="markers",
        marker=dict(color=np.where(resid >= 0, C["green"], C["red"]),
                    size=5, opacity=0.8),
        name="Residual",
    ))
    fig.update_layout(
        title=dict(text="Residuals (Actual − Fitted)", font=dict(size=12, color=C["heading"])),
        xaxis_title="Date", yaxis_title="Residual (STB/day)",
        height=200,
        **{k: v for k, v in PBG.items() if k != "margin"},
        margin=dict(l=50, r=20, t=40, b=30),
    )
    return fig


def chart_cumulative_forecast(df_actual, eur_dict, well_name, phase="Oil_bbl") -> go.Figure:
    C = get_C()
    PBG = get_plotly_bg()
    cum_actual = df_actual[phase].cumsum()
    dates_a = df_actual["Date"]
    fore_dates = eur_dict["dates_forecast"]
    fore_cum = eur_dict["cum_forecast"] + float(cum_actual.iloc[-1])
    fig = _themed_fig()
    fig.add_trace(go.Scatter(
        x=dates_a, y=cum_actual / 1e6,
        name="Actual", mode="lines",
        line=dict(color=C["green"], width=2.5),
    ))
    fig.add_trace(go.Scatter(
        x=fore_dates, y=fore_cum / 1e6,
        name="Forecast (P50)", mode="lines",
        line=dict(color=C["green"], width=2, dash="dash"),
        fill="tonexty", fillcolor="rgba(16,185,129,0.08)",
    ))
    fig.add_annotation(
        x=0.98, y=0.92, xref="paper", yref="paper",
        text=f"EUR (P50)<br><b>{eur_dict['eur_mmbbl']:.2f} MM STB</b>",
        showarrow=False, align="right",
        font=dict(color=C["green"], size=12),
        bgcolor=C["card"], bordercolor=C["border"],
    )
    fig.update_layout(
        title=dict(text="Cumulative Oil Production", font=dict(size=14, color=C["heading"])),
        xaxis_title="Date", yaxis_title="Cumulative Oil (MM STB)",
        hovermode="x unified", height=320,
        **{k: v for k, v in PBG.items() if k != "margin"},
        margin=dict(l=55, r=20, t=60, b=40),
    )
    return fig


def chart_production_split_by_phase(wells_data, selected) -> dict:
    C = get_C()
    PBG = get_plotly_bg()
    phase_config = {
        "Oil": ("Oil_bbl", "#10b981", "STB/day"),
        "Gas": ("Gas_mscf", "#ef4444", "Mscf/day"),
        "Water": ("Water_bbl", "#3b82f6", "STB/day"),
    }
    figures = {}
    for phase_name, (col_name, colour, unit) in phase_config.items():
        well_data = []
        total = 0.0
        for well in selected:
            df = wells_data.get(well)
            if df is None or len(df) == 0:
                continue
            last = df.iloc[-1]
            value = float(last.get(col_name, 0))
            if col_name == "Gas_mscf":
                value = value * 6
            well_data.append({"well": well, "value": value})
            total += value
        fig = _themed_fig()
        if well_data:
            well_names = [w["well"] for w in well_data]
            values = [w["value"] for w in well_data]
            colours = [WELL_COLOURS[i % len(WELL_COLOURS)] for i in range(len(well_names))]
            fig.add_trace(go.Pie(
                labels=well_names, values=values, hole=0.55,
                marker=dict(colors=colours),
                textinfo="percent+label",
                textfont=dict(size=10, color=C["text"]),
                hovertemplate="<b>%{label}</b><br>%{value:,.0f} " + unit + "<br>%{percent}<extra></extra>",
            ))
            total_display = f"{total:,.0f}" if col_name != "Gas_mscf" else f"{total/6:,.1f}"
            total_unit = unit if col_name != "Gas_mscf" else "Mscf/day"
            fig.add_annotation(
                text=f"<b>{total_display}</b><br>{total_unit}",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=12, color=C["text"]),
            )
        fig.update_layout(
            title=dict(text=f"{phase_name} Production (Latest Day)", font=dict(size=12, color=C["heading"])),
            showlegend=True, height=250,
            legend=dict(orientation="v", font=dict(size=9, color=C["text"]), x=1.0, y=1.0),
            **{k: v for k, v in PBG.items() if k not in ["margin", "legend"]},
            margin=dict(l=10, r=10, t=40, b=10),
        )
        figures[phase_name] = fig
    return figures


def chart_eur_vs_decline(eur_results) -> go.Figure:
    C = get_C()
    PBG = get_plotly_bg()
    wells = [w for w in eur_results if eur_results[w].get("eur_mmbbl")]
    eurs = [eur_results[w]["eur_mmbbl"] for w in wells]
    dis = [eur_results[w]["Di_year"] for w in wells]
    qis = [eur_results[w]["qi"] for w in wells]
    clrs = [WELL_COLOURS[i % len(WELL_COLOURS)] for i in range(len(wells))]
    fig = _themed_fig()
    fig.add_trace(go.Scatter(
        x=dis, y=eurs, mode="markers+text",
        text=[w.split("/")[-1] for w in wells],
        textposition="top center",
        textfont=dict(color=C["text"]),
        marker=dict(size=[max(10, q / 500) for q in qis],
                    color=clrs, opacity=0.85,
                    line=dict(width=1, color=C["border"])),
        customdata=list(zip(wells, qis)),
        hovertemplate="<b>%{customdata[0]}</b><br>EUR: %{y:.2f} MM STB<br>"
                      "Di: %{x:.3f}/yr<br>qi: %{customdata[1]:,.0f} STB/d<extra></extra>",
    ))
    fig.update_layout(
        title=dict(text="EUR vs Decline Rate", font=dict(size=13, color=C["heading"])),
        xaxis_title="Decline Rate (1/yr)",
        yaxis_title="EUR (MM STB)",
        height=320,
        **{k: v for k, v in PBG.items() if k != "margin"},
        margin=dict(l=55, r=20, t=50, b=50),
    )
    return fig
