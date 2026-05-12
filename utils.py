from .theme import get_C


def kpi_card(icon, label, value, unit, delta="", delta_pos=True) -> str:
    C = get_C()
    delta_cls = "pos" if delta_pos else "neg"
    delta_html = f'<div class="kpi-delta {delta_cls}">{delta}</div>' if delta else ""
    return f"""
    <div class="kpi-card">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value-row">
        <div class="kpi-value">{value}</div>
        <div class="kpi-unit">{unit}</div>
      </div>
      {delta_html}
    </div>"""


def result_row(label, value) -> str:
    return f"""<div class="result-row">
      <span class="result-label">{label}</span>
      <span class="result-value">{value}</span>
    </div>"""


def insight_item(icon, text, color="#f59e0b") -> str:
    C = get_C()
    return f"""<div class="insight-item">
      <span style="color:{color};font-size:1.1rem">{icon}</span>
      <span style="color:{C['text']}">{text}</span>
    </div>"""
