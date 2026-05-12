import streamlit as st
from datetime import datetime
from .theme import _html, get_C
from .data_loader import load_excel_production, load_csv_production


def render_sidebar():
    C = get_C()
    is_dark = st.session_state.get("theme", "Dark") == "Dark"

    with st.sidebar:
        _html(f"""
        <div style="display:flex;align-items:center;gap:10px;padding:8px 0 12px">
          <div style="background:{C['blue']};border-radius:10px;width:40px;height:40px;
                      display:flex;align-items:center;justify-content:center;
                      font-size:1.3rem">🛢️</div>
          <div>
            <div style="font-weight:700;font-size:1.05rem;color:{C['sidebar_text']}">PetroDCA</div>
            <div style="color:{C['sidebar_muted']};font-size:0.75rem">Production Analytics</div>
          </div>
        </div>
        <hr style="border-color:{C['border']};margin:0 0 10px">
        """)

        _html(f"<div style='color:{C['sidebar_muted']};font-size:0.72rem;"
              f"letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px'>"
              f"🎨 Theme</div>")
        col_tog1, col_tog2 = st.columns([1, 1])
        with col_tog1:
            if st.button("☀️ Light" if is_dark else "☀️ Light ✓",
                         key="sidebar_theme_light", use_container_width=True):
                st.session_state.theme = "Light"
                st.rerun()
        with col_tog2:
            if st.button("🌙 Dark ✓" if is_dark else "🌙 Dark",
                         key="sidebar_theme_dark", use_container_width=True):
                st.session_state.theme = "Dark"
                st.rerun()

        _html(f"<hr style='border-color:{C['border']};margin:10px 0'>")

        _html(f"<div style='color:{C['sidebar_muted']};font-size:0.72rem;"
              f"letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px'>"
              f"📂 Project / Selection</div>")
        with st.expander("📋 Data Format Guide", expanded=False):
            st.markdown("""
            **Expected Excel Structure:**
            - One sheet per well (well name as sheet tab)
            - Headers: `Date`, `Oil Rate`, `Gas Rate`, `Water Rate`, `On-Stream Hrs`
            - Units: Sm³/day → auto-converts to STB/day / Mscf/day

            **CSV Alternative:**
            - Columns: `date`, `oil`, `gas`, `water`, `well`
            """)

        uploaded = st.file_uploader(
            "Upload Data (Excel / CSV)",
            type=["xlsx", "xls", "csv"],
            label_visibility="collapsed",
        )
        if uploaded:
            with st.spinner("⏳ Loading and validating data…"):
                try:
                    if uploaded.name.endswith(".csv"):
                        st.session_state.wells = load_csv_production(uploaded)
                    else:
                        st.session_state.wells = load_excel_production(uploaded)
                    st.session_state.selected = list(st.session_state.wells.keys())[:3]
                    st.session_state.dca_results = {}
                    st.session_state.eur_results = {}
                    if st.session_state.wells:
                        st.session_state.data_uploaded = True
                        st.success(f"✅ {len(st.session_state.wells)} well(s) loaded!")
                    else:
                        st.session_state.data_uploaded = False
                        st.error("❌ No valid wells found. Check data format.")
                except Exception as e:
                    st.session_state.data_uploaded = False
                    st.error(f"❌ Error loading file: {e}")

        st.session_state.field_name = st.text_input(
            "Field", value=st.session_state.field_name,
        )
        all_wells = list(st.session_state.wells.keys())
        if all_wells:
            st.session_state.selected = st.multiselect(
                "Wells", options=all_wells,
                default=st.session_state.selected or all_wells[:3],
            )

        if st.session_state.wells:
            with st.expander("📦 Loaded Wells", expanded=False):
                st.markdown(f"**{len(st.session_state.wells)} well(s) loaded**")
                for well, df in st.session_state.wells.items():
                    if "Date" in df.columns and not df["Date"].empty:
                        date_range = f"({df['Date'].min().date()} → {df['Date'].max().date()})"
                    else:
                        date_range = ""
                    st.caption(f"✓ {well}: {len(df)} records {date_range}")

        _html(f"<hr style='border-color:{C['border']};margin:8px 0'>")

        _html(f"<div style='color:{C['sidebar_muted']};font-size:0.72rem;"
              f"letter-spacing:0.08em;text-transform:uppercase;margin-bottom:6px'>"
              f"Navigation</div>")
        pages = [
            ("🏠", "Dashboard Overview"),
            ("📋", "Production Data"),
            ("📉", "Decline Curve Analysis (DCA)"),
            ("🔮", "EUR Prediction"),
            ("⚙️", "Model Settings"),
            ("💡", "Field Insights"),
            ("📤", "Reports & Export"),
            ("🤖", "AI Interaction Log"),
        ]
        if "page" not in st.session_state or st.session_state.page not in [p[1] for p in pages]:
            st.session_state.page = pages[0][1]

        for i, (icon, label) in enumerate(pages):
            if st.button(f"{icon}  {label}", key=f"nav_{i}", use_container_width=True):
                st.session_state.page = label

        _html(f"<hr style='border-color:{C['border']};margin:8px 0'>")

        with st.expander("FILTERS", expanded=True):
            st.markdown("**Date Range**")
            all_dfs = list(st.session_state.wells.values())
            if all_dfs:
                min_d = min(df["Date"].min() for df in all_dfs).to_pydatetime()
                max_d = max(df["Date"].max() for df in all_dfs).to_pydatetime()
                st.slider("", min_value=min_d, max_value=max_d,
                          value=(min_d, max_d), format="YYYY-MM", key="date_filter")
            st.markdown("**Production Phase**")
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                st.checkbox("Oil", True, key="f_oil")
            with fc2:
                st.checkbox("Gas", True, key="f_gas")
            with fc3:
                st.checkbox("Water", True, key="f_water")
            st.selectbox("Rate Type", ["Daily Rates", "Monthly Avg", "Yearly Avg"],
                         key="rate_type")
            st.session_state.settings["smooth"] = st.checkbox(
                "Smoothing", value=st.session_state.settings.get("smooth", True),
                key="smooth_tog",
            )

        n_analyzed = len(st.session_state.dca_results)
        if n_analyzed:
            _html(f"""
            <div class="status-bar">
              ✅ {n_analyzed} well(s) analysed &nbsp;|&nbsp;
              {len(st.session_state.eur_results)} EUR calc(s)
            </div>""")


def render_top_bar():
    C = get_C()
    n_sel = len(st.session_state.selected)
    field = st.session_state.field_name
    dot_c = C["green"] if st.session_state.data_uploaded else C["red"]
    status = "Data Loaded" if st.session_state.data_uploaded else "Data Not Loaded"
    theme = st.session_state.get("theme", "Dark")
    _html(f"""
    <div class="top-bar">
      <div style="display:flex;align-items:center;gap:16px">
        <div>
          <span class="top-bar-title">Decline Curve Analysis Estimator</span>
          <span class="top-bar-sub">Field: {field} · {n_sel} Well{'s' if n_sel!=1 else ''} Selected</span>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:20px">
        <div style="display:flex;align-items:center;gap:6px">
          <div style="width:8px;height:8px;border-radius:50%;background:{dot_c}"></div>
          <span class="top-bar-label">{status}</span>
        </div>
        <span class="top-bar-label">Unit System: <b class="top-bar-value">Field Units</b></span>
        <span class="top-bar-label">Theme: <b class="top-bar-value">{theme}</b></span>
        <span class="top-bar-label">{datetime.now().strftime('%d %b %Y  %H:%M')}</span>
      </div>
    </div>
    """)
