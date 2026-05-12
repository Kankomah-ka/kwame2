"""
Configuration module for PetroDCA
Contains constants, unit conversions, and theme palettes
"""

# ─────────────────────────────────────────────────────────────────────────────
# UNIT CONVERSION CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
SM3_TO_BBL  = 6.28981
SM3_TO_MSCF = 0.035315
BBL_TO_BOE  = 1.0
MSCF_TO_BOE = 1 / 6.0

# ─────────────────────────────────────────────────────────────────────────────
# THEME PALETTES (Light & Dark)
# ─────────────────────────────────────────────────────────────────────────────

C_LIGHT = {
    "bg":           "#f4f7fb",
    "sidebar":      "#e9eef7",
    "sidebar_text": "#10203c",
    "sidebar_muted":"#55647e",
    "card":         "#ffffff",
    "card2":        "#eef4fb",
    "border":       "#d5dee8",
    "text":         "#0f172a",
    "heading":      "#0b1225",
    "muted":        "#4b5668",
    "input_bg":     "#ffffff",
    "green":        "#16a34a",
    "red":          "#dc2626",
    "blue":         "#2563eb",
    "orange":       "#d97706",
    "purple":       "#7c3aed",
    "teal":         "#0891b2",
    "yellow":       "#ca8a04",
    "pink":         "#db2777",
    "kpi_value":    "#0b1225",
    "result_value": "#0b1225",
    "btn_bg":       "#2563eb",
    "btn_hover":    "#1d4ed8",
    "chart_bg":     "#ffffff",
    "chart_paper":  "#ffffff",
    "chart_grid":   "#d5dee8",
    "chart_tick":   "#475569",
    "chart_text":   "#0f172a",
    "tag_bg":       "#dbeafe",
    "tag_text":     "#1e40af",
}

C_DARK = {
    "bg":           "#0d1929",
    "sidebar":      "#060e1a",
    "sidebar_text": "#e8f0fe",
    "sidebar_muted":"#7a99be",
    "card":         "#162338",
    "card2":        "#0f1d30",
    "border":       "#1e3a56",
    "text":         "#e2eaf8",
    "heading":      "#ffffff",
    "muted":        "#7a99be",
    "input_bg":     "#0f1d30",
    "green":        "#10b981",
    "red":          "#f87171",
    "blue":         "#60a5fa",
    "orange":       "#fbbf24",
    "purple":       "#a78bfa",
    "teal":         "#22d3ee",
    "yellow":       "#facc15",
    "pink":         "#f472b6",
    "kpi_value":    "#ffffff",
    "result_value": "#e2eaf8",
    "btn_bg":       "#1d4ed8",
    "btn_hover":    "#2563eb",
    "chart_bg":     "#0f1d30",
    "chart_paper":  "#0f1d30",
    "chart_grid":   "#1e3a56",
    "chart_tick":   "#7a99be",
    "chart_text":   "#e2eaf8",
    "tag_bg":       "#1e3a56",
    "tag_text":     "#93c5fd",
}

WELL_COLOURS = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444",
                "#8b5cf6", "#14b8a6", "#ec4899", "#eab308"]
