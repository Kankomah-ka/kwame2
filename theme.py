"""
Theme and styling module for PetroDCA
Handles color palettes, CSS injection, and Plotly theme configuration
"""

import streamlit as st
import plotly.graph_objects as go
from .config import C_LIGHT, C_DARK


def _html(s: str) -> None:
    """Render HTML safely using st.html or st.markdown."""
    if hasattr(st, "html"):
        try:
            st.html(s)
        except Exception:
            st.markdown(s, unsafe_allow_html=True)
    else:
        st.markdown(s, unsafe_allow_html=True)


def _themed_fig(**kwargs) -> go.Figure:
    fig = go.Figure(**kwargs)
    fig.update_layout(**get_plotly_bg())
    return fig


def get_C() -> dict:
    """Return active colour palette based on current theme setting."""
    return C_DARK if st.session_state.get("theme", "Dark") == "Dark" else C_LIGHT


def get_plotly_bg() -> dict:
    """Get Plotly background theme configuration."""
    C = get_C()
    return dict(
        plot_bgcolor  = C["chart_bg"],
        paper_bgcolor = C["chart_paper"],
        font          = dict(color=C["chart_text"], family="Inter, sans-serif"),
        xaxis = dict(
            gridcolor=C["chart_grid"], linecolor=C["chart_grid"],
            tickfont=dict(color=C["chart_tick"]),
        ),
        yaxis = dict(
            gridcolor=C["chart_grid"], linecolor=C["chart_grid"],
            tickfont=dict(color=C["chart_tick"]),
        ),
        legend = dict(bgcolor=C["card"], bordercolor=C["border"],
                      font=dict(color=C["text"])),
        margin = dict(l=50, r=20, t=40, b=40),
    )


def inject_css():
    """Inject CSS styling for the entire application."""
    C = get_C()
    _html(f"""
<style>
/* ── Google Font ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ──────────────────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    color: {C['text']};
}}
.stApp {{
    background-color: {C['bg']};
}}
header, [data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stAppViewContainer"], .css-1outpf7, .css-1v3fvcr {{
    background-color: {C['bg']} !important;
    color: {C['text']} !important;
}}

/* ── Sidebar ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {{
    background-color: {C['sidebar']} !important;
    border-right: 1px solid {C['border']};
}}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stSelectbox label {{
    color: {C['sidebar_muted']} !important;
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}
[data-testid="stSidebar"] .stMarkdown,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not([data-testid]),
[data-testid="stSidebar"] .stCaption {{
    color: {C['sidebar_text']} !important;
}}

/* ── Sidebar nav buttons ─────────────────────────────────── */
[data-testid="stSidebar"] .stButton > button {{
    background-color: {C['card2']} !important;
    color: {C['sidebar_text']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 8px;
    font-size: 0.88rem;
    font-weight: 500;
    display: flex;
    justify-content: flex-start;
    align-items: center;
    text-align: left !important;
    gap: 10px;
    padding: 8px 16px;
    margin-bottom: 6px;
    transition: all 0.18s;
    width: 100%;
}}
[data-testid="stSidebar"] .stButton > button > div,
[data-testid="stSidebar"] .stButton > button > span {{
    justify-content: flex-start;
    text-align: left !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background-color: {C['blue']} !important;
    border-color: {C['blue']} !important;
    color: #ffffff !important;
    transform: none;
}}

/* ── Theme toggle area ───────────────────────────────────── */
.theme-toggle-wrap {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
}}
.theme-label {{
    color: {C['sidebar_muted']};
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    flex: 1;
}}

/* ── Radio nav (legacy – keep for safety) ────────────────── */
[data-testid="stSidebar"] div[role="radiogroup"] label {{
    text-transform: none !important;
    letter-spacing: 0 !important;
    font-size: 0.9rem !important;
    padding: 8px 12px;
    border-radius: 8px;
    margin-bottom: 2px;
    color: {C['sidebar_muted']} !important;
    cursor: pointer;
    display: block !important;
    width: 100% !important;
}}

/* ── Main content text ───────────────────────────────────── */
.stMarkdown, .stText, p, li, span, div {{
    color: {C['text']};
}}
h1, h2, h3, h4, h5, h6 {{
    color: {C['heading']} !important;
}}
.stMarkdown strong {{
    color: {C['heading']};
}}

/* ── Input fields ────────────────────────────────────────── */
.stSelectbox > div > div,
.stMultiSelect > div > div {{
    background-color: {C['input_bg']} !important;
    border: 1px solid {C['border']} !important;
    color: {C['text']} !important;
    border-radius: 8px;
}}
.stSelectbox label, .stMultiSelect label,
.stNumberInput label, .stSlider label,
.stToggle label, .stCheckbox label,
.stTextInput label, .stTextArea label,
.stDateInput label, .stRadio label {{
    color: {C['muted']} !important;
    font-size: 0.82rem;
}}
.stTextInput > div > input,
.stTextArea > div > textarea,
.stNumberInput > div > input {{
    background-color: {C['input_bg']} !important;
    border: 1px solid {C['border']} !important;
    color: {C['text']} !important;
    border-radius: 8px;
}}
.stDateInput input {{
    background-color: {C['input_bg']} !important;
    border: 1px solid {C['border']} !important;
    color: {C['text']} !important;
    border-radius: 6px;
}}
/* Dropdown menu items */
[data-baseweb="popover"] li,
[data-baseweb="menu"] li {{
    background-color: {C['card']} !important;
    color: {C['text']} !important;
}}
[data-baseweb="popover"],
[data-baseweb="menu"] {{
    background-color: {C['card']} !important;
    border: 1px solid {C['border']} !important;
}}
/* Multiselect tags */
[data-baseweb="tag"] {{
    background-color: {C['tag_bg']} !important;
    color: {C['tag_text']} !important;
}}

/* ── Main action buttons ─────────────────────────────────── */
.stButton > button {{
    background-color: {C['btn_bg']};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 8px 16px;
    transition: all 0.2s;
}}
.stButton > button:hover {{
    background-color: {C['btn_hover']};
    transform: translateY(-1px);
}}

/* ── Download buttons – Enhanced visibility ───────────────── */
[data-testid="stDownloadButton"] button {{
    background: linear-gradient(135deg, {C['btn_bg']} 0%, {C['btn_hover']} 100%) !important;
    color: #ffffff !important;
    border: 2px solid {C['blue']} !important;
    border-radius: 8px;
    font-weight: 700;
    padding: 10px 18px !important;
    transition: all 0.25s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}}
[data-testid="stDownloadButton"] button:hover {{
    background: linear-gradient(135deg, {C['btn_hover']} 0%, {C['btn_bg']} 100%) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.16);
    transform: translateY(-2px);
}}

/* ── File uploader ───────────────────────────────────────── */
[data-testid="stFileUploader"] {{
    background-color: #1a2332 !important;
    border: 1px dashed #3a4a62 !important;
    border-radius: 10px;
    padding: 12px;
}}
[data-testid="stFileUploader"] button {{
    background-color: #000000 !important;
    border: 1px solid #000000 !important;
    color: #ffffff !important;
}}
/* Caption text – Keep white for visibility in both modes */
[data-testid="stFileUploader"] * {{
    color: #ffffff !important;
}}
[data-testid="stFileUploader"] button {{
    background-color: #000000 !important;
    border: 1px solid #000000 !important;
    color: #ffffff !important;
}}

/* ── DataFrames / tables ─────────────────────────────────── */
.stDataFrame, [data-testid="stDataFrame"] {{
    background-color: {C['card']} !important;
}}
[data-testid="stDataFrame"] th {{
    background-color: {C['card2']} !important;
    color: {C['heading']} !important;
    border-bottom: 1px solid {C['border']} !important;
}}
[data-testid="stDataFrame"] td {{
    color: {C['text']} !important;
    border-bottom: 1px solid {C['border']} !important;
}}
.stTable table {{
    background-color: {C['card']} !important;
    color: {C['text']} !important;
}}
.stTable th {{
    background-color: {C['card2']} !important;
    color: {C['heading']} !important;
    border-bottom: 1px solid {C['border']} !important;
}}
.stTable td {{
    color: {C['text']} !important;
    border-bottom: 1px solid {C['border']} !important;
}}

/* ── Tabs ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {{
    background-color: {C['card2']};
    border-radius: 8px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    background-color: transparent;
    color: {C['muted']};
    border-radius: 6px;
    font-size: 0.85rem;
}}
.stTabs [aria-selected="true"] {{
    background-color: {C['blue']} !important;
    color: #ffffff !important;
}}

/* ── Sliders ─────────────────────────────────────────────── */
.stSlider > div > div > div {{
    background-color: {C['blue']} !important;
}}
.stSlider p {{ color: {C['muted']} !important; }}

/* ── Toggle / Checkbox ───────────────────────────────────── */
.stCheckbox > label, .stToggle > label {{
    color: {C['muted']};
}}

/* ── Info / warning / success boxes ─────────────────────── */
.stAlert {{
    background-color: {C['card2']} !important;
    border: 1px solid {C['border']} !important;
    color: {C['text']} !important;
    border-radius: 10px;
}}
.stInfo  {{ border-left: 3px solid {C['blue']}   !important; }}
.stSuccess {{ border-left: 3px solid {C['green']} !important; }}
.stWarning {{ border-left: 3px solid {C['orange']} !important; }}
.stError {{ border-left: 3px solid {C['red']}    !important; }}

/* ── Metric widget ───────────────────────────────────────── */
[data-testid="stMetricValue"] {{
    color: {C['heading']} !important;
}}
[data-testid="stMetricLabel"] {{
    color: {C['muted']} !important;
}}

/* ── Expander ────────────────────────────────────────────── */
[data-testid="stExpander"] {{
    background-color: {C['card2']} !important;
    border: 1px solid {C['border']} !important;
    border-radius: 10px;
}}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {{
    color: {C['muted']} !important;
}}

/* ── Caption ─────────────────────────────────────────────── */
.stCaption, .stCaption p {{
    color: {C['muted']} !important;
}}

/* ── KPI card ────────────────────────────────────────────── */
.kpi-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 18px 16px;
    display: flex; flex-direction: column;
    gap: 6px;
    min-height: 120px;
    height: auto;
}}
.kpi-icon {{
    font-size: 1.4rem;
    margin-bottom: 2px;
}}
.kpi-label {{
    font-size: 0.78rem;
    color: {C['muted']};
    font-weight: 500;
}}
.kpi-value-row {{
    display: flex;
    align-items: baseline;
    gap: 6px;
    flex-wrap: wrap;
}}
.kpi-unit {{
    font-size: 0.68rem;
    color: {C['muted']};
    white-space: normal;
    flex-shrink: 1;
    min-width: 0;
    overflow-wrap: anywhere;
}}
.kpi-value {{
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1.1;
    color: {C['kpi_value']};
    min-width: 0;
    overflow-wrap: anywhere;
}}
.kpi-delta {{
    font-size: 0.75rem;
    font-weight: 500;
}}
@media (max-width: 1200px) {{
    .kpi-value {{ font-size: 1.6rem; }}
    .kpi-unit  {{ font-size: 0.62rem; }}
}}
.kpi-delta.pos {{ color: {C['green']}; }}
.kpi-delta.neg {{ color: {C['red']};   }}

/* ── Section header ──────────────────────────────────────── */
.section-header {{
    font-size: 1.3rem;
    font-weight: 700;
    color: {C['heading']};
    margin: 0 0 16px;
    padding-bottom: 8px;
    border-bottom: 1px solid {C['border']};
}}

/* ── Panel card ──────────────────────────────────────────── */
.panel-card {{
    background: {C['card']};
    border: 1px solid {C['border']};
    border-radius: 14px;
    padding: 20px;
}}

/* ── Insight alert ───────────────────────────────────────── */
.insight-item {{
    display: flex; align-items: flex-start; gap: 10px;
    background: {C['card2']};
    border: 1px solid {C['border']};
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 8px;
    font-size: 0.84rem;
}}
.insight-item span:last-child {{
    color: {C['text']} !important;
}}

/* ── Page title ──────────────────────────────────────────── */
.page-title {{
    font-size: 1.6rem;
    font-weight: 700;
    color: {C['heading']};
    margin-bottom: 20px;
}}

/* ── Top bar ─────────────────────────────────────────────── */
.top-bar {{
    background: {C['card']};
    border: 1px solid {C['border']};
    padding: 10px 24px;
    display: flex; align-items: center;
    justify-content: space-between;
    border-radius: 12px;
    margin-bottom: 20px;
}}
.top-bar-title  {{ font-weight: 700; font-size: 1.05rem; color: {C['heading']}; }}
.top-bar-sub    {{ color: {C['muted']}; font-size: 0.85rem; margin-left: 8px; }}
.top-bar-label  {{ color: {C['muted']}; font-size: 0.82rem; }}
.top-bar-value  {{ color: {C['heading']}; font-weight: 700; }}

/* ── Result row ──────────────────────────────────────────── */
.result-row {{
    display: flex; justify-content: space-between;
    padding: 6px 0;
    border-bottom: 1px solid {C['border']};
    font-size: 0.87rem;
}}
.result-label {{ color: {C['muted']}; }}
.result-value {{ color: {C['result_value']}; font-weight: 600; }}

/* ── Status bar ──────────────────────────────────────────── */
.status-bar {{
    background: {C['card2']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 8px 10px;
    margin-top: 8px;
    font-size: 0.8rem;
    color: {C['muted']};
}}

/* ── Footer ──────────────────────────────────────────────── */
.app-footer {{
    margin-top: 40px;
    padding-top: 12px;
    border-top: 1px solid {C['border']};
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: {C['muted']};
}}
</style>
""")
