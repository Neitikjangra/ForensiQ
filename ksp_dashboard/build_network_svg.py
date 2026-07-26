"""
build_network_svg.py
---------------------
Builds the "Criminal Network Analysis" radial node diagram as raw SVG,
positioned the same way as the sample: a center node with spokes out to
associates, assets and case nodes. Purely synthetic/demo data.
"""
import math
from icons import icon_inner

ICONS = {
    "person": "user",
    "car": "car",
    "phone": "phone",
    "group": "users",
    "file": "file_text",
}


def _node_icon(name, x, y, size, color):
    """Embed one of our inline vector icons as a nested <svg>, centered at (x, y)."""
    inner = icon_inner(name if name in ("user", "car", "phone", "users", "file_text", "search") else "user")
    half = size / 2
    return (
        f'<svg x="{x - half:.1f}" y="{y - half:.1f}" width="{size}" height="{size}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg>'
    )

NODE_COLORS = {
    "person": "#3b82f6",
    "asset": "#f59e0b",
    "group": "#8b5cf6",
    "case": "#22c55e",
}


def build_network_svg(network, width=520, height=360):
    cx, cy = width / 2, height / 2 - 10
    center = network["center"]
    nodes = network["nodes"]
    n = len(nodes)
    radius = min(width, height) / 2 - 70

    parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
             f'style="width:100%;height:100%">']

    positions = []
    start_angle = -90
    for i in range(n):
        angle = math.radians(start_angle + i * (360 / n))
        x = cx + radius * math.cos(angle)
        y = cy + radius * math.sin(angle)
        positions.append((x, y))

    # spokes first (behind nodes)
    for (x, y) in positions:
        parts.append(f'<line x1="{cx}" y1="{cy}" x2="{x}" y2="{y}" '
                      f'stroke="#ef444466" stroke-width="1.5" stroke-dasharray="4 3"/>')

    # center node
    parts.append(f'''
    <circle cx="{cx}" cy="{cy}" r="34" fill="#ef444422" stroke="#ef4444" stroke-width="2"/>
    <circle cx="{cx}" cy="{cy}" r="24" fill="#1c1330"/>
    {_node_icon("search", cx, cy, 22, "#ef4444")}
    <text x="{cx}" y="{cy+52}" text-anchor="middle" fill="#eef1f7" font-size="12" font-weight="700"
          font-family="Segoe UI, sans-serif">{center['label']}</text>
    <text x="{cx}" y="{cy+66}" text-anchor="middle" fill="#9aa5bd" font-size="10"
          font-family="Segoe UI, sans-serif">{center['role']}</text>
    ''')

    for (x, y), node in zip(positions, nodes):
        color = NODE_COLORS.get(node["type"], "#3b82f6")
        icon_name = ICONS.get(node["icon"], "user")
        # keep label inside viewbox
        label_y = y + 34 if y > cy else y - 24
        parts.append(f'''
        <circle cx="{x}" cy="{y}" r="22" fill="{color}22" stroke="{color}" stroke-width="1.5"/>
        {_node_icon(icon_name, x, y, 18, color)}
        <text x="{x}" y="{label_y}" text-anchor="middle" fill="#eef1f7" font-size="10.5"
              font-family="Segoe UI, sans-serif">{node['label']}</text>
        ''')

    parts.append('</svg>')
    return "\n".join(parts)


if __name__ == "__main__":
    import json
    with open("data/real_crime_data.json") as f:
        data = json.load(f)
    svg = build_network_svg(data["network"])
    print(svg[:400], "...")
