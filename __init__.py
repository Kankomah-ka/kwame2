"""
PetroDCA Package
A professional Streamlit web application for petroleum decline curve analysis.
"""

__version__ = "1.0.0"

from .theme import get_C, inject_css, get_plotly_bg, _html
from .config import SM3_TO_BBL, SM3_TO_MSCF, BBL_TO_BOE, MSCF_TO_BOE

__all__ = [
    "get_C",
    "inject_css",
    "get_plotly_bg",
    "_html",
    "SM3_TO_BBL",
    "SM3_TO_MSCF",
    "BBL_TO_BOE",
    "MSCF_TO_BOE",
]
