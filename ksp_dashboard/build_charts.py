"""
build_charts.py
----------------
Builds Plotly figures for the dashboard and registers them in
CHART_REGISTRY as plain data (figure JSON), rather than emitting
auto-executing <script>Plotly.newPlot(...)</script> tags via
fig.to_html(). This matters: a chart built with fig.to_html() runs the
instant the browser parses that <script> tag, which -- for any chart
sitting inside a tab that starts hidden (display:none) -- means Plotly
measures a zero-size container and silently falls back to its default
700x450 canvas. That default-size chart then overflows its real
(smaller) column once the tab is shown, because CSS grid tracks don't
clip oversized content by default. That was the exact bug behind the
Category Breakdown chart overlapping the Alerts panel on the Crime
Analytics tab.

Instead, every chart here is just registered (id -> {data, layout,
config, minHeight}). The page's own JS (in build_dashboard.py's
TEMPLATE) explicitly measures each chart's real container box *after*
its tab becomes visible and layout has settled, then calls
Plotly.newPlot/relayout with that exact, correct pixel size. Plotly
itself never has to guess a hidden element's size.
"""
import json
import os
import plotly.graph_objects as go

BG = "#0f1729"
GRID = "#26314a"
TEXT = "#9aa5bd"
TEXT_BRIGHT = "#eef1f7"
BLUE = "#3b82f6"
PURPLE = "#8b5cf6"
GREEN = "#22c55e"
AMBER = "#f59e0b"
RED = "#ef4444"
CYAN = "#22d3ee"

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT, family="Inter, Segoe UI, sans-serif", size=12),
    margin=dict(l=8, r=8, t=8, b=8),
    autosize=True,
)

# Populated as chart-building functions run below; consumed once, at the
# end of build_dashboard.py's build(), into a single JSON blob embedded
# in the page.
CHART_REGISTRY = {}


def _register(div_id, fig, legend=False, min_height=160, margin=None):
    layout = dict(BASE_LAYOUT)
    if margin is not None:
        layout["margin"] = margin
    layout["showlegend"] = bool(legend)
    if legend:
        layout["legend"] = dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left",
                                 x=0, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(**layout)
    spec = fig.to_plotly_json()
    CHART_REGISTRY[div_id] = {
        "data": spec.get("data", []),
        "layout": spec.get("layout", {}),
        "config": {"displayModeBar": False, "responsive": False},
        "minHeight": min_height,
    }
    return (f'<div class="chart-fill" data-chart-id="{div_id}" style="--chart-min:{min_height}px">'
            f'<div id="{div_id}" class="plotly-graph-div"></div></div>')


def trend_chart(d, div_id="trend-chart"):
    """Bengaluru City reported cases by category, 2021-2023 -- real,
    sourced (see data/real/SOURCES.md), single consistent methodology."""
    t = d["trend_bengaluru"]
    fig = go.Figure()
    for s in t["series"]:
        fig.add_trace(go.Scatter(x=t["years"], y=s["values"], name=s["name"], mode="lines+markers",
                                  line=dict(color=s["color"], width=3), marker=dict(size=7)))
    fig.update_xaxes(showgrid=False, color=TEXT, dtick=1, tickformat="d")
    fig.update_yaxes(showgrid=True, gridcolor=GRID, zeroline=False, color=TEXT)
    return _register(div_id, fig, legend=True, min_height=240)


def category_donut(d, div_id="category-donut"):
    cats = d["crime_categories"]
    fig = go.Figure(go.Pie(
        labels=[c["category"] for c in cats], values=[c["count"] for c in cats],
        hole=0.62, sort=False,
        marker=dict(colors=[c["color"] for c in cats], line=dict(color=BG, width=3)),
        textinfo="none",
    ))
    total = sum(c["count"] for c in cats)
    fig.add_annotation(text=f"<b>{total:,}</b><br><span style='font-size:11px'>2024 cases</span>",
                        showarrow=False, font=dict(size=17, color=TEXT_BRIGHT))
    return _register(div_id, fig, min_height=190)


def hotspot_map(d):
    """Self-contained Karnataka outline (no CDN/topojson dependency) with
    risk bubbles sized by real 2024 district case totals, plotted as raw
    SVG (no Plotly involved, so no sizing-timing risk at all)."""
    with open(os.path.join(os.path.dirname(__file__), "karnataka_outline.json")) as f:
        outline = json.load(f)

    lons = [p[0] for p in outline]
    lats = [p[1] for p in outline]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    pad = 0.4
    min_lon -= pad; max_lon += pad; min_lat -= pad; max_lat += pad

    W, H = 460, 340

    def project(lon, lat):
        x = (lon - min_lon) / (max_lon - min_lon) * W
        y = H - (lat - min_lat) / (max_lat - min_lat) * H
        return x, y

    path_pts = [project(lo, la) for lo, la in outline]
    path_d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in path_pts) + " Z"

    districts = d["districts"]
    max_val = max(x["firs_2024"] for x in districts) or 1

    def color_for(v):
        t = v / max_val
        if t < 0.5:
            t2 = t / 0.5
            r = int(0x22 + (0xf5 - 0x22) * t2); g = int(0xc5 + (0x9e - 0xc5) * t2); b = int(0x5e + (0x0b - 0x5e) * t2)
        else:
            t2 = (t - 0.5) / 0.5
            r = int(0xf5 + (0xef - 0xf5) * t2); g = int(0x9e + (0x44 - 0x9e) * t2); b = int(0x0b + (0x44 - 0x0b) * t2)
        return f"rgb({r},{g},{b})"

    bubbles, labels = [], []
    for x in districts:
        cx, cy = project(x["lon"], x["lat"])
        r = 4 + (x["firs_2024"] / max_val) * 16
        color = color_for(x["firs_2024"])
        bubbles.append(
            f'<g><circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{color}" '
            f'fill-opacity="0.55" stroke="{color}" stroke-width="1.2"/>'
            f'<title>{x["district"]}: {x["firs_2024"]:,} cases (2024)</title></g>'
        )
        if x["firs_2024"] > max_val * 0.35:
            labels.append(
                f'<text x="{cx:.1f}" y="{cy-9:.1f}" text-anchor="middle" font-size="8.5" '
                f'fill="#c7cee2" font-family="Segoe UI, sans-serif">{x["district"]}</text>'
            )

    svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%">
      <path d="{path_d}" fill="#141b30" stroke="#3b4a6b" stroke-width="1.3"/>
      {"".join(bubbles)}
      {"".join(labels)}
    </svg>'''
    return (f'<div class="chart-fill" style="--chart-min:220px;display:flex;'
            f'align-items:center;justify-content:center">{svg}</div>')


def _hex_to_rgba(hex_color, alpha=0.15):
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def sparkline(values, color, div_id):
    fig = go.Figure(go.Scatter(
        y=values, mode="lines", line=dict(color=color, width=2.5), fill="tozeroy",
        fillcolor=_hex_to_rgba(color),
    ))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _register(div_id, fig, min_height=50, margin=dict(l=0, r=0, t=0, b=0))


def stations_bar(d):
    """Top districts ranked by real 2024 case totals."""
    stations = d["stations"]
    colors = [AMBER, "#94a3b8", "#b45309", BLUE, PURPLE]
    fig = go.Figure(go.Bar(
        x=[s["firs"] for s in stations][::-1], y=[s["station"] for s in stations][::-1],
        orientation="h", marker=dict(color=colors[:len(stations)][::-1]),
        text=[f"{s['firs']:,}" for s in stations][::-1], textposition="outside",
        textfont=dict(color=TEXT_BRIGHT),
    ))
    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=False, color=TEXT_BRIGHT)
    fig.update_layout(bargap=0.4)
    return _register("stations-bar", fig, min_height=190)


def build_all(data):
    return {
        "trend_div": trend_chart(data),
        "donut_div": category_donut(data),
        "map_div": hotspot_map(data),
        "cases_spark": sparkline(data["cases_sparkline"], PURPLE, "cases-spark"),
        "arrests_spark": sparkline(data["arrests_sparkline"], GREEN, "arrests-spark"),
        "stations_div": stations_bar(data),
    }


if __name__ == "__main__":
    with open("data/real_crime_data.json") as f:
        data = json.load(f)
    data.setdefault("cases_sparkline", [10, 12, 9, 14, 13, 15, 14])
    data.setdefault("arrests_sparkline", [4, 5, 5, 6, 6, 7, 7])
    divs = build_all(data)
    print("Built", len(divs), "chart divs;", len(CHART_REGISTRY), "registered charts")
