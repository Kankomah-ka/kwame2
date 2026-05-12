import os
import sys
import streamlit as st

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    from PetroDCA.theme import inject_css
    from PetroDCA.ui import render_sidebar, render_top_bar
    from PetroDCA.pages import (
        page_dashboard,
        page_production_data,
        page_dca,
        page_eur,
        page_model_settings,
        page_insights,
        page_reports,
        page_ai_log,
    )
    from PetroDCA.session import _init_state
except ImportError:
    from .theme import inject_css
    from .ui import render_sidebar, render_top_bar
    from .pages import (
        page_dashboard,
        page_production_data,
        page_dca,
        page_eur,
        page_model_settings,
        page_insights,
        page_reports,
        page_ai_log,
    )
    from .session import _init_state


def main():
    st.set_page_config(
        page_title="PetroDCA – Decline Curve Analysis",
        page_icon="🛢️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _init_state()
    inject_css()

    render_sidebar()
    render_top_bar()

    page_map = {
        "Dashboard Overview": page_dashboard,
        "Production Data": page_production_data,
        "Decline Curve Analysis (DCA)": page_dca,
        "EUR Prediction": page_eur,
        "Model Settings": page_model_settings,
        "Field Insights": page_insights,
        "Reports & Export": page_reports,
        "AI Interaction Log": page_ai_log,
    }

    page = st.session_state.get("page", "Dashboard Overview")
    if page in page_map:
        page_map[page]()
    else:
        st.warning("Selected page is unavailable. Please choose a different menu item.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align:center;font-size:0.82rem;color:gray;'>"
        "Developed by Kwame Ankomah, Maspolic Amo Yeboah, Prince Atsirim, Ignatius Cudjoe."
        "</div>", unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
