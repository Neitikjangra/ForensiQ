"""
build_dashboard.py
-------------------
Entry point. Loads data/real_crime_data.json (built by real_data.py from
real, sourced Karnataka State Police statistics -- see
data/real/SOURCES.md), builds all charts + the network SVG, and writes a
single self-contained HTML file.

Run:
  python3 real_data.py       # (re)builds data/real_crime_data.json
  python3 build_dashboard.py # builds ksp_crime_dashboard.html
"""
import json
from build_charts import build_all, trend_chart, category_donut, hotspot_map, CHART_REGISTRY
from build_network_svg import build_network_svg
from icons import icon

OUT_PATH = "ksp_crime_dashboard.html"


def up_arrow(size=11):
    return icon("trending_up", size=size, cls="delta-ic")


def down_arrow(size=11):
    return icon("trending_down", size=size, cls="delta-ic")


def delta_span(pct, cls_extra=""):
    """Small up/down badge for a +/- percentage."""
    arrow = up_arrow() if pct >= 0 else down_arrow()
    cls = "up" if pct >= 0 else "down"
    return f'<span class="kpi-delta {cls} {cls_extra}">{arrow} {abs(pct)}%</span>'


def tag(text, kind="neutral"):
    """A panel-title badge, color-coded so real vs. illustrative data is
    scannable at a glance rather than something you have to read to catch."""
    cls = {"real": "tag tag-real", "fictional": "tag tag-fictional"}.get(kind, "tag")
    return f'<span class="{cls}">{text}</span>'


def build():
    with open("data/real_crime_data.json") as f:
        d = json.load(f)

    charts = build_all(d)
    trend_div_2 = trend_chart(d, div_id="trend-chart-2")
    donut_div_2 = category_donut(d, div_id="category-donut-2")
    map_div_2 = hotspot_map(d)
    network_svg = build_network_svg(d["network"])
    k = d["kpis"]
    meta = d["meta"]

    # ---------------- KPI row (all 6 grounded in real, cited data) ------
    kpi_defs = [
        ("Total Cases Registered", f"{k['total_cases']:,}", k["total_cases_yoy_pct"], "vs 2022",
         "file_text", "#3b82f6", f"{k['total_cases_year']} \u00b7 statewide"),
        ("Cyber Crime Cases", f"{k['cyber_crime_2024']:,}", k["cyber_crime_growth_pct"], "vs 2022",
         "cpu", "#22d3ee", "2024 \u00b7 statewide"),
        ("Detection Rate (sample)", f"{d['blended_detection_rate']}%", None, None,
         "check_circle", "#22c55e", "2023 \u00b7 Bengaluru sample"),
        ("Crimes vs Women & Children", f"{k['women_children_2024']:,}", None, None,
         "alert_circle", "#ef4444", "2024 \u00b7 statewide"),
        ("Districts Tracked", str(k["districts_tracked"]), None, None,
         "map_pin", "#8b5cf6", "Full state coverage"),
        ("High-Volume Districts", str(k["high_volume_districts"]), None, None,
         "flame", "#f59e0b", "Above median \u00b7 2024"),
    ]

    def kpi_card(label, value, delta, delta_label, icon_name, color, caption):
        if delta is not None:
            sub = delta_span(delta) + f'<span class="kpi-cap"> {delta_label}</span><div class="kpi-cap-line">{caption}</div>'
        else:
            sub = f'<span class="kpi-cap">{caption}</span>'
        return f'''
        <div class="kpi-card">
          <div class="kpi-icon" style="background:{color}22;color:{color}">{icon(icon_name, size=18)}</div>
          <div>
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {sub}
          </div>
        </div>'''

    kpi_row = "\n".join(kpi_card(*c) for c in kpi_defs)

    # ---------------- today cards (explicitly-labeled daily estimates) --
    today_cards = f'''
    <div class="panel today-card">
      <div class="today-head"><span>Cases Registered</span><span class="today-tag">Daily avg. estimate</span></div>
      <div class="today-value">{d['cases_registered_today']:,}</div>
      <div class="today-note">{icon('info', size=11) if False else ''}Derived from the 2023 published annual total \u00b7 not a live feed</div>
      {charts['cases_spark']}
    </div>
    <div class="panel today-card">
      <div class="today-head"><span>Arrests</span><span class="today-tag">Daily avg. estimate</span></div>
      <div class="today-value">{d['arrests_today']:,}</div>
      <div class="today-note">Derived from a {d['blended_detection_rate']}% sample detection rate \u00b7 not a live feed</div>
      {charts['arrests_spark']}
    </div>'''

    # ---------------- 3 bottom mini stat cards (all real) ---------------
    ma = d["most_active_district"]
    mc = d["most_common_category"]
    fg = d["fastest_growing"]
    stat_cards = f'''
    <div class="mini-card">
      <div class="mini-icon" style="background:#f59e0b22;color:#f59e0b">{icon('star', size=17)}</div>
      <div><div class="mini-label">Most Active District</div>
      <div class="mini-value">{ma['district']}</div>
      <div class="mini-sub">{ma['firs']:,} cases \u00b7 2024</div></div>
    </div>
    <div class="mini-card">
      <div class="mini-icon" style="background:#3b82f622;color:#3b82f6">{icon('tag', size=17)}</div>
      <div><div class="mini-label">Most Common Category</div>
      <div class="mini-value">{mc['category']}</div>
      <div class="mini-sub">{mc['count']:,} cases \u00b7 2024</div></div>
    </div>
    <div class="mini-card">
      <div class="mini-icon" style="background:#22d3ee22;color:#22d3ee">{icon('trending_up', size=17)}</div>
      <div><div class="mini-label">Fastest-Growing</div>
      <div class="mini-value">{fg['label']}</div>
      <div class="mini-sub up">{up_arrow()} {fg['pct']}% \u00b7 {fg['detail']}</div></div>
    </div>'''

    # ---------------- category legend rows --------------------------
    total_cat = sum(c["count"] for c in d["crime_categories"])
    cat_rows = "\n".join(
        f'''<div class="legend-row">
              <span class="legend-dot" style="background:{c['color']}"></span>
              <span class="legend-label">{c['category']}</span>
              <span class="legend-val">{c['count']:,} ({c['count']/total_cat*100:.1f}%)</span>
            </div>'''
        for c in d["crime_categories"]
    )

    # ---------------- alerts (right sidebar + Alerts tab) -----------
    alert_colors = {"spike": "#ef4444", "offender": "#f59e0b", "cyber": "#22d3ee", "safety": "#a855f7"}
    alert_icon_names = {"spike": "alert_triangle", "offender": "lock", "cyber": "cpu", "safety": "alert_circle"}

    def alert_item(a):
        color = alert_colors.get(a["kind"], "#3b82f6")
        icon_name = alert_icon_names.get(a["kind"], "alert_circle")
        return f'''
        <div class="alert-item">
          <div class="alert-icon" style="background:{color}22;color:{color}">{icon(icon_name, size=15)}</div>
          <div>
            <div class="alert-title" style="color:{color}">{a['title']}</div>
            <div class="alert-text">{a['text']}</div>
            <div class="alert-time">{a['minutes_ago']} mins ago</div>
          </div>
        </div>'''

    alerts_sidebar = "\n".join(alert_item(a) for a in d["alerts"][:4])
    alerts_full = "\n".join(alert_item(a) for a in d["alerts"])

    # ---------------- most wanted (clearly fictional) ------------------
    def wanted_item(p):
        return f'''
        <div class="wanted-item">
          <div class="wanted-avatar">{p['initials']}</div>
          <div>
            <div class="wanted-name">{p['name']}</div>
            <div class="wanted-charge">{p['charges']}</div>
            <div class="wanted-reward">Reward: \u20b9{p['reward']:,}</div>
          </div>
        </div>'''

    wanted_html = "\n".join(wanted_item(p) for p in d["most_wanted"])

    # ---------------- recent FIRs (clearly fictional examples) ---------
    def fir_item(f):
        return f'''
        <div class="fir-item">
          <div class="fir-no">FIR No: {f['fir_no']}</div>
          <div class="fir-type">{f['crime_type']} - {f['station']}</div>
          <div class="fir-time">{f['minutes_ago']} mins ago</div>
        </div>'''

    fir_html = "\n".join(fir_item(f) for f in d["fir_log"])
    fir_search_rows = "\n".join(
        f'''<tr><td>{f['fir_no']}</td><td>{f['crime_type']}</td><td>{f['station']}</td>
             <td>{f['minutes_ago']} min ago</td></tr>'''
        for f in d["fir_log"]
    )

    # ---------------- district table (real) -----------------------------
    def yoy_cell(v):
        if v is None:
            return '<td class="muted">n/a</td>'
        arrow = up_arrow(10) if v >= 0 else down_arrow(10)
        cls = "up" if v >= 0 else "down"
        return f'<td class="{cls}">{arrow} {abs(v)}%</td>'

    district_rows_html = "\n".join(
        f'''<tr><td>{r['district']}</td><td>{r['firs_2024']:,}</td>
             <td>{r['firs_2023']:,}</td>{yoy_cell(r['yoy_2022_23_pct'])}
             <td>{r['top_category_2024']}</td></tr>'''
        for r in d["districts"]
    )

    # ---------------- AI copilot suggestions ---------------------------
    def suggestion_item(text, icon_name):
        return f'''
        <div class="suggestion-item">
          <div class="suggestion-icon">{icon(icon_name, size=16)}</div>
          <div>
            <div class="suggestion-text">{text}</div>
            <a class="suggestion-link" href="javascript:void(0)" onclick="gotoTab('predictive')">View Details &rarr;</a>
          </div>
        </div>'''

    icons_cycle = ["cpu", "trending_up", "flame"]
    suggestions_html = "\n".join(
        suggestion_item(t, icons_cycle[i % len(icons_cycle)])
        for i, t in enumerate(d["copilot_suggestions"])
    )

    # ---------------- predictive intelligence --------------------------
    pred = d["predictive"]
    predictive_block = f'''
    <div class="predictive-body">
      <div class="pred-label">Next {pred['horizon_days']} Days \u2014 Illustrative Projection</div>
      <div class="pred-text">Elevated likelihood of increase in</div>
      <div class="pred-highlight">{' &amp; '.join(pred['top_categories'])}</div>
      <div class="pred-text">across {', '.join(pred['districts'])}</div>
      <span class="risk-badge">{pred['risk_level']}</span>
      <div class="conf-row"><span>Confidence Score</span><b>{pred['confidence_score']}%</b></div>
      <div class="conf-bar"><div class="conf-fill" style="width:{pred['confidence_score']}%"></div></div>
      <div class="pred-footnote">{pred['note']}</div>
    </div>'''

    # ---------------- Vehicles & Assets tab -----------------------------
    vehicle_rows = "\n".join(
        f'''<tr><td>{v['id']}</td><td>{v['type']}</td>
             <td><span class="status-pill status-{v['status'].lower().replace(' ', '-')}">{v['status']}</span></td>
             <td>{v['district']}</td><td>{v['linked_fir']}</td></tr>'''
        for v in d["vehicles"]
    )

    # ---------------- Department Directory (User Management) -----------
    directory_rows = "\n".join(
        f'''<tr><td>{p['name']}</td><td>{p['rank']}</td><td>{p['station']}</td>
             <td>{p['badge']}</td><td><span class="status-pill status-{p['status'].lower().replace(' ', '-')}">{p['status']}</span></td></tr>'''
        for p in d["directory"]
    )

    # ---------------- Print report (Reports & PDF) ----------------------
    print_district_rows = "\n".join(
        f"<tr><td>{r['district']}</td><td>{r['firs_2024']:,}</td><td>{r['firs_2023']:,}</td>"
        f"<td>{'' if r['yoy_2022_23_pct'] is None else str(r['yoy_2022_23_pct'])+'%'}</td></tr>"
        for r in d["districts"][:15]
    )
    print_category_rows = "\n".join(
        f"<tr><td>{c['category']}</td><td>{c['count']:,}</td><td>{c['count']/total_cat*100:.1f}%</td></tr>"
        for c in d["crime_categories"]
    )
    print_report_html = f'''
    <div id="printReport">
      <h1>Karnataka State Police &mdash; Crime Intelligence Summary</h1>
      <p class="pr-meta">Generated {meta['generated_at']} &middot; Source: {meta['source_name']}</p>
      <p class="pr-note">{meta['note']}</p>
      <h2>Key Figures</h2>
      <table class="pr-table">
        <tr><td>Total Cases Registered ({k['total_cases_year']})</td><td>{k['total_cases']:,}</td></tr>
        <tr><td>YoY Change (2022&rarr;2023)</td><td>{k['total_cases_yoy_pct']}%</td></tr>
        <tr><td>Cyber Crime Cases (2024)</td><td>{k['cyber_crime_2024']:,}</td></tr>
        <tr><td>Cyber Crime Growth (2022&rarr;2023, Bengaluru)</td><td>{k['cyber_crime_growth_pct']}%</td></tr>
        <tr><td>Crimes vs Women &amp; Children (2024)</td><td>{k['women_children_2024']:,}</td></tr>
        <tr><td>Districts Tracked</td><td>{k['districts_tracked']}</td></tr>
      </table>
      <h2>Top Districts by Case Volume (2024 snapshot)</h2>
      <table class="pr-table pr-table-wide">
        <thead><tr><th>District</th><th>2024 Cases</th><th>2023 Total</th><th>YoY 22&rarr;23</th></tr></thead>
        <tbody>{print_district_rows}</tbody>
      </table>
      <h2>Category Breakdown (2024, statewide)</h2>
      <table class="pr-table pr-table-wide">
        <thead><tr><th>Category</th><th>Cases</th><th>Share</th></tr></thead>
        <tbody>{print_category_rows}</tbody>
      </table>
      <p class="pr-footer">Individual case records, named suspects, and the network diagram are illustrative
      examples and are intentionally excluded from this report.</p>
    </div>'''

    # ---------------- sidebar nav (icons instead of emoji) --------------
    nav_defs = [
        ("dashboard", "grid", "Dashboard", None),
        ("copilot", "sparkles", "AI Copilot", ("new", "New")),
        ("chatdata", "message_square", "Chat with Data", None),
        ("analytics", "bar_chart", "Crime Analytics", None),
        ("map", "map_pin", "Crime Map", None),
        ("network", "share", "Network Analysis", None),
        ("predictive", "trending_up", "Predictive Intelligence", None),
        ("fir", "folder_search", "FIR &amp; Case Search", None),
        ("persons", "users", "Accused &amp; Persons", None),
        ("vehicles", "car", "Vehicles &amp; Assets", None),
        ("reports", "file_text", "Reports &amp; PDF", None),
        ("alerts", "bell", "Alerts &amp; Notifications", ("count", str(len(d["alerts"])))),
        ("audit", "clock", "Audit Trail", None),
        ("users", "users", "Department Directory", None),
        ("settings", "settings", "Settings", None),
    ]

    def nav_item(tab, icon_name, label, badge, active=False):
        cls = "nav-item active" if active else "nav-item"
        badge_html = ""
        if badge:
            kind, val = badge
            badge_html = (f'<span class="new-tag">{val}</span>' if kind == "new"
                           else f'<span class="count-tag">{val}</span>')
        return (f'<div class="{cls}" data-tab="{tab}" onclick="gotoTab(\'{tab}\')">'
                f'{icon(icon_name, size=16)} {label}{badge_html}</div>')

    nav_html = "\n".join(
        nav_item(tab, ic, label, badge, active=(tab == "dashboard"))
        for tab, ic, label, badge in nav_defs
    )

    # ---------------- profile menu ---------------------------------------
    profile_menu_html = f'''
        <div class="profile-menu-item" onclick="gotoTab('settings')">{icon('user', size=14)} Profile</div>
        <div class="profile-menu-item" onclick="gotoTab('settings')">{icon('settings', size=14)} Settings</div>
        <div class="profile-menu-item" onclick="performLogout()">{icon('log_out', size=14)} Logout</div>'''

    # ---------------- settings tab: officer profile + project info + sources
    settings_tab_html = f'''
    <div class="grid-2">
      <div class="panel">
        <div class="panel-title"><h3>Officer Profile</h3><span class="tag">Editable</span></div>
        <div class="profile-form">
          <div class="avatar-upload-row">
            <div class="avatar-upload" onclick="document.getElementById('avatarFileInput').click()" title="Click to change photo">
              <div id="avatarPreview" class="avatar-lg">IA</div>
              <div class="avatar-edit-badge">{icon('image', size=12)}</div>
            </div>
            <input type="file" id="avatarFileInput" accept="image/*" style="display:none" onchange="handleAvatarUpload(event)">
            <div>
              <div class="field-label">Profile Photo</div>
              <div class="field-hint">Click the avatar to upload a photo.</div>
              <button type="button" class="link-btn" style="width:auto;padding:6px 12px;margin-top:6px;" onclick="removeAvatar()">Remove Photo</button>
            </div>
          </div>

          <div class="field-grid">
            <label class="field"><span>Full Name</span><input id="pf-name" type="text" oninput="liveSyncTopbar()" placeholder="Inspector Arjun"></label>
            <label class="field"><span>{icon('id', size=13)} Badge / Employee ID</span><input id="pf-badge" type="text" placeholder="KSP-88213"></label>
            <label class="field"><span>Rank / Role</span><input id="pf-role" type="text" oninput="liveSyncTopbar()" placeholder="Investigating Officer"></label>
            <label class="field"><span>{icon('building', size=13)} Department / Station</span><input id="pf-dept" type="text" placeholder="Bengaluru City CCB"></label>
            <label class="field"><span>{icon('mail', size=13)} Email</span><input id="pf-email" type="email" placeholder="officer@ksp.gov.in"></label>
            <label class="field"><span>{icon('phone', size=13)} Phone</span><input id="pf-phone" type="tel" placeholder="+91 90000 00000"></label>
          </div>
          <label class="field field-wide"><span>Bio / Notes</span>
            <textarea id="pf-bio" rows="3" placeholder="A short note about your role on this project..."></textarea>
          </label>

          <div class="settings-actions">
            <button type="button" class="ask-btn" style="width:auto;padding:9px 18px;" onclick="saveSettings()">{icon('save', size=14)} Save Profile</button>
            <button type="button" class="link-btn" style="width:auto;padding:9px 18px;" onclick="resetSettings()">Reset to Default</button>
            <span id="profileSaveMsg" class="save-msg"></span>
          </div>
        </div>
      </div>

      <div class="panel">
        <div class="panel-title"><h3>Project Information</h3><span class="tag">Attach reference docs</span></div>
        <label class="field field-wide"><span>Project Notes</span>
          <textarea id="proj-notes" rows="5" placeholder="Describe the project, jurisdiction, data sources, or any context worth keeping with this dashboard..."></textarea>
        </label>

        <div class="upload-dropzone" id="projDropzone"
             onclick="document.getElementById('projFileInput').click()"
             ondragover="event.preventDefault(); this.classList.add('drag')"
             ondragleave="this.classList.remove('drag')"
             ondrop="handleProjectFileDrop(event)">
          {icon('upload', size=22)}
          <div><b>Click to upload</b> or drag a file here</div>
          <div class="field-hint">.txt, .md, .csv, .json or .log &middot; up to 1&nbsp;MB each</div>
        </div>
        <input type="file" id="projFileInput" multiple accept=".txt,.md,.csv,.json,.log" style="display:none" onchange="handleProjectFileUpload(event)">

        <div id="attachmentList" class="attachment-list"></div>

        <div class="settings-actions">
          <button type="button" class="ask-btn" style="width:auto;padding:9px 18px;" onclick="saveSettings()">{icon('save', size=14)} Save Project Info</button>
          <span id="projectSaveMsg" class="save-msg"></span>
        </div>
      </div>
    </div>

    <div class="panel" style="margin-top:14px">
      <div class="panel-title"><h3>Data Sources &amp; Methodology</h3></div>
      <p class="src-p">{meta['note']}</p>
      <p class="src-p"><b>Primary source:</b> {meta['source_name']} &mdash;
        <a href="{meta['source_url']}" target="_blank" rel="noopener">{meta['source_url']}</a></p>
      <p class="src-p">Full per-figure citations are in <code>data/real/SOURCES.md</code> in the project download.</p>
    </div>

    <div class="panel" style="margin-top:14px">
      <div class="panel-title"><h3>Where Settings Are Saved</h3></div>
      <p class="src-p">
        Profile and project details save to this workspace's storage when the dashboard is opened as a Claude
        artifact, so they'll be here next time you open it. If that storage isn't available (for example, if
        this is opened as a plain downloaded HTML file), everything above still works &mdash; it's just kept
        for the current browser session instead.
      </p>
    </div>'''

    settings_js = SETTINGS_JS_TEMPLATE.replace(
        "__ICON_PAPERCLIP__", icon('paperclip', size=14)
    ).replace(
        "__ICON_X__", icon('x', size=12)
    )

    chart_registry_json = json.dumps(CHART_REGISTRY)
    charts_js = CHARTS_JS_TEMPLATE.replace("__CHART_SPECS_JSON__", chart_registry_json)

    import plotly.offline as pyo
    plotly_js = pyo.get_plotlyjs()

    html = TEMPLATE.format(
        CSS=CSS,
        PLOTLY_JS=plotly_js,
        SETTINGS_JS=settings_js,
        CHARTS_JS=charts_js,
        DATA_TABS_JS=DATA_TABS_JS,
        generated_at=meta["generated_at"],
        n_alerts=len(d["alerts"]),
        n_firs=len(d["fir_log"]),
        total_cases=f"{k['total_cases']:,}",
        total_cases_year=k["total_cases_year"],
        districts_tracked=k["districts_tracked"],
        source_name=meta["source_name"],
        brand_icon=icon("shield", size=19),
        menu_icon=icon("menu", size=20),
        bell_icon=icon("bell", size=18),
        chevron_icon=icon("chevron_down", size=11),
        sos_icon=icon("phone", size=14),
        copilot_ask_icon=icon("message_square", size=14),
        filter_icon=icon("filter", size=13),
        print_icon=icon("print", size=15),
        check_icon=icon("check_circle", size=12),
        flag_icon=icon("flag", size=12),
        sos_modal_icon=icon("phone", size=26),
        sos_call_icon=icon("phone", size=14),
        nav_html=nav_html,
        profile_menu_html=profile_menu_html,
        settings_tab_html=settings_tab_html,
        kpi_row=kpi_row,
        today_cards=today_cards,
        stat_cards=stat_cards,
        cat_rows=cat_rows,
        alerts_sidebar=alerts_sidebar,
        alerts_full=alerts_full,
        wanted_html=wanted_html,
        fir_html=fir_html,
        suggestions_html=suggestions_html,
        predictive_block=predictive_block,
        predictive_block_2=predictive_block,
        trend_div=charts["trend_div"],
        trend_div_2=trend_div_2,
        donut_div=charts["donut_div"],
        donut_div_2=donut_div_2,
        map_div=charts["map_div"],
        map_div_2=map_div_2,
        stations_div=charts["stations_div"],
        network_svg=network_svg,
        network_svg_2=network_svg,
        fir_search_rows=fir_search_rows,
        district_rows_html=district_rows_html,
        vehicle_rows=vehicle_rows,
        directory_rows=directory_rows,
        print_report_html=print_report_html,
        data_json=json.dumps(d),
    )

    with open(OUT_PATH, "w") as f:
        f.write(html)
    print("Wrote", OUT_PATH)

TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Karnataka State Police &mdash; Crime Intelligence AI</title>
<script>{PLOTLY_JS}</script>
<style>
{CSS}
</style>
</head>
<body>

<div class="header-stack">
<div class="topbar">
  <div class="brand">
    <button type="button" class="hamburger-btn" onclick="toggleSidebar()" aria-label="Open menu">{menu_icon}</button>
    <div class="brand-badge">{brand_icon}</div>
    <div>
      <div class="brand-title">KARNATAKA STATE POLICE</div>
      <div class="brand-sub">CRIME <span>INTELLIGENCE AI</span></div>
      <div class="brand-tag">Talk to Crime Data</div>
    </div>
  </div>

  <div class="search-wrap">
    <input id="globalSearch" class="search-input" placeholder="Ask anything about crime data... (try 'cyber' or a district name)" oninput="onSearch(this.value)">
    <div id="searchResults" class="search-results"></div>
  </div>

  <div class="topbar-right">
    <div class="pill lang">English {chevron_icon}</div>
    <div class="bell-wrap" onclick="gotoTab('alerts')">
      {bell_icon}<span class="badge">{n_alerts}</span>
    </div>
    <div class="profile-wrap" onclick="toggleProfileMenu()">
      <div class="avatar" id="topbarAvatar">IA</div>
      <div>
        <div class="profile-name" id="topbarName">Inspector Arjun</div>
        <div class="profile-role" id="topbarRole">Investigating Officer</div>
      </div>
      <div id="profileMenu" class="profile-menu">
        {profile_menu_html}
      </div>
    </div>
  </div>
</div>

<div class="data-legend">
  <span class="legend-badge legend-real">{check_icon} Real, sourced data</span>
  <span class="legend-badge legend-fictional">{flag_icon} Illustrative example</span>
  <span class="legend-note">Watch for these tags throughout &middot; full citations in Settings &rarr; Data Sources</span>
</div>
</div>

<div class="layout">
  <div class="sidebar-backdrop" id="sidebarBackdrop" onclick="closeSidebar()"></div>
  <div class="sidebar" id="sidebar">
    {nav_html}

    <div class="quick-stats">
      <div class="qs-title">Quick Statistics</div>
      <div class="qs-row"><span>Total Cases ({total_cases_year})</span><b>{total_cases}</b></div>
      <div class="qs-row"><span>Districts Tracked</span><b>{districts_tracked}</b></div>
      <div class="qs-row"><span>Data Source</span><b class="qs-src">KSP / OpenCity</b></div>
      <div class="qs-row"><span>Latest Published Year</span><b>2024</b></div>
    </div>
    <div class="sos-btn" onclick="openSOSModal()">{sos_icon} Emergency SOS</div>
  </div>

  <div class="main">

    <!-- ============ DASHBOARD TAB ============ -->
    <div class="tab-content active" id="tab-dashboard">
      <div class="kpi-grid">{kpi_row}</div>

      <div class="grid-3">
        <div class="panel">
          <div class="panel-title"><h3>Crime Trend Overview</h3><span class="tag tag-real">Bengaluru, 2021&ndash;23</span></div>
          {trend_div}
        </div>
        <div class="panel">
          <div class="panel-title"><h3>Crime Hotspot Map (Karnataka)</h3><span class="tag tag-real">2024 snapshot</span></div>
          {map_div}
        </div>
        <div class="panel">
          <div class="panel-title"><h3>Top Crime Categories</h3><span class="tag tag-real">2024</span></div>
          {donut_div}
          <div class="legend-list">{cat_rows}</div>
        </div>
      </div>

      <div class="grid-today">
        {today_cards}
      </div>

      <div class="mini-row">{stat_cards}</div>

      <div class="grid-3">
        <div class="panel">
          <div class="panel-title"><h3>Criminal Network Analysis</h3><span class="tag tag-fictional">Illustrative example</span></div>
          <div class="chart-fill" style="--chart-min:230px">{network_svg}</div>
          <button class="link-btn" onclick="gotoTab('network')">Explore Network &rarr;</button>
        </div>
        <div class="panel">
          <div class="panel-title"><h3>Predictive Intelligence</h3><span class="tag tag-fictional">Illustrative projection</span></div>
          {predictive_block}
          <button class="link-btn" onclick="gotoTab('predictive')">View Prediction Details</button>
        </div>
        <div class="panel">
          <div class="panel-title"><h3>AI Copilot Suggestions</h3><span class="tag new-tag">New</span></div>
          {suggestions_html}
          <button class="ask-btn" onclick="gotoTab('copilot')">{copilot_ask_icon} Ask AI Copilot</button>
        </div>
      </div>
    </div>

    <!-- ============ AI COPILOT TAB ============ -->
    <div class="tab-content" id="tab-copilot">
      <div class="panel chat-panel">
        <div class="panel-title"><h3>AI Copilot</h3><span class="tag ai-mode-badge" id="copilotModeBadge">Checking AI connection&hellip;</span></div>
        <div id="copilotLog" class="chat-log"></div>
        <div class="chat-input-row">
          <input id="copilotInput" class="chat-input" placeholder="Ask about cyber crime, a district, categories, forecasts..." onkeydown="if(event.key==='Enter') sendCopilot()">
          <button class="chat-send" onclick="sendCopilot()">Send</button>
        </div>
      </div>
    </div>

    <!-- ============ CHAT WITH DATA TAB ============ -->
    <div class="tab-content" id="tab-chatdata">
      <div class="panel chat-panel">
        <div class="panel-title"><h3>Chat with Data</h3><span class="tag ai-mode-badge" id="chatdataModeBadge">Checking AI connection&hellip;</span></div>
        <div id="chatdataLog" class="chat-log"></div>
        <div class="chat-input-row">
          <input id="chatdataInput" class="chat-input" placeholder="e.g. 'total cases' or 'Tumakuru'" onkeydown="if(event.key==='Enter') sendChatData()">
          <button class="chat-send" onclick="sendChatData()">Send</button>
        </div>
      </div>
    </div>

    <!-- ============ CRIME ANALYTICS TAB ============ -->
    <div class="tab-content" id="tab-analytics">
      <div class="grid-2">
        <div class="panel">
          <div class="panel-title"><h3>Crime Trend by Category</h3><span class="tag tag-real">Bengaluru, 2021&ndash;23</span></div>
          {trend_div_2}
        </div>
        <div class="panel">
          <div class="panel-title"><h3>Category Breakdown</h3><span class="tag tag-real">2024</span></div>
          {donut_div_2}
          <div class="legend-list">{cat_rows}</div>
        </div>
      </div>
      <div class="panel">
        <div class="panel-title"><h3>Top Districts by Case Volume</h3><span class="tag tag-real">2024 snapshot, real KSP data</span></div>
        {stations_div}
      </div>
    </div>

    <!-- ============ CRIME MAP TAB ============ -->
    <div class="tab-content" id="tab-map">
      <div class="panel">
        <div class="panel-title"><h3>Karnataka Crime Hotspot Map</h3><span class="tag tag-real">Bubble size = 2024 case volume (real KSP data)</span></div>
        {map_div_2}
      </div>
    </div>

    <!-- ============ NETWORK TAB ============ -->
    <div class="tab-content" id="tab-network">
      <div class="panel">
        <div class="panel-title"><h3>Criminal Network Analysis</h3><span class="tag tag-fictional">Fictional illustrative example</span></div>
        <div class="chart-fill" style="--chart-min:420px">{network_svg_2}</div>
      </div>
    </div>

    <!-- ============ PREDICTIVE TAB ============ -->
    <div class="tab-content" id="tab-predictive">
      <div class="panel" style="max-width:520px">
        <div class="panel-title"><h3>Predictive Intelligence</h3><span class="tag tag-fictional">Illustrative projection</span></div>
        {predictive_block_2}
      </div>
    </div>

    <!-- ============ FIR SEARCH TAB ============ -->
    <div class="tab-content" id="tab-fir">
      <div class="panel">
        <div class="panel-title"><h3>FIR &amp; Case Search</h3><span class="tag tag-fictional">{n_firs} illustrative example records</span></div>
        <input class="table-filter" placeholder="Filter by crime type or station..." oninput="filterTable('firTable', this.value)">
        <table id="firTable">
          <thead><tr><th>FIR No</th><th>Crime Type</th><th>Station</th><th>Logged</th></tr></thead>
          <tbody>{fir_search_rows}</tbody>
        </table>
      </div>
      <div class="panel" style="margin-top:14px">
        <div class="panel-title"><h3>District-wise Case Data</h3><span class="tag tag-real">Real KSP figures</span></div>
        <input class="table-filter" placeholder="Filter by district or category..." oninput="filterTable('districtTable', this.value)">
        <table id="districtTable">
          <thead><tr><th>District</th><th>2024 Cases <span class="th-note">(major heads)</span></th><th>2023 Total <span class="th-note">(IPC+SLL)</span></th><th>YoY 22&rarr;23</th><th>Top Category (2024)</th></tr></thead>
          <tbody>{district_rows_html}</tbody>
        </table>
      </div>
    </div>

    <!-- ============ ACCUSED & PERSONS TAB ============ -->
    <div class="tab-content" id="tab-persons">
      <div class="panel">
        <div class="panel-title"><h3>Most Wanted</h3><span class="tag tag-fictional">Fictional illustrative entries</span></div>
        {wanted_html}
      </div>
    </div>

    <!-- ============ VEHICLES & ASSETS TAB ============ -->
    <div class="tab-content" id="tab-vehicles">
      <div class="panel">
        <div class="panel-title"><h3>Vehicle Theft</h3><span class="tag tag-real">Real KSP figure, Bengaluru City 2023</span></div>
        <p class="src-p">Bengaluru City Police recorded <b>5,909 motor vehicle thefts</b> in 2023, of which
        1,437 were recovered (a 24.3% recovery rate) &mdash; up from 5,062 reported in 2022. Source:
        Bengaluru Crime Data 2023, via OpenCity.</p>
      </div>
      <div class="panel" style="margin-top:14px">
        <div class="panel-title"><h3>Flagged Vehicles</h3><span class="tag tag-fictional">Illustrative example records</span></div>
        <input class="table-filter" placeholder="Filter by plate, type, status, or district..." oninput="filterTable('vehicleTable', this.value)">
        <table id="vehicleTable">
          <thead><tr><th>Plate No.</th><th>Type</th><th>Status</th><th>District</th><th>Linked FIR</th></tr></thead>
          <tbody>{vehicle_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- ============ REPORTS TAB ============ -->
    <div class="tab-content" id="tab-reports">
      <div class="panel">
        <div class="panel-title"><h3>Reports &amp; PDF</h3></div>
        <p class="src-p">Export a summary report built from this dashboard's real, sourced figures (key
        totals, top districts, category breakdown). Your browser's print dialog lets you save it as a PDF
        or send it to a printer.</p>
        <button type="button" class="ask-btn" style="width:auto;padding:9px 18px;" onclick="exportReport()">{print_icon} Print / Save as PDF</button>
      </div>
      <div class="panel" style="margin-top:14px">
        <div class="panel-title"><h3>Report Preview</h3></div>
        {print_report_html}
      </div>
    </div>

    <!-- ============ ALERTS TAB ============ -->
    <div class="tab-content" id="tab-alerts">
      <div class="panel">
        <div class="panel-title"><h3>All Alerts &amp; Notifications</h3></div>
        {alerts_full}
      </div>
    </div>

    <!-- ============ AUDIT TRAIL (real session log) ============ -->
    <div class="tab-content" id="tab-audit">
      <div class="panel">
        <div class="panel-title"><h3>Audit Trail</h3><span class="tag tag-real">Live log of this session's actions</span></div>
        <input class="table-filter" placeholder="Filter by action..." oninput="filterTable('auditTable', this.value)">
        <table id="auditTable">
          <thead><tr><th>Time</th><th>Action</th><th>Detail</th></tr></thead>
          <tbody id="auditTableBody"></tbody>
        </table>
        <div class="field-hint" style="margin-top:10px">This tracks real interactions during your current
        session (tab switches, searches, chats, saves, exports). It resets on reload &mdash; no backend log
        storage is wired up in this build.</div>
      </div>
    </div>

    <!-- ============ DEPARTMENT DIRECTORY (was User Management) ======= -->
    <div class="tab-content" id="tab-users">
      <div class="panel">
        <div class="panel-title"><h3>Department Directory</h3><span class="tag tag-fictional">Illustrative example personnel</span></div>
        <input class="table-filter" placeholder="Filter by name, rank, or station..." oninput="filterTable('directoryTable', this.value)">
        <table id="directoryTable">
          <thead><tr><th>Name</th><th>Rank</th><th>Station</th><th>Badge</th><th>Status</th></tr></thead>
          <tbody>{directory_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- ============ SETTINGS (live) ============ -->
    <div class="tab-content" id="tab-settings">
      {settings_tab_html}
    </div>

    <div class="footer">
      Data as of {generated_at} &middot; Source: {source_name} &middot; Secure. Intelligent. Proactive.
      Together for a Safer Karnataka.
    </div>
  </div>

  <div class="right-panel">
    <div class="panel">
      <div class="panel-title"><h3>Real-time Alerts</h3><a href="javascript:void(0)" onclick="gotoTab('alerts')" class="view-all">View All</a></div>
      {alerts_sidebar}
    </div>
    <div class="panel">
      <div class="panel-title"><h3>Most Wanted</h3><a href="javascript:void(0)" onclick="gotoTab('persons')" class="view-all">View All</a></div>
      {wanted_html}
    </div>
    <div class="panel">
      <div class="panel-title"><h3>Recent FIRs</h3><a href="javascript:void(0)" onclick="gotoTab('fir')" class="view-all">View All</a></div>
      {fir_html}
    </div>
  </div>
</div>

<div class="modal-backdrop" id="sosModalBackdrop" onclick="closeSOSModal()"></div>
<div class="sos-modal" id="sosModal" role="dialog" aria-modal="true">
  <div class="sos-modal-icon">{sos_modal_icon}</div>
  <h3>Call India's Emergency Number?</h3>
  <p>This places a real call to <b>112</b>, India's national emergency helpline (police, fire,
  ambulance). It does <b>not</b> send your location, this dashboard's data, or any case context to
  KSP &mdash; it's simply a normal phone call, same as dialing it yourself.</p>
  <div class="sos-modal-actions">
    <button type="button" class="link-btn" onclick="closeSOSModal()">Cancel</button>
    <button type="button" class="ask-btn sos-call-btn" onclick="confirmSOSCall()">{sos_call_icon} Call 112 Now</button>
  </div>
</div>

<script>
const DATA = {data_json};

{CHARTS_JS}

function gotoTab(tab) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  const target = document.getElementById('tab-' + tab);
  if (target) target.classList.add('active');
  const navItem = document.querySelector('.nav-item[data-tab="' + tab + '"]');
  if (navItem) navItem.classList.add('active');
  window.scrollTo({{top:0, behavior:'smooth'}});
  document.getElementById('profileMenu').style.display = 'none';
  closeSidebar();
  renderChartsIn(target);
  if (typeof logAudit === 'function' && tab !== 'audit') logAudit('Viewed tab', navItem ? navItem.textContent.trim() : tab);
}}

function toggleProfileMenu() {{
  const m = document.getElementById('profileMenu');
  m.style.display = (m.style.display === 'block') ? 'none' : 'block';
}}
document.addEventListener('click', function(e) {{
  if (!e.target.closest('.profile-wrap')) {{
    document.getElementById('profileMenu').style.display = 'none';
  }}
}});

function toggleSidebar() {{
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebarBackdrop').classList.toggle('open');
}}
function closeSidebar() {{
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebarBackdrop').classList.remove('open');
}}

function syncHeaderHeight() {{
  const stack = document.querySelector('.header-stack');
  if (!stack) return;
  document.documentElement.style.setProperty('--header-h', stack.getBoundingClientRect().height + 'px');
}}
window.addEventListener('resize', syncHeaderHeight);

// ---------------- Emergency SOS: a REAL call to India's 112 helpline -----
// This is intentionally NOT a fake "dispatch integration." No static page
// can reach KSP's internal dispatch system. What it *can* honestly do is
// place a real phone call to India's actual national emergency number,
// after an explicit confirmation step (so it can never fire by accident).
function openSOSModal() {{
  document.getElementById('sosModalBackdrop').classList.add('open');
  document.getElementById('sosModal').classList.add('open');
  logAudit('Emergency SOS opened', 'Awaiting confirmation before dialing');
}}
function closeSOSModal() {{
  document.getElementById('sosModalBackdrop').classList.remove('open');
  document.getElementById('sosModal').classList.remove('open');
}}
function confirmSOSCall() {{
  logAudit('Emergency SOS confirmed', 'Dialing 112 (India national emergency number)');
  closeSOSModal();
  window.location.href = 'tel:112';
}}
document.addEventListener('keydown', function (e) {{
  if (e.key === 'Escape') closeSOSModal();
}});

// ---------------- Logout: really resets the session (no fake backend) ----
function performLogout() {{
  document.getElementById('profileMenu').style.display = 'none';
  resetSettings();
  gotoTab('dashboard');
  logAudit('Logged out', 'Session profile reset to default');
}}

function onSearch(q) {{
  const box = document.getElementById('searchResults');
  q = q.trim().toLowerCase();
  if (!q) {{ box.style.display='none'; box.innerHTML=''; return; }}
  let results = [];
  DATA.districts.forEach(d => {{
    if (d.district.toLowerCase().includes(q)) {{
      results.push({{label: d.district + ' \u2014 ' + d.firs_2024.toLocaleString() + ' cases (2024)', tab:'map'}});
    }}
  }});
  DATA.crime_categories.forEach(c => {{
    if (c.category.toLowerCase().includes(q)) {{
      results.push({{label: c.category + ' \u2014 ' + c.count.toLocaleString() + ' cases (2024)', tab:'analytics'}});
    }}
  }});
  DATA.fir_log.forEach(f => {{
    if (f.fir_no.toLowerCase().includes(q) || f.crime_type.toLowerCase().includes(q)) {{
      results.push({{label: 'FIR ' + f.fir_no + ' \u2014 ' + f.crime_type + ' (example)', tab:'fir'}});
    }}
  }});
  results = results.slice(0, 6);
  if (results.length === 0) {{
    box.innerHTML = '<div class="search-empty">No matches</div>';
  }} else {{
    box.innerHTML = results.map(r =>
      '<div class="search-item" onclick="gotoTab(\'' + r.tab + '\'); logAudit(\'Search\', ' + JSON.stringify(q) + ')">' + r.label + '</div>'
    ).join('');
  }}
  box.style.display = 'block';
}}

function filterTable(tableId, q) {{
  q = q.trim().toLowerCase();
  const rows = document.querySelectorAll('#' + tableId + ' tbody tr');
  rows.forEach(r => {{
    r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
  }});
}}

// ---------------- canned copilot / chat-with-data engine (real data) ----
function answerQuery(q) {{
  q = q.toLowerCase();
  const k = DATA.kpis;
  if (q.includes('cyber')) {{
    return 'Cyber crime is the fastest-growing category: ' + k.cyber_crime_2024.toLocaleString() +
           ' cases statewide in 2024. In Bengaluru it grew ' + k.cyber_crime_growth_pct + '% from 2022 to 2023 (' +
           DATA.fastest_growing.detail + '). Source: KSP / OpenCity.';
  }}
  if (q.includes('theft') || q.includes('burglary')) {{
    const c = DATA.crime_categories.find(c => c.category.includes('Theft'));
    return 'Theft & Burglary recorded ' + c.count.toLocaleString() + ' cases statewide in 2024, the largest single category.';
  }}
  if (q.includes('women') || q.includes('child') || q.includes('safety') || q.includes('pocso')) {{
    return 'Crimes against women: ' + k.women_safety_cases_2024.toLocaleString() +
           ' cases in 2024. Combined with crimes against children (POCSO): ' + k.women_children_2024.toLocaleString() + ' cases statewide.';
  }}
  if (q.includes('most active') || q.includes('highest crime') || q.includes('top district')) {{
    return DATA.most_active_district.district + ' recorded ' + DATA.most_active_district.firs.toLocaleString() +
           ' cases in 2024, the highest of any district (real KSP data).';
  }}
  if (q.includes('detection') || q.includes('conviction') || q.includes('solved')) {{
    return 'The sample detection rate (Bengaluru, 2023, across property/cyber/women categories) is ' +
           DATA.blended_detection_rate + '%. This varies a lot by category \u2014 it is not a single statewide figure.';
  }}
  if (q.includes('total') && (q.includes('case') || q.includes('fir') || q.includes('crime'))) {{
    return 'Total cases registered statewide in ' + k.total_cases_year + ': ' + k.total_cases.toLocaleString() +
           ' (+' + k.total_cases_yoy_pct + '% vs 2022). Source: Karnataka State Police via OpenCity.';
  }}
  if (q.includes('vehicle')) {{
    return 'Bengaluru City recorded 5,909 motor vehicle thefts in 2023 (1,437 recovered) \u2014 see the Vehicles & Assets tab.';
  }}
  for (const d of DATA.districts) {{
    if (q.includes(d.district.toLowerCase())) {{
      const yoy = d.yoy_2022_23_pct === null ? 'n/a' : (d.yoy_2022_23_pct + '%');
      return d.district + ': ' + d.firs_2024.toLocaleString() + ' cases (2024 snapshot), ' +
             d.firs_2023.toLocaleString() + ' total in 2023, YoY 2022\u21922023: ' + yoy +
             '. Top category: ' + d.top_category_2024 + '.';
    }}
  }}
  if (q.includes('forecast') || q.includes('predict')) {{
    return 'Illustrative ' + DATA.predictive.horizon_days + '-day projection: elevated likelihood in ' +
           DATA.predictive.top_categories.join(' & ') + ' across ' + DATA.predictive.districts.join(', ') +
           ' (confidence ' + DATA.predictive.confidence_score + '%). This is a demo projection, not a statistical model.';
  }}
  if (q.includes('source') || q.includes('real') || q.includes('data from')) {{
    return DATA.meta.note;
  }}
  const fallback = DATA.copilot_suggestions[Math.floor(Math.random()*DATA.copilot_suggestions.length)];
  return "I couldn't find an exact match. Here's a related insight: " + fallback;
}}

function appendChat(logId, sender, text) {{
  const log = document.getElementById(logId);
  const div = document.createElement('div');
  div.className = 'chat-bubble ' + sender;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}}

function sendCopilot() {{ sendChat('copilotInput', 'copilotLog', 'AI Copilot', 'copilotModeBadge'); }}
function sendChatData() {{ sendChat('chatdataInput', 'chatdataLog', 'Chat with Data', 'chatdataModeBadge'); }}

// ---------------- Live AI (Claude) with automatic, honest fallback -------
// This dashboard tries a real Claude call first. That succeeds with zero
// setup when viewed as a Claude artifact (Anthropic proxies the request);
// it fails harmlessly everywhere else (downloaded file, self-hosted, no
// backend/API key) and we fall back to a fast offline assistant that's
// still grounded in the real KSP data below -- never a broken chat box.
let liveAIAvailable = null; // null = not yet tested, true/false once known

function buildAIDataContext() {{
  const k = DATA.kpis;
  const cats = DATA.crime_categories.map(c => c.category + ': ' + c.count.toLocaleString()).join('; ');
  const topDistricts = DATA.districts.slice(0, 10)
    .map(d => d.district + ': ' + d.firs_2024.toLocaleString() + ' cases (2024)').join('; ');
  return [
    'You are the AI assistant embedded in a Karnataka State Police Crime Intelligence dashboard.',
    'Source: ' + DATA.meta.source_name + ' (' + DATA.meta.source_url + ').',
    DATA.meta.note,
    'Statewide headline: total cases ' + k.total_cases_year + ' = ' + k.total_cases.toLocaleString() +
      ' (+' + k.total_cases_yoy_pct + '% vs 2022). Cyber crime 2024 = ' + k.cyber_crime_2024.toLocaleString() +
      ' (+' + k.cyber_crime_growth_pct + '% Bengaluru 2022\u219223). Crimes vs women & children 2024 = ' +
      k.women_children_2024.toLocaleString() + '. Districts tracked = ' + k.districts_tracked + '.',
    'Category breakdown, 2024 statewide: ' + cats + '.',
    'Top districts by 2024 case volume: ' + topDistricts + '.',
    'Anything about individual FIR numbers, named "most wanted" suspects, the network diagram, vehicle plate records, or personnel directory entries is FICTIONAL illustrative example data, not real \u2014 say so plainly if asked about those.',
    'Answer the question conversationally, grounded ONLY in the facts above. If the answer needs information not given here, say so honestly rather than guessing. Keep it under 80 words unless asked for more detail.',
  ].join(' ');
}}

async function callLiveAI(query) {{
  const prompt = buildAIDataContext() + '\\n\\nUser question: ' + query;
  const response = await fetch('https://api.anthropic.com/v1/messages', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{
      model: 'claude-sonnet-4-6',
      max_tokens: 1000,
      messages: [{{ role: 'user', content: prompt }}],
    }}),
  }});
  if (!response.ok) throw new Error('live-ai-unavailable');
  const data = await response.json();
  const text = (data.content || []).filter(b => b.type === 'text').map(b => b.text).join('\\n').trim();
  if (!text) throw new Error('live-ai-empty-response');
  return text;
}}

function setAIModeBadges(isLive) {{
  const label = isLive ? '\u25cf Live AI \u2014 Claude Sonnet' : '\u25cb Offline Assistant \u2014 rule-based, real KSP data';
  ['copilotModeBadge', 'chatdataModeBadge'].forEach(function (id) {{
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = label;
    el.classList.toggle('live', !!isLive);
  }});
}}

async function sendChat(inputId, logId, src, badgeId) {{
  const input = document.getElementById(inputId);
  const q = input.value.trim();
  if (!q) return;
  appendChat(logId, 'user', q);
  input.value = '';
  logAudit(src + ' query', q);
  const thinking = appendChat(logId, 'bot thinking', '\u2026');

  if (liveAIAvailable !== false) {{
    try {{
      const answer = await callLiveAI(q);
      liveAIAvailable = true;
      setAIModeBadges(true);
      thinking.textContent = answer;
      thinking.className = 'chat-bubble bot';
      logAudit(src + ' answered', 'Live AI');
      return;
    }} catch (e) {{
      liveAIAvailable = false;
      setAIModeBadges(false);
    }}
  }}
  setTimeout(function () {{
    thinking.textContent = answerQuery(q);
    thinking.className = 'chat-bubble bot';
    logAudit(src + ' answered', 'Offline assistant');
  }}, 300);
}}

async function primeAIMode() {{
  try {{
    await callLiveAI('ping');
    liveAIAvailable = true;
  }} catch (e) {{
    liveAIAvailable = false;
  }}
  setAIModeBadges(liveAIAvailable);
}}

window.addEventListener('DOMContentLoaded', () => {{
  syncHeaderHeight();
  appendChat('copilotLog', 'bot', "Hi Inspector Arjun \u2014 ask me about cyber crime, categories, districts, or forecasts. I try live Claude AI first and fall back to a fast offline assistant automatically \u2014 both grounded in real KSP data.");
  appendChat('chatdataLog', 'bot', "Ask me a question about the dataset, e.g. 'total cases' or a district name.");
  renderChartsIn(document.getElementById('tab-dashboard'));
  loadSettings();
  logAudit('Session started', 'Dashboard loaded');
  primeAIMode();
}});

{DATA_TABS_JS}

{SETTINGS_JS}
</script>

</body>
</html>
"""

CHARTS_JS_TEMPLATE = r"""
// ---------------- Chart rendering: measure-then-relayout, robust ----------
// Charts are registered as plain data (id -> {data, layout, config,
// minHeight}) rather than auto-executing scripts, so Plotly never has to
// guess the size of a container that's still hidden (display:none) --
// which is what previously caused a chart to fall back to Plotly's
// default 700x450 canvas and overflow its real, smaller column. Instead
// we explicitly measure the container after its tab is shown and layout
// has settled (double requestAnimationFrame), and hand Plotly that exact
// pixel size.
const CHART_SPECS = __CHART_SPECS_JSON__;
const _renderedCharts = new Set();

function _sizeAndRenderChart(divId) {
  const spec = CHART_SPECS[divId];
  const wrap = document.querySelector('[data-chart-id="' + divId + '"]');
  const el = document.getElementById(divId);
  if (!spec || !wrap || !el || !window.Plotly) return;
  const box = wrap.getBoundingClientRect();
  const w = Math.max(Math.round(box.width), 1);
  const h = Math.max(Math.round(box.height), 40);
  if (w < 20 || h < 20) return; // not laid out yet -- next resize/tab-switch will retry
  const layout = Object.assign({}, spec.layout, {width: w, height: h, autosize: false});
  if (!_renderedCharts.has(divId)) {
    Plotly.newPlot(divId, spec.data, layout, spec.config);
    _renderedCharts.add(divId);
  } else {
    Plotly.relayout(divId, {width: w, height: h});
  }
}

function renderChartsIn(container) {
  if (!container) return;
  const wraps = container.querySelectorAll('[data-chart-id]');
  if (!wraps.length) return;
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      wraps.forEach(function (wrap) {
        _sizeAndRenderChart(wrap.getAttribute('data-chart-id'));
      });
    });
  });
}

let _chartResizeTimer = null;
window.addEventListener('resize', function () {
  clearTimeout(_chartResizeTimer);
  _chartResizeTimer = setTimeout(function () {
    renderChartsIn(document.querySelector('.tab-content.active'));
  }, 150);
});
"""

DATA_TABS_JS = r"""
// ---------------- Audit trail: a real log of this session's actions ------
const auditEvents = [];
function logAudit(action, detail) {
  try {
    const row = {time: new Date(), action: action, detail: detail || ''};
    auditEvents.unshift(row);
    if (auditEvents.length > 300) auditEvents.pop();
    renderAudit();
  } catch (e) {}
}
function renderAudit() {
  const body = document.getElementById('auditTableBody');
  if (!body) return;
  body.innerHTML = auditEvents.map(function (e) {
    const t = e.time.toLocaleTimeString();
    return '<tr><td>' + t + '</td><td>' + escapeHtml(e.action) + '</td><td>' + escapeHtml(e.detail) + '</td></tr>';
  }).join('');
}

// ---------------- Reports & PDF: real browser print/export ---------------
function exportReport() {
  logAudit('Exported report', 'Print / Save as PDF');
  gotoTab('reports');
  setTimeout(function () { window.print(); }, 300);
}
"""

SETTINGS_JS_TEMPLATE = r"""
// ---------------- Settings: Officer Profile + Project Info ----------------
const ICON_PAPERCLIP = '__ICON_PAPERCLIP__';
const ICON_X = '__ICON_X__';

const DEFAULT_PROFILE = { name: 'Inspector Arjun', badge: '', role: 'Investigating Officer', dept: '', email: '', phone: '', bio: '', avatar: '' };
let profileState = Object.assign({}, DEFAULT_PROFILE);
let projectState = { notes: '', attachments: [] };

function hasStorage() {
  return typeof window.storage !== 'undefined' && window.storage && typeof window.storage.get === 'function';
}

async function loadSettings() {
  if (hasStorage()) {
    try {
      const res = await window.storage.get('ksp_settings');
      if (res && res.value) {
        const parsed = JSON.parse(res.value);
        if (parsed.profile) profileState = Object.assign({}, DEFAULT_PROFILE, parsed.profile);
        if (parsed.project) projectState = Object.assign({ notes: '', attachments: [] }, parsed.project);
      }
    } catch (e) {
      // nothing saved yet, or storage isn't available in this context -- use defaults
    }
  }
  applyProfileToUI();
  applyProjectToUI();
}

function initials(name) {
  if (!name) return 'IA';
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return 'IA';
  const a = parts[0][0] || '';
  const b = (parts[1] ? parts[1][0] : parts[0][1]) || '';
  return (a + b).toUpperCase() || 'IA';
}

function renderAvatar() {
  const el = document.getElementById('avatarPreview');
  if (!el) return;
  el.innerHTML = profileState.avatar
    ? '<img src="' + profileState.avatar + '" alt="Profile photo">'
    : initials(profileState.name);
}

function syncTopbarProfile() {
  document.getElementById('topbarName').textContent = profileState.name || 'Inspector Arjun';
  document.getElementById('topbarRole').textContent = profileState.role || 'Investigating Officer';
  const av = document.getElementById('topbarAvatar');
  av.innerHTML = profileState.avatar
    ? '<img src="' + profileState.avatar + '" alt="Profile photo">'
    : initials(profileState.name);
}

function liveSyncTopbar() {
  document.getElementById('topbarName').textContent = document.getElementById('pf-name').value.trim() || 'Inspector Arjun';
  document.getElementById('topbarRole').textContent = document.getElementById('pf-role').value.trim() || 'Investigating Officer';
  if (!profileState.avatar) {
    document.getElementById('topbarAvatar').innerHTML = initials(document.getElementById('pf-name').value);
  }
}

function applyProfileToUI() {
  document.getElementById('pf-name').value = profileState.name || '';
  document.getElementById('pf-badge').value = profileState.badge || '';
  document.getElementById('pf-role').value = profileState.role || '';
  document.getElementById('pf-dept').value = profileState.dept || '';
  document.getElementById('pf-email').value = profileState.email || '';
  document.getElementById('pf-phone').value = profileState.phone || '';
  document.getElementById('pf-bio').value = profileState.bio || '';
  renderAvatar();
  syncTopbarProfile();
}

function collectProfileFromForm() {
  profileState = {
    name: document.getElementById('pf-name').value.trim() || DEFAULT_PROFILE.name,
    badge: document.getElementById('pf-badge').value.trim(),
    role: document.getElementById('pf-role').value.trim() || DEFAULT_PROFILE.role,
    dept: document.getElementById('pf-dept').value.trim(),
    email: document.getElementById('pf-email').value.trim(),
    phone: document.getElementById('pf-phone').value.trim(),
    bio: document.getElementById('pf-bio').value.trim(),
    avatar: profileState.avatar || '',
  };
}

function handleAvatarUpload(evt) {
  const file = evt.target.files && evt.target.files[0];
  evt.target.value = '';
  if (!file) return;
  if (!file.type.startsWith('image/')) {
    showMsg('profileSaveMsg', 'Please choose an image file.', true);
    return;
  }
  const reader = new FileReader();
  reader.onload = function (e) {
    const img = new Image();
    img.onload = function () {
      const size = 128;
      const canvas = document.createElement('canvas');
      canvas.width = size; canvas.height = size;
      const ctx = canvas.getContext('2d');
      const scale = Math.max(size / img.width, size / img.height);
      const w = img.width * scale, h = img.height * scale;
      ctx.drawImage(img, (size - w) / 2, (size - h) / 2, w, h);
      profileState.avatar = canvas.toDataURL('image/jpeg', 0.85);
      renderAvatar();
      syncTopbarProfile();
      if (typeof logAudit === 'function') logAudit('Updated profile photo', file.name);
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

function removeAvatar() {
  profileState.avatar = '';
  renderAvatar();
  syncTopbarProfile();
}

const PROJECT_ALLOWED_EXT = ['txt', 'md', 'csv', 'json', 'log'];
const PROJECT_MAX_BYTES = 1024 * 1024;

function handleProjectFileUpload(evt) {
  processProjectFiles(evt.target.files);
  evt.target.value = '';
}

function handleProjectFileDrop(evt) {
  evt.preventDefault();
  evt.currentTarget.classList.remove('drag');
  processProjectFiles(evt.dataTransfer.files);
}

function processProjectFiles(fileList) {
  Array.from(fileList || []).forEach(function (file) {
    const ext = (file.name.split('.').pop() || '').toLowerCase();
    if (PROJECT_ALLOWED_EXT.indexOf(ext) === -1) {
      showMsg('projectSaveMsg', '"' + file.name + '" skipped \u2014 only .txt, .md, .csv, .json, .log files are supported.', true);
      return;
    }
    if (file.size > PROJECT_MAX_BYTES) {
      showMsg('projectSaveMsg', '"' + file.name + '" skipped \u2014 file is larger than 1MB.', true);
      return;
    }
    const reader = new FileReader();
    reader.onload = function (e) {
      projectState.attachments.push({
        name: file.name,
        size: file.size,
        content: e.target.result,
        addedAt: new Date().toISOString()
      });
      renderAttachments();
      if (typeof logAudit === 'function') logAudit('Attached project file', file.name);
    };
    reader.readAsText(file);
  });
}

function removeAttachment(idx) {
  projectState.attachments.splice(idx, 1);
  renderAttachments();
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  return (bytes / 1024).toFixed(1) + ' KB';
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, function (c) {
    return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
  });
}

function renderAttachments() {
  const box = document.getElementById('attachmentList');
  if (!box) return;
  if (!projectState.attachments.length) {
    box.innerHTML = '<div class="field-hint">No files attached yet.</div>';
    return;
  }
  box.innerHTML = projectState.attachments.map(function (a, i) {
    return '<div class="attachment-row">' + ICON_PAPERCLIP +
      '<span class="att-name" title="' + escapeHtml(a.name) + '">' + escapeHtml(a.name) + '</span>' +
      '<span class="att-size">' + formatFileSize(a.size) + '</span>' +
      '<button type="button" onclick="removeAttachment(' + i + ')" title="Remove">' + ICON_X + '</button>' +
      '</div>';
  }).join('');
}

function applyProjectToUI() {
  document.getElementById('proj-notes').value = projectState.notes || '';
  renderAttachments();
}

function showMsg(id, text, isErr) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = 'save-msg' + (isErr ? ' err' : '');
  clearTimeout(el._t);
  el._t = setTimeout(function () { el.textContent = ''; }, 4000);
}

async function saveSettings() {
  collectProfileFromForm();
  projectState.notes = document.getElementById('proj-notes').value.trim();
  syncTopbarProfile();
  const payload = JSON.stringify({ profile: profileState, project: projectState });
  if (hasStorage()) {
    try {
      await window.storage.set('ksp_settings', payload);
      showMsg('profileSaveMsg', 'Saved to your workspace.');
      showMsg('projectSaveMsg', 'Saved to your workspace.');
      if (typeof logAudit === 'function') logAudit('Saved settings', 'Persisted to workspace storage');
      return;
    } catch (e) {
      // fall through to the session-only notice below
    }
  }
  showMsg('profileSaveMsg', 'Saved for this browser session.');
  showMsg('projectSaveMsg', 'Saved for this browser session.');
  if (typeof logAudit === 'function') logAudit('Saved settings', 'Session only (no persistent storage)');
}

async function resetSettings() {
  profileState = Object.assign({}, DEFAULT_PROFILE);
  projectState = { notes: '', attachments: [] };
  applyProfileToUI();
  applyProjectToUI();
  if (hasStorage()) {
    try { await window.storage.delete('ksp_settings'); } catch (e) {}
  }
  showMsg('profileSaveMsg', 'Reset to default.');
  if (typeof logAudit === 'function') logAudit('Reset settings', 'Back to default profile');
}
"""

CSS = r"""
:root {
  --bg: #0a0f1e; --panel: #131b2e; --panel-2: #0e1524; --border: #232c42;
  --text: #9aa5bd; --text-bright: #eef1f7;
  --blue:#3b82f6; --purple:#8b5cf6; --amber:#f59e0b; --green:#22c55e; --red:#ef4444; --cyan:#22d3ee;
  --header-h: 99px;
}
* { box-sizing: border-box; min-width: 0; }
body { margin:0; background:var(--bg); color:var(--text-bright); font-family:'Segoe UI',Inter,-apple-system,sans-serif; }
.icon { display:inline-block; vertical-align:-3px; flex-shrink:0; }

/* slim, subtle scrollbars (Chrome/Edge/Safari) so any internal-overflow
   area never looks like a stray glitch-bar */
::-webkit-scrollbar { width:8px; height:8px; }
::-webkit-scrollbar-track { background:transparent; }
::-webkit-scrollbar-thumb { background:#2a344e; border-radius:8px; }
::-webkit-scrollbar-thumb:hover { background:#374266; }
* { scrollbar-width: thin; scrollbar-color: #2a344e transparent; }

.topbar { display:flex; align-items:center; justify-content:space-between; gap:16px; padding:12px 20px; background:var(--panel); border-bottom:1px solid var(--border);}
.header-stack { position:sticky; top:0; z-index:50; }

/* Persistent, unmissable legend: real (sourced) vs illustrative data */
.data-legend { display:flex; align-items:center; gap:14px; padding:7px 20px; background:var(--panel-2); border-bottom:1px solid var(--border); font-size:11px; flex-wrap:wrap; }
.legend-badge { display:inline-flex; align-items:center; gap:5px; font-weight:600; padding:3px 10px; border-radius:12px; }
.legend-real { background:#22c55e1c; color:var(--green); }
.legend-fictional { background:#f59e0b1c; color:var(--amber); }
.legend-note { color:#5a6584; }
.tag-real, .tag.tag-real { border-color:#22c55e55; color:var(--green); background:#22c55e14; }
.tag-fictional, .tag.tag-fictional { border-color:#f59e0b55; color:var(--amber); background:#f59e0b14; }
.ai-mode-badge { transition:color .2s, background .2s; }
.ai-mode-badge.live { color:var(--green); background:#22c55e18; border-color:#22c55e55; }

.brand { display:flex; gap:10px; align-items:center; flex-shrink:0;}
.hamburger-btn { display:none; align-items:center; justify-content:center; width:32px; height:32px; background:none; border:1px solid var(--border); border-radius:8px; color:var(--text-bright); cursor:pointer; padding:0; flex-shrink:0;}
.hamburger-btn:hover { background:#1c2740; }
.sidebar-backdrop { display:none; }
.brand-badge { width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,var(--blue),var(--purple));display:flex;align-items:center;justify-content:center;color:#fff; flex-shrink:0;}
.brand-title { font-size:11px; color:var(--text); letter-spacing:.5px; }
.brand-sub { font-size:15px; font-weight:700; }
.brand-sub span { color:var(--blue); }
.brand-tag { font-size:10.5px; color:var(--text); }
.search-wrap { flex:1; max-width:480px; position:relative; }
.search-input { width:100%; background:var(--panel-2); border:1px solid var(--border); border-radius:10px; padding:9px 14px; color:var(--text-bright); font-size:13px; }
.search-input:focus { outline:1px solid var(--blue); }
.search-results { position:absolute; top:110%; left:0; right:0; background:var(--panel-2); border:1px solid var(--border); border-radius:10px; display:none; overflow:hidden; z-index:60;}
.search-item { padding:9px 14px; font-size:12.5px; cursor:pointer; border-bottom:1px solid var(--border); }
.search-item:hover { background:#1c2740; }
.search-item:last-child { border-bottom:none;}
.search-empty { padding:9px 14px; font-size:12px; color:var(--text);}
.topbar-right { display:flex; align-items:center; gap:16px; flex-shrink:0;}
.pill.lang { background:var(--panel-2); border:1px solid var(--border); border-radius:20px; padding:6px 14px; font-size:12.5px; display:inline-flex; align-items:center; gap:5px;}
.bell-wrap { position:relative; cursor:pointer; display:inline-flex; align-items:center; flex-shrink:0;}
.badge { position:absolute; top:-6px; right:-10px; background:var(--red); color:#fff; font-size:10px; border-radius:10px; padding:1px 5px; }
.profile-wrap { display:flex; align-items:center; gap:8px; cursor:pointer; position:relative; flex-shrink:0;}
.avatar { width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,var(--blue),var(--purple)); display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700; overflow:hidden; flex-shrink:0;}
.avatar img { width:100%; height:100%; object-fit:cover; }
.profile-name { font-size:12.5px; font-weight:600; white-space:nowrap; }
.profile-role { font-size:10.5px; color:var(--text); white-space:nowrap; }
.profile-menu { display:none; position:absolute; top:120%; right:0; background:var(--panel-2); border:1px solid var(--border); border-radius:10px; min-width:150px; overflow:hidden; z-index:60;}
.profile-menu-item { padding:9px 14px; font-size:12.5px; cursor:pointer; display:flex; align-items:center; gap:8px;}
.profile-menu-item:hover { background:#1c2740; }

.layout { display:flex; align-items:flex-start; }
.sidebar { width:230px; flex-shrink:0; background:var(--panel); border-right:1px solid var(--border); padding:14px 10px; position:sticky; top:var(--header-h, 99px); height:calc(100vh - var(--header-h, 99px)); overflow-y:auto;}
.nav-item { display:flex; align-items:center; gap:9px; padding:9px 12px; border-radius:9px; font-size:13.5px; color:var(--text); cursor:pointer; margin-bottom:2px;}
.nav-item:hover { background:#1c2740; }
.nav-item.active { background:linear-gradient(90deg,#3b82f633,transparent); color:var(--text-bright); border-left:3px solid var(--blue); }
.new-tag { background:var(--green); color:#06240f; font-size:9.5px; padding:1px 6px; border-radius:8px; margin-left:auto; font-weight:700;}
.count-tag { background:var(--red); color:#fff; font-size:9.5px; padding:1px 6px; border-radius:8px; margin-left:auto; }
.quick-stats { margin-top:16px; border-top:1px solid var(--border); padding-top:12px; }
.qs-title { font-size:11px; text-transform:uppercase; color:#5a6584; margin-bottom:8px; letter-spacing:.5px;}
.qs-row { display:flex; justify-content:space-between; gap:8px; font-size:12px; padding:5px 4px; color:var(--text);}
.qs-row b { color:var(--text-bright); text-align:right; }
.qs-src { font-size:10.5px; }
.sos-btn { margin-top:14px; background:var(--red); color:#fff; text-align:center; padding:10px; border-radius:10px; font-size:12.5px; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:7px;}
.sos-btn:hover { background:#dc2626; }

.modal-backdrop { display:none; position:fixed; inset:0; background:rgba(5,8,16,.65); z-index:200; }
.modal-backdrop.open { display:block; }
.sos-modal { display:none; position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); z-index:201; background:var(--panel); border:1px solid var(--border); border-radius:16px; padding:28px; width:min(430px, 90vw); text-align:center; box-shadow:0 20px 60px rgba(0,0,0,.5);}
.sos-modal.open { display:block; }
.sos-modal-icon { width:56px; height:56px; border-radius:50%; background:#ef444422; color:var(--red); display:flex; align-items:center; justify-content:center; margin:0 auto 14px;}
.sos-modal h3 { margin:0 0 10px; font-size:17px; color:var(--text-bright);}
.sos-modal p { font-size:12.5px; color:var(--text); line-height:1.65; margin:0 0 20px; text-align:left;}
.sos-modal p b { color:var(--text-bright); }
.sos-modal-actions { display:flex; gap:10px; }
.sos-modal-actions .link-btn, .sos-modal-actions .ask-btn { width:auto; flex:1; margin-top:0; }
.sos-call-btn { background:var(--red) !important; }
.sos-call-btn:hover { background:#dc2626 !important; }

.main { flex:1; padding:18px 20px; min-width:0; }
.right-panel { width:300px; flex-shrink:0; padding:18px 16px; display:flex; flex-direction:column; gap:14px; }

.tab-content { display:none; }
.tab-content.active { display:block; animation:fadeIn .25s ease; }
@keyframes fadeIn { from { opacity:0; transform:translateY(4px);} to { opacity:1; transform:translateY(0);} }

.kpi-card, .mini-card, .panel { transition:border-color .15s, transform .15s, box-shadow .15s; }
.kpi-card:hover, .mini-card:hover { border-color:#33405f; transform:translateY(-2px); box-shadow:0 6px 18px rgba(0,0,0,.25); }
.nav-item { transition:background .15s, border-color .15s; }

.kpi-grid { display:grid; grid-template-columns:repeat(6,1fr); gap:12px; margin-bottom:16px;}
.kpi-card { background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:14px; display:flex; gap:10px; min-width:0;}
.kpi-icon { width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center; flex-shrink:0;}
.kpi-label { font-size:11.5px; color:var(--text); margin-bottom:3px;}
.kpi-value { font-size:19px; font-weight:700; }
.kpi-delta { font-size:10.5px; }
.kpi-cap { font-size:10px; color:#5a6584; }
.kpi-cap-line { font-size:10px; color:#5a6584; margin-top:1px;}
.up, .down { display:inline-flex; align-items:center; gap:3px; }
.delta-ic { flex-shrink:0; }
.up { color:var(--green); } .down { color:var(--red); }
.muted { color:#5a6584; }

.grid-3 { display:grid; grid-template-columns:1.2fr 1fr 1fr; gap:14px; margin-bottom:14px; }
.grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px; }
.grid-today { display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-bottom:14px;}
.panel { background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:14px; display:flex; flex-direction:column; overflow:hidden; min-width:0;}
.panel-title { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; flex:0 0 auto; gap:8px;}
.panel-title h3 { font-size:13.5px; margin:0; font-weight:600; }
.tag { font-size:10.5px; color:var(--text); background:var(--panel-2); padding:3px 9px; border-radius:16px; border:1px solid var(--border); white-space:nowrap;}
.view-all { font-size:11.5px; color:var(--blue); text-decoration:none; cursor:pointer;}

/* Charts (Plotly divs / inline SVGs) fill whatever height their panel row
   stretches them to, instead of sitting at a fixed pixel height and
   leaving a dead gap below when a sibling panel in the same row is
   taller. Sizing itself is done in JS (see CHARTS_JS) by measuring this
   box directly and handing Plotly an exact pixel size -- overflow:hidden
   here is a defensive backstop so a chart can never visually spill into
   a neighboring panel even in an edge case. */
.chart-fill { flex:1 1 auto; min-height:var(--chart-min, 160px); width:100%; overflow:hidden; min-width:0; }
.chart-fill > div { height:100%; width:100%; }
/* Buttons that end a card (Explore Network / View Prediction / Ask Copilot)
   pin to the bottom of the card, so all three cards in a row line up even
   when the content above them is a different height. */
.panel > .link-btn:last-child, .panel > .ask-btn:last-child { margin-top:auto; }

.legend-list { margin-top:6px; flex:0 0 auto; }
.legend-row { display:flex; align-items:center; gap:8px; font-size:11.5px; padding:4px 0; }
.legend-dot { width:9px;height:9px;border-radius:50%; flex-shrink:0;}
.legend-label { flex:1; color:var(--text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
.legend-val { color:var(--text-bright); flex-shrink:0; }

.today-card { }
.today-head { font-size:12px; color:var(--text); margin-bottom:4px; display:flex; align-items:center; justify-content:space-between; gap:8px;}
.today-tag { font-size:9.5px; color:#5a6584; background:var(--panel-2); border:1px solid var(--border); padding:2px 7px; border-radius:10px; white-space:nowrap;}
.today-value { font-size:24px; font-weight:700; margin-bottom:2px;}
.today-note { font-size:10px; color:#5a6584; margin-bottom:6px; line-height:1.4;}

.mini-row { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-bottom:14px;}
.mini-card { background:var(--panel); border:1px solid var(--border); border-radius:14px; padding:12px; display:flex; gap:10px; align-items:center; min-width:0;}
.mini-icon { width:34px;height:34px;border-radius:9px;display:flex;align-items:center;justify-content:center; flex-shrink:0;}
.mini-label { font-size:10.5px; color:var(--text); }
.mini-value { font-size:14px; font-weight:700; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
.mini-sub { font-size:10.5px; color:var(--text); }

.link-btn { margin-top:8px; background:none; border:1px solid var(--border); color:var(--blue); padding:7px 12px; border-radius:8px; font-size:12px; cursor:pointer; width:100%; display:flex; align-items:center; justify-content:center; gap:6px;}
.link-btn:hover { background:#1c2740; }
.link-btn:disabled { opacity:.5; cursor:not-allowed;}
.ask-btn { margin-top:8px; width:100%; background:var(--blue); color:#fff; border:none; padding:9px; border-radius:8px; font-size:12.5px; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px;}
.ask-btn:hover { background:#2563eb; }

.predictive-body { font-size:12px; }
.pred-label { color:var(--text); font-size:11px; margin-bottom:4px;}
.pred-text { color:var(--text); font-size:12.5px; }
.pred-highlight { color:var(--amber); font-size:19px; font-weight:700; margin:2px 0;}
.risk-badge { display:inline-block; background:#ef444422; color:var(--red); font-size:11px; padding:3px 10px; border-radius:14px; margin:8px 0;}
.conf-row { display:flex; justify-content:space-between; font-size:12px; margin-top:6px;}
.conf-bar { background:var(--panel-2); border-radius:6px; height:8px; margin-top:4px; overflow:hidden;}
.conf-fill { background:linear-gradient(90deg,var(--blue),var(--cyan)); height:100%; }
.pred-footnote { font-size:10px; color:#5a6584; margin-top:10px; line-height:1.4;}

.suggestion-item { display:flex; gap:9px; padding:8px 0; border-bottom:1px solid var(--border); align-items:flex-start;}
.suggestion-item:last-child { border-bottom:none; }
.suggestion-icon { color:var(--blue); margin-top:1px;}
.suggestion-text { font-size:11.8px; color:var(--text-bright); line-height:1.4;}
.suggestion-link { font-size:11px; color:var(--blue); text-decoration:none; }

.alert-item { display:flex; gap:9px; padding:9px 0; border-bottom:1px solid var(--border); }
.alert-item:last-child { border-bottom:none; }
.alert-icon { width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center; flex-shrink:0;}
.alert-title { font-size:11.8px; font-weight:600; }
.alert-text { font-size:11.5px; color:var(--text); line-height:1.4; }
.alert-time { font-size:10px; color:#5a6584; margin-top:1px;}

.wanted-item { display:flex; gap:10px; padding:9px 0; border-bottom:1px solid var(--border); align-items:center;}
.wanted-item:last-child { border-bottom:none; }
.wanted-avatar { width:38px;height:38px;border-radius:50%; background:linear-gradient(135deg,#3b3b3b,#1c1c1c); border:1px solid var(--border); display:flex; align-items:center;justify-content:center; font-size:12px; font-weight:700; color:var(--text-bright); flex-shrink:0;}
.wanted-name { font-size:12.5px; font-weight:600; }
.wanted-charge { font-size:11px; color:var(--text); }
.wanted-reward { font-size:11px; color:var(--amber); }

.fir-item { padding:8px 0; border-bottom:1px solid var(--border); }
.fir-item:last-child { border-bottom:none; }
.fir-no { font-size:12px; font-weight:600; }
.fir-type { font-size:11.3px; color:var(--text); }
.fir-time { font-size:10px; color:#5a6584; }

.chat-panel { display:flex; flex-direction:column; height:520px; }
.chat-log { flex:1; overflow-y:auto; padding:10px 4px; display:flex; flex-direction:column; gap:8px;}
.chat-bubble { max-width:75%; padding:9px 13px; border-radius:12px; font-size:13px; line-height:1.4;}
.chat-bubble.user { align-self:flex-end; background:var(--blue); color:#fff; border-bottom-right-radius:3px;}
.chat-bubble.bot { align-self:flex-start; background:var(--panel-2); border:1px solid var(--border); border-bottom-left-radius:3px;}
.chat-bubble.bot.thinking { color:#5a6584; font-weight:700; letter-spacing:2px; }
.chat-input-row { display:flex; gap:8px; margin-top:8px; }
.chat-input { flex:1; background:var(--panel-2); border:1px solid var(--border); border-radius:9px; padding:10px 14px; color:var(--text-bright); font-size:13px;}
.chat-send { background:var(--blue); color:#fff; border:none; padding:10px 18px; border-radius:9px; cursor:pointer; font-size:13px;}
.chat-send:hover { background:#2563eb; }

.stub-panel p { font-size:13px; color:var(--text); line-height:1.6; }
.stub-panel h3 { margin-top:0; }
.src-p { font-size:12.5px; color:var(--text); line-height:1.7; margin:0 0 8px; }
.src-p a { color:var(--blue); }
.src-p code { background:var(--panel-2); border:1px solid var(--border); border-radius:5px; padding:1px 6px; font-size:11.5px;}

/* status pills used in Vehicles & Assets / Department Directory tables */
.status-pill { font-size:10.5px; padding:3px 9px; border-radius:12px; white-space:nowrap; display:inline-block;}
.status-stolen { background:#ef444422; color:var(--red); }
.status-recovered { background:#22c55e22; color:var(--green); }
.status-impounded { background:#f59e0b22; color:var(--amber); }
.status-under-investigation { background:#3b82f622; color:var(--blue); }
.status-on-duty { background:#22c55e22; color:var(--green); }
.status-on-leave { background:#94a3b822; color:#94a3b8; }
.status-field-deployment { background:#8b5cf622; color:var(--purple); }

/* ---------------- Settings: profile + project info ---------------- */
.profile-form { display:flex; flex-direction:column; gap:14px; }
.avatar-upload-row { display:flex; gap:14px; align-items:center; }
.avatar-upload { position:relative; cursor:pointer; flex-shrink:0; }
.avatar-lg { width:64px; height:64px; border-radius:50%; background:linear-gradient(135deg,var(--blue),var(--purple)); display:flex; align-items:center; justify-content:center; font-size:20px; font-weight:700; color:#fff; overflow:hidden;}
.avatar-lg img { width:100%; height:100%; object-fit:cover; }
.avatar-edit-badge { position:absolute; right:-2px; bottom:-2px; width:22px; height:22px; border-radius:50%; background:var(--blue); display:flex; align-items:center; justify-content:center; border:2px solid var(--panel); color:#fff;}
.field-label { font-size:12px; font-weight:600; color:var(--text-bright); margin-bottom:2px;}
.field-hint { font-size:11px; color:var(--text); line-height:1.5; max-width:360px;}
.field-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.field { display:flex; flex-direction:column; gap:5px; font-size:11.5px; color:var(--text); }
.field span { display:inline-flex; align-items:center; gap:5px; }
.field-wide { grid-column:1 / -1; }
.field input, .field textarea { background:var(--panel-2); border:1px solid var(--border); border-radius:9px; padding:9px 12px; color:var(--text-bright); font-size:12.5px; font-family:inherit; resize:vertical; }
.field input:focus, .field textarea:focus { outline:1px solid var(--blue); }
.settings-actions { display:flex; align-items:center; gap:12px; margin-top:2px; flex-wrap:wrap;}
.settings-actions .ask-btn, .settings-actions .link-btn { margin-top:0; width:auto; }
.save-msg { font-size:11.5px; color:var(--green); }
.save-msg.err { color:var(--red); }
.upload-dropzone { border:1.5px dashed var(--border); border-radius:12px; padding:18px; text-align:center; cursor:pointer; color:var(--text); font-size:12px; display:flex; flex-direction:column; align-items:center; gap:6px; margin-top:12px; }
.upload-dropzone:hover, .upload-dropzone.drag { border-color:var(--blue); background:#3b82f60c; }
.attachment-list { display:flex; flex-direction:column; gap:8px; margin-top:12px; }
.attachment-row { display:flex; align-items:center; gap:10px; background:var(--panel-2); border:1px solid var(--border); border-radius:9px; padding:8px 12px; font-size:12px; color:var(--text);}
.attachment-row .att-name { flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; color:var(--text-bright);}
.attachment-row .att-size { color:var(--text); font-size:10.5px; flex-shrink:0;}
.attachment-row button { background:none; border:none; color:var(--text); cursor:pointer; display:flex; padding:2px;}
.attachment-row button:hover { color:var(--red); }

table { width:100%; border-collapse:collapse; font-size:12.5px; margin-top:10px;}
th { text-align:left; color:var(--text); font-weight:500; padding:8px 6px; border-bottom:1px solid var(--border); font-size:11px; text-transform:uppercase;}
.th-note { text-transform:none; font-size:9.5px; color:#5a6584; }
td { padding:8px 6px; border-bottom:1px solid var(--border); }
.table-filter { width:100%; background:var(--panel-2); border:1px solid var(--border); border-radius:9px; padding:9px 13px; color:var(--text-bright); font-size:12.5px;}

.footer { text-align:center; padding:16px; color:var(--text); font-size:11.5px; border-top:1px solid var(--border); margin-top:10px;}

/* ---------------- Reports & PDF: on-screen preview + print output ------- */
#printReport { background:#fff; color:#12151f; border-radius:10px; padding:26px; }
#printReport h1 { font-size:19px; margin:0 0 4px; }
#printReport h2 { font-size:14px; margin:18px 0 8px; color:#12151f; }
#printReport .pr-meta { font-size:11.5px; color:#555; margin:0 0 10px; }
#printReport .pr-note { font-size:11px; color:#555; line-height:1.6; background:#f3f4f7; border-radius:8px; padding:10px 12px; }
#printReport .pr-footer { font-size:10.5px; color:#777; margin-top:16px; }
.pr-table { width:100%; border-collapse:collapse; font-size:12px; }
.pr-table td, .pr-table th { padding:6px 8px; border-bottom:1px solid #e2e4ea; color:#12151f; }
.pr-table th { text-transform:none; font-size:11px; color:#555; }
.pr-table-wide td:first-child, .pr-table-wide th:first-child { width:40%; }

@media print {
  body * { visibility:hidden; }
  #printReport, #printReport * { visibility:visible; }
  #printReport { position:absolute; left:0; top:0; width:100%; margin:0; border-radius:0; }
}

@media (max-width:1500px) {
  .kpi-grid { grid-template-columns:repeat(3,1fr); }
}
@media (max-width:1300px) {
  .grid-3, .grid-2, .grid-today, .mini-row, .field-grid { grid-template-columns:1fr; }
  .right-panel { display:none; }
}
@media (max-width:980px) {
  .hamburger-btn { display:flex; }
  .sidebar {
    position:fixed; left:-260px; top:0; height:100vh; z-index:120;
    transition:left .2s ease; box-shadow:2px 0 24px rgba(0,0,0,.4);
  }
  .sidebar.open { left:0; }
  .sidebar-backdrop {
    display:none; position:fixed; inset:0; background:rgba(0,0,0,.5); z-index:110;
  }
  .sidebar-backdrop.open { display:block; }
  .search-wrap { max-width:180px; }
  .brand-tag { display:none; }
}
@media (max-width:480px) {
  .pill.lang { display:none; }
  .profile-wrap > div:not(.avatar) { display:none; }
  .search-wrap { max-width:120px; }
  .topbar { padding:10px 12px; gap:8px; }
  .topbar-right { gap:10px; }
  .kpi-grid { grid-template-columns:1fr 1fr; }
}
@media (max-width:360px) {
  .search-wrap { max-width:80px; }
  .topbar-right { gap:6px; }
  .brand-badge { width:32px; height:32px; }
  .topbar { padding:8px; gap:6px; }
}
@media (max-width:340px) {
  .brand > div:not(.brand-badge) { display:none; }
  .search-wrap { max-width:60px; }
}
"""

if __name__ == "__main__":
    build()
