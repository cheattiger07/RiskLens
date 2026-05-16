import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
 
 
# ── Colour palette (mirrors the HTML dashboard) ──────────────────────────────
C_BG          = colors.HexColor("#090d12")
C_SURFACE     = colors.HexColor("#0e1520")
C_CARD        = colors.HexColor("#111926")
C_RAISED      = colors.HexColor("#1a2636")
C_BORDER      = colors.HexColor("#1e2d3d")
C_BORDER_LT   = colors.HexColor("#253545")
 
C_CYAN        = colors.HexColor("#00e5ff")
C_BLUE        = colors.HexColor("#3b82f6")
C_GREEN       = colors.HexColor("#10d48e")
C_YELLOW      = colors.HexColor("#f5c542")
C_RED         = colors.HexColor("#f04747")
C_ORANGE      = colors.HexColor("#ff8c42")
 
C_TEXT        = colors.HexColor("#e8f0f8")
C_TEXT_SEC    = colors.HexColor("#7a93b0")
C_TEXT_MUTED  = colors.HexColor("#4a6070")
C_WHITE       = colors.white
 
PAGE_W, PAGE_H = letter  # 612 x 792 pt
 
 
# ── Helpers ───────────────────────────────────────────────────────────────────
 
def _hex_alpha(hex_color: colors.HexColor, alpha: float) -> colors.Color:
    r, g, b = hex_color.red, hex_color.green, hex_color.blue
    return colors.Color(r, g, b, alpha)
 
 
def _fmt_pct(val, decimals=1):
    try:
        return f"{float(val) * 100:.{decimals}f}%"
    except Exception:
        return str(val)
 
 
def _fmt_float(val, decimals=2):
    try:
        return f"{float(val):.{decimals}f}"
    except Exception:
        return str(val)
 
 
def _fmt_dollar(val):
    try:
        return f"${float(val):,.0f}"
    except Exception:
        return str(val)
 
 
def _risk_color(metric: str, val) -> colors.Color:
    """Return traffic-light colour based on metric and value."""
    try:
        v = float(val)
    except Exception:
        return C_TEXT_SEC
 
    rules = {
        "volatility":    [(0.25, C_RED), (0.15, C_YELLOW), (0, C_GREEN)],
        "sharpe":        [(1.0, C_GREEN), (0.5, C_YELLOW), (0, C_RED)],
        "beta":          [(1.3, C_RED), (1.0, C_YELLOW), (0, C_GREEN)],
        "var":           [(-0.15, C_RED), (-0.08, C_YELLOW), (0, C_GREEN)],
        "cvar":          [(-0.20, C_RED), (-0.10, C_YELLOW), (0, C_GREEN)],
        "max_drawdown":  [(-0.30, C_RED), (-0.15, C_YELLOW), (0, C_GREEN)],
    }
    thresholds = rules.get(metric, [])
    if metric in ("volatility", "beta"):
        for thresh, colour in thresholds:
            if v > thresh:
                return colour
    else:  # lower is worse (var, cvar, drawdown, sharpe inverted)
        if metric == "sharpe":
            for thresh, colour in thresholds:
                if v >= thresh:
                    return colour
        else:
            for thresh, colour in thresholds:
                if v < thresh:
                    return colour
    return C_GREEN
 
 
def _risk_label(metric: str, val) -> str:
    color = _risk_color(metric, val)
    mapping = {
        C_GREEN:  "STABLE",
        C_YELLOW: "CAUTION",
        C_RED:    "HIGH RISK",
    }
    return mapping.get(color, "—")
 
 
# ── Drawing primitives ────────────────────────────────────────────────────────
 
def _rect(c, x, y, w, h, fill=None, stroke=None, radius=4):
    c.saveState()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(0.5)
    else:
        c.setLineWidth(0)
    c.roundRect(x, y, w, h, radius,
                fill=1 if fill else 0,
                stroke=1 if stroke else 0)
    c.restoreState()
 
 
def _text(c, x, y, txt, size=10, color=None, font="Helvetica", align="left"):
    c.saveState()
    c.setFont(font, size)
    c.setFillColor(color or C_TEXT)
    if align == "center":
        c.drawCentredString(x, y, str(txt))
    elif align == "right":
        c.drawRightString(x, y, str(txt))
    else:
        c.drawString(x, y, str(txt))
    c.restoreState()
 
 
def _hline(c, x1, y, x2, color=None, width=0.4):
    c.saveState()
    c.setStrokeColor(color or C_BORDER)
    c.setLineWidth(width)
    c.line(x1, y, x2, y)
    c.restoreState()
 
 
def _accent_bar(c, x, y, w, color, h=2):
    """Thin coloured top-bar on a card."""
    _rect(c, x, y, w, h, fill=color, radius=1)
 
 
# ── Page furniture ────────────────────────────────────────────────────────────
 
def _draw_background(c):
    _rect(c, 0, 0, PAGE_W, PAGE_H, fill=C_BG)
 
 
def _draw_header(c, generated_at: str):
    """Top header band."""
    band_h = 72
    _rect(c, 0, PAGE_H - band_h, PAGE_W, band_h, fill=C_SURFACE)
    _hline(c, 0, PAGE_H - band_h, PAGE_W, color=C_BORDER, width=0.6)
 
    # Logo mark
    lm_size = 32
    lm_x = 36
    lm_y = PAGE_H - band_h + (band_h - lm_size) / 2
    c.saveState()
    c.setFillColor(C_CYAN)
    c.roundRect(lm_x, lm_y, lm_size, lm_size, 6, fill=1, stroke=0)
    c.setFillColor(C_BG)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(lm_x + lm_size / 2, lm_y + 10, "RL")
    c.restoreState()
 
    # Brand name
    _text(c, lm_x + lm_size + 10, PAGE_H - 30, "RiskLens",
          size=20, font="Helvetica-Bold", color=C_TEXT)
    _text(c, lm_x + lm_size + 10, PAGE_H - 46,
          "Portfolio Risk & Stress Testing Engine",
          size=9, color=C_TEXT_SEC)
 
    # Right-side badge + date
    badge_x = PAGE_W - 36
    _text(c, badge_x, PAGE_H - 28, "RISK REPORT",
          size=9, font="Helvetica-Bold", color=C_CYAN, align="right")
    _text(c, badge_x, PAGE_H - 44, generated_at,
          size=8, color=C_TEXT_MUTED, align="right")
 
    # Cyan accent line under header
    _rect(c, 0, PAGE_H - band_h, PAGE_W, 2, fill=C_CYAN, radius=0)
 
 
def _draw_footer(c, page_num: int):
    foot_y = 28
    _hline(c, 36, foot_y + 14, PAGE_W - 36, color=C_BORDER)
    _text(c, 36, foot_y, "RiskLens — Confidential Risk Report",
          size=7.5, color=C_TEXT_MUTED)
    _text(c, PAGE_W - 36, foot_y, f"Page {page_num}",
          size=7.5, color=C_TEXT_MUTED, align="right")
    _text(c, PAGE_W / 2, foot_y,
          "Generated for internal use only. Not investment advice.",
          size=7, color=C_TEXT_MUTED, align="center")
 
 
def _section_label(c, x, y, label: str):
    """Uppercase section divider with accent dot."""
    _text(c, x, y, "  " + label,
          size=7.5, font="Helvetica-Bold", color=C_TEXT_MUTED)
    _rect(c, x, y - 4, 3, 3, fill=C_CYAN, radius=1)
    _hline(c, x + 8 + len(label) * 4.5, y - 2, PAGE_W - 36,
           color=C_BORDER, width=0.4)
 
 
# ── KPI card ──────────────────────────────────────────────────────────────────
 
def _kpi_card(c, x, y, w, h, label, raw_value, display_value,
              metric_key, sublabel=""):
    accent = _risk_color(metric_key, raw_value)
    status = _risk_label(metric_key, raw_value)
 
    # Card body
    _rect(c, x, y, w, h, fill=C_CARD, stroke=C_BORDER, radius=6)
 
    # Top accent bar
    _accent_bar(c, x, y + h - 2, w, accent)
 
    # Glow blob (subtle)
    c.saveState()
    c.setFillColor(_hex_alpha(accent, 0.06))
    c.circle(x + w - 10, y + h - 10, 28, fill=1, stroke=0)
    c.restoreState()
 
    # Label
    _text(c, x + 12, y + h - 18, label.upper(),
          size=7, font="Helvetica-Bold", color=C_TEXT_MUTED)
 
    # Value
    _text(c, x + 12, y + h - 38, display_value,
          size=18, font="Helvetica-Bold", color=accent)
 
    # Sublabel
    if sublabel:
        _text(c, x + 12, y + h - 52, sublabel,
              size=7, color=C_TEXT_MUTED)
 
    # Status badge
    badge_w = len(status) * 5.5 + 12
    badge_x = x + 12
    badge_y = y + 6
    c.saveState()
    c.setFillColor(_hex_alpha(accent, 0.12))
    c.roundRect(badge_x, badge_y, badge_w, 13, 6, fill=1, stroke=0)
    c.setFillColor(accent)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawString(badge_x + 6, badge_y + 3.5, status)
    c.restoreState()
 
 
# ── Stress test card ──────────────────────────────────────────────────────────
 
def _stress_card(c, x, y, w, h, title, value_str, icon, accent, note=""):
    _rect(c, x, y, w, h, fill=C_CARD, stroke=C_BORDER, radius=6)
    # Bottom accent bar
    _rect(c, x, y, w, 2, fill=accent, radius=1)
    # Glow
    c.saveState()
    c.setFillColor(_hex_alpha(accent, 0.06))
    c.circle(x + w / 2, y + h / 2, 40, fill=1, stroke=0)
    c.restoreState()
 
    _text(c, x + 14, y + h - 20, icon + "  " + title,
          size=8, font="Helvetica-Bold", color=C_TEXT_MUTED)
    _text(c, x + 14, y + h - 44, value_str,
          size=20, font="Helvetica-Bold", color=accent)
    if note:
        _text(c, x + 14, y + 14, note, size=7, color=C_TEXT_MUTED)
 
 
# ── Main generator ────────────────────────────────────────────────────────────
 
def generate_pdf_report(metrics: dict) -> str:
    """
    Generate an enhanced, design-forward PDF report for RiskLens.
 
    Parameters
    ----------
    metrics : dict
        Keys: volatility, sharpe, beta, var, cvar, max_drawdown,
              current_value, value_2008, value_covid, value_custom,
              risk_flag, schema  (all optional except the core six)
 
    Returns
    -------
    str
        Path to the generated PDF file.
    """
# create unique timestamp for every report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# output filename with timestamp
    output_path = f"static/risk_report_{timestamp}.pdf"

# ensure static folder exists
    os.makedirs("static", exist_ok=True)
 
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setTitle("RiskLens Portfolio Risk Report")
    c.setAuthor("RiskLens Engine")
    c.setSubject("Portfolio Risk & Stress Testing Report")
 
    generated_at = datetime.now().strftime("%d %b %Y, %H:%M UTC")
 
    # ── PAGE 1 ────────────────────────────────────────────────────────────────
    _draw_background(c)
    _draw_header(c, generated_at)
    _draw_footer(c, 1)
 
    cursor_y = PAGE_H - 72 - 28  # just below header
 
    # ── Report intro text ─────────────────────────────────────────────────────
    _section_label(c, 36, cursor_y, "EXECUTIVE SUMMARY")
    cursor_y -= 22
 
    intro = (
        "This report presents a quantitative risk assessment of the uploaded portfolio, "
        "including volatility analysis, risk-adjusted return metrics, tail-risk estimates, "
        "Monte Carlo simulation results, and historical stress-test scenarios."
    )
    # Word-wrap the intro manually
    c.saveState()
    c.setFont("Helvetica", 9)
    c.setFillColor(C_TEXT_SEC)
    from reportlab.lib.utils import simpleSplit
    lines = simpleSplit(intro, "Helvetica", 9, PAGE_W - 72)
    for line in lines:
        c.drawString(36, cursor_y, line)
        cursor_y -= 14
    c.restoreState()
    cursor_y -= 10
 
    # ── KPI Cards (2 rows × 3) ────────────────────────────────────────────────
    _section_label(c, 36, cursor_y, "KEY RISK METRICS")
    cursor_y -= 20
 
    kpi_data = [
        ("Volatility",    metrics.get("volatility",   0),
         _fmt_pct(metrics.get("volatility",   0)), "volatility",   "Annualised std dev"),
        ("Sharpe Ratio",  metrics.get("sharpe",       0),
         _fmt_float(metrics.get("sharpe",     0)), "sharpe",       "Risk-adjusted return"),
        ("Beta",          metrics.get("beta",         0),
         _fmt_float(metrics.get("beta",       0)), "beta",         "vs. market benchmark"),
        ("VaR (95%)",     metrics.get("var",          0),
         _fmt_pct(metrics.get("var",          0)), "var",          "Daily max expected loss"),
        ("CVaR (95%)",    metrics.get("cvar",         0),
         _fmt_pct(metrics.get("cvar",         0)), "cvar",         "Expected shortfall"),
        ("Max Drawdown",  metrics.get("max_drawdown", 0),
         _fmt_pct(metrics.get("max_drawdown", 0)), "max_drawdown", "Peak-to-trough decline"),
    ]
 
    card_w = (PAGE_W - 72 - 20) / 3
    card_h = 82
    gap = 10
    cols = 3
 
    for i, (label, raw, disp, key, sub) in enumerate(kpi_data):
        row = i // cols
        col = i % cols
        cx = 36 + col * (card_w + gap)
        cy = cursor_y - row * (card_h + gap) - card_h
        _kpi_card(c, cx, cy, card_w, card_h, label, raw, disp, key, sub)
 
    cursor_y -= 2 * (card_h + gap) + 16
 
    # ── Risk flag ─────────────────────────────────────────────────────────────
    risk_flag = metrics.get("risk_flag", "")
    if risk_flag:
        _section_label(c, 36, cursor_y, "PORTFOLIO WARNING")
        cursor_y -= 16
        flag_h = 42
        _rect(c, 36, cursor_y - flag_h, PAGE_W - 72, flag_h,
              fill=_hex_alpha(C_RED, 0.07),
              stroke=_hex_alpha(C_RED, 0.25), radius=6)
        _rect(c, 36, cursor_y - flag_h, 3, flag_h,
              fill=C_RED, radius=1)
        _text(c, 50, cursor_y - 14, "RISK FLAG DETECTED",
              size=8, font="Helvetica-Bold", color=C_RED)
        c.saveState()
        c.setFont("Helvetica", 8.5)
        c.setFillColor(C_TEXT_SEC)
        flag_lines = simpleSplit(str(risk_flag), "Helvetica", 8.5, PAGE_W - 110)
        ly = cursor_y - 28
        for fl in flag_lines[:2]:
            c.drawString(50, ly, fl)
            ly -= 12
        c.restoreState()
        cursor_y -= flag_h + 16
 
    # ── Stress testing ────────────────────────────────────────────────────────
    _section_label(c, 36, cursor_y, "STRESS TEST SCENARIOS")
    cursor_y -= 18
 
    stress_data = [
        ("2008 Financial Crash", metrics.get("value_2008",  0),
         _fmt_dollar(metrics.get("value_2008",  0)), "[2008]", C_RED,
         "Based on 2008 GFC drawdown profile"),
        ("COVID-19 Crash",       metrics.get("value_covid", 0),
         _fmt_dollar(metrics.get("value_covid", 0)), "[COVID]", C_ORANGE,
         "Based on March 2020 drawdown"),
        ("Custom Shock",         metrics.get("value_custom",0),
         _fmt_dollar(metrics.get("value_custom",0)), "[CUSTOM]", C_YELLOW,
         "User-defined shock scenario"),
    ]
 
    s_card_w = (PAGE_W - 72 - 20) / 3
    s_card_h = 80
 
    for i, (title, raw, disp, icon, accent, note) in enumerate(stress_data):
        sx = 36 + i * (s_card_w + gap)
        sy = cursor_y - s_card_h
        _stress_card(c, sx, sy, s_card_w, s_card_h,
                     title, disp, icon, accent, note)
 
    cursor_y -= s_card_h + 20
 
    # ── Current portfolio value bar ───────────────────────────────────────────
    cur_val = metrics.get("current_value", 0)
    if cur_val:
        _rect(c, 36, cursor_y - 38, PAGE_W - 72, 38,
              fill=C_RAISED, stroke=C_BORDER, radius=6)
        _text(c, 52, cursor_y - 15, "CURRENT PORTFOLIO VALUE",
              size=7.5, font="Helvetica-Bold", color=C_TEXT_MUTED)
        _text(c, 52, cursor_y - 30, _fmt_dollar(cur_val),
              size=16, font="Helvetica-Bold", color=C_CYAN)
        _text(c, PAGE_W - 52, cursor_y - 22,
              f"Schema: {metrics.get('schema', 'Auto-detected')}",
              size=8, color=C_TEXT_MUTED, align="right")
        cursor_y -= 38 + 12
 
    # ── Page 1 done ───────────────────────────────────────────────────────────
    c.showPage()
 
        # ── PAGE 2 — Monte Carlo ──────────────────────────────────────────────────
    _draw_background(c)
    _draw_header(c, generated_at)
    _draw_footer(c, 2)

    cursor_y = PAGE_H - 72 - 28

    _section_label(c, 36, cursor_y, "MONTE CARLO SIMULATION")
    cursor_y -= 18

    # Description
    mc_desc = (
        "200 portfolio paths simulated via Geometric Brownian Motion over a 252-trading-day "
        "horizon. The simulation fan illustrates the distribution of possible outcomes — wider "
        "spread = higher uncertainty. Parameters below reflect the last interactive simulation."
    )
    c.saveState()
    c.setFont("Helvetica", 9)
    c.setFillColor(C_TEXT_SEC)
    from reportlab.lib.utils import simpleSplit as _ss
    for line in _ss(mc_desc, "Helvetica", 9, PAGE_W - 72):
        c.drawString(36, cursor_y, line)
        cursor_y -= 14
    c.restoreState()
    cursor_y -= 8
    def _fmt_inr(v):
        if v >= 1e7:
            return f"₹{v/1e7:.2f}Cr"
        if v >= 1e5:
            return f"₹{v/1e5:.1f}L"
        if v >= 1e3:
            return f"₹{v/1e3:.0f}K"
        return f"₹{v:.0f}"

    # ── Simulation parameter cards (Starting Value / Horizon / Return / Vol) ──
    mc_params = [
        ("Starting Portfolio", _fmt_dollar(metrics.get("mc_start",    metrics.get("current_value", 500000)))),
        ("Time Horizon",       f"{metrics.get('mc_years', 10)} years"),
        ("Expected Return",    f"{metrics.get('mc_return', 30)}% p.a."),
        ("Volatility",         f"{metrics.get('mc_volatility', 17)}%"),
    ]

    p_card_w = (PAGE_W - 72 - 30) / 4
    p_card_h = 52
    for i, (plabel, pval) in enumerate(mc_params):
        px = 36 + i * (p_card_w + 10)
        py = cursor_y - p_card_h
        _rect(c, px, py, p_card_w, p_card_h, fill=C_CARD, stroke=C_BORDER, radius=6)
        _accent_bar(c, px, py + p_card_h - 2, p_card_w, C_CYAN)
        _text(c, px + 10, py + p_card_h - 16, plabel.upper(),
              size=6.5, font="Helvetica-Bold", color=C_TEXT_MUTED)
        _text(c, px + 10, py + p_card_h - 32, pval,
              size=13, font="Helvetica-Bold", color=C_CYAN)
    cursor_y -= p_card_h + 16

    # Metadata tags row
    tags = ["CONFIDENCE: 95%", "METHOD: GBM", "PATHS: 200", "HORIZON: 252d/yr"]
    tx = 36
    for tag in tags:
        tw = len(tag) * 5.2 + 16
        _rect(c, tx, cursor_y - 14, tw, 16,
              fill=_hex_alpha(C_CYAN, 0.07),
              stroke=_hex_alpha(C_CYAN, 0.18), radius=8)
        _text(c, tx + 8, cursor_y - 9, tag,
              size=7, font="Helvetica-Bold", color=C_TEXT_SEC)
        tx += tw + 8
    cursor_y -= 28

    # Monte Carlo image
    image_path = "static/monte_carlo.png"
    if os.path.exists(image_path):
        img_w = PAGE_W - 72
        img_h = 240
        _rect(c, 36, cursor_y - img_h - 16,
              img_w, img_h + 16,
              fill=C_CARD, stroke=C_BORDER, radius=8)
        try:
            img = Image(image_path, width=img_w - 16, height=img_h)
            img.drawOn(c, 36 + 8, cursor_y - img_h - 8)
        except Exception:
            _text(c, 36 + img_w / 2, cursor_y - img_h / 2,
                  "[Monte Carlo chart — image not found]",
                  size=10, color=C_TEXT_MUTED, align="center")
        cursor_y -= img_h + 32
    else:
        _rect(c, 36, cursor_y - 60, PAGE_W - 72, 60,
              fill=C_CARD, stroke=C_BORDER, radius=8)
        _text(c, PAGE_W / 2, cursor_y - 35,
              "Monte Carlo chart not available",
              size=10, color=C_TEXT_MUTED, align="center")
        cursor_y -= 76

    # ── Simulation output stats (6 stats mirroring the dashboard) ────────────
    _section_label(c, 36, cursor_y, "SIMULATION OUTPUT STATISTICS")
    cursor_y -= 18

    S0     = float(metrics.get("mc_start",      metrics.get("current_value", 500000)))
    mu     = float(metrics.get("mc_return",     30)) / 100
    sigma  = float(metrics.get("mc_volatility", 17)) / 100
    years  = float(metrics.get("mc_years",      10))

    import math
    drift     = (mu - 0.5 * sigma ** 2) * years
    stdev_t   = sigma * math.sqrt(years)
    median_v  = S0 * math.exp(drift)
    p95_v     = S0 * math.exp(drift + 1.645 * stdev_t)
    p5_v      = S0 * math.exp(drift - 1.645 * stdev_t)
    cagr_med  = math.pow(median_v / S0, 1 / years) - 1 if years > 0 else 0
    # Approximate prob of profit via log-normal CDF
    d1        = (math.log(S0 / S0) - drift) / stdev_t if stdev_t > 0 else 0
    # P(S_T > S0) = N(drift / stdev_t)
    z         = drift / stdev_t if stdev_t > 0 else 0
    # Simple erf-based normal CDF
    def _norm_cdf(x):
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2)))
    prob_profit = _norm_cdf(z) * 100
    worst_loss  = ((p5_v - S0) / S0) * 100

    def _fmt_inr(v):
        if v >= 1e7:  return f"₹{v/1e7:.2f}Cr"
        if v >= 1e5:  return f"₹{v/1e5:.1f}L"
        if v >= 1e3:  return f"₹{v/1e3:.0f}K"
        return f"₹{v:.0f}"

    stat_items = [
        ("Median Final Value",   _fmt_inr(median_v),          C_CYAN),
        ("95th Percentile",      _fmt_inr(p95_v),             C_GREEN),
        ("5th Percentile",       _fmt_inr(p5_v),              C_RED),
        ("Prob. of Profit",      f"{prob_profit:.1f}%",       C_CYAN),
        ("Expected CAGR",        f"{cagr_med*100:.1f}% p.a.", C_CYAN),
        ("Max Simulated Loss", f"{worst_loss:.1f}%",           C_RED)
    ]

    s_w  = (PAGE_W - 72 - 25) / 3
    s_h  = 52
    s_gap = 5
    for i, (slabel, sval, scol) in enumerate(stat_items):
        row = i // 3
        col = i % 3
        sx = 36 + col * (s_w + s_gap)
        sy = cursor_y - row * (s_h + s_gap) - s_h
        _rect(c, sx, sy, s_w, s_h, fill=C_CARD, stroke=C_BORDER, radius=6)
        # left accent pip
        _rect(c, sx, sy, 2, s_h, fill=scol, radius=1)
        _text(c, sx + 10, sy + s_h - 16, slabel.upper(),
              size=6.5, font="Helvetica-Bold", color=C_TEXT_MUTED)
        _text(c, sx + 10, sy + s_h - 32, sval,
              size=14, font="Helvetica-Bold", color=scol)

    cursor_y -= 2 * (s_h + s_gap) + 20

    # ── Interpretation table ──────────────────────────────────────────────────
    _section_label(c, 36, cursor_y, "SIMULATION INTERPRETATION")
    cursor_y -= 18
    # page break if not enough space
    if cursor_y < 180:
        c.showPage()
        _draw_background(c)
        _draw_header(c, generated_at)
        _draw_footer(c, 3)   # next page number
        cursor_y = PAGE_H - 72

    vol  = float(metrics.get("volatility", sigma))
    var_ = float(metrics.get("var",  0))
    cvar = float(metrics.get("cvar", 0))

    interp_rows = [
        ("Annualised Volatility",            _fmt_pct(vol),
         "Higher vol = wider MC path distribution",
         _risk_color("volatility", vol)),
        ("Value at Risk (95%)",              _fmt_pct(var_),
         "95% of simulated paths end above this loss",
         _risk_color("var", var_)),
        ("CVaR / Expected Shortfall (95%)",  _fmt_pct(cvar),
         "Average loss in the worst 5% of scenarios",
         _risk_color("cvar", cvar)),
        ("Median Simulated Outcome",         _fmt_inr(median_v),
         f"Based on mu={mu*100:.0f}%, sigma={sigma*100:.0f}%, T={years:.0f}yr",
         C_CYAN),
        ("Upside (P95) vs Downside (P5)",
         f"{_fmt_inr(p95_v)}  /  {_fmt_inr(p5_v)}",
         "Asymmetry of the return distribution",
         C_TEXT_SEC),
    ]

    row_h = 28
    rw    = PAGE_W - 72
    for i, (rl, rv, rn, rcol) in enumerate(interp_rows):
        ry = cursor_y - i * row_h - row_h
        _rect(c, 36, ry, rw, row_h - 2,
              fill=C_CARD if i % 2 == 0 else C_RAISED, radius=4)
        _rect(c, 36, ry, 2, row_h - 2, fill=rcol, radius=1)
        _text(c, 46, ry + row_h - 14, rl,
              size=8, font="Helvetica-Bold", color=C_TEXT)
        _text(c, 46, ry + 5, rn,
              size=7, color=C_TEXT_MUTED)
        _text(c, PAGE_W - 46, ry + row_h / 2 - 4, rv,
              size=10, font="Helvetica-Bold", color=rcol, align="right")

    cursor_y -= len(interp_rows) * row_h + 20

    # ── Disclaimer ────────────────────────────────────────────────────────────
    disc_h = 50
    _rect(c, 36, cursor_y - disc_h, PAGE_W - 72, disc_h,
          fill=_hex_alpha(C_BLUE, 0.06),
          stroke=_hex_alpha(C_BLUE, 0.2), radius=6)
    _rect(c, 36, cursor_y - disc_h, 2, disc_h, fill=C_BLUE, radius=1)
    _text(c, 50, cursor_y - 14, "DISCLAIMER",
          size=7.5, font="Helvetica-Bold", color=C_BLUE)
    disc_txt = (
        "This report is generated automatically by the RiskLens engine for informational "
        "purposes only. It does not constitute investment advice. Past performance and "
        "simulated results are not indicative of future outcomes."
    )
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(C_TEXT_SEC)
    ly = cursor_y - 26
    for line in _ss(disc_txt, "Helvetica", 8, PAGE_W - 108):
        c.drawString(50, ly, line)
        ly -= 12
    c.restoreState()

    c.showPage()
    c.save()
    return output_path