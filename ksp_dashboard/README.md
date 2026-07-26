# Karnataka State Police — Crime Intelligence AI

A single-file, self-contained crime intelligence dashboard built on **real,
published Karnataka State Police statistics** — not synthetic demo data.
15 working modules: live search, a rule-based/live-AI chat assistant, real
analytics and mapping, a working PDF export, a real session audit log, and
editable settings with file upload.

> **Real data. Real features.**

---

## Contents
- [What this is](#what-this-is)
- [Live demo / how to view it](#live-demo--how-to-view-it)
- [Feature tour](#feature-tour-all-15-tabs)
- [Real data vs. illustrative data](#real-data-vs-illustrative-data)
- [The "Live AI" chat, honestly explained](#the-live-ai-chat-honestly-explained)
- [Why Emergency SOS calls a real number](#why-emergency-sos-calls-a-real-number)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Building it yourself](#building-it-yourself)
- [Responsive design](#responsive-design)
- [Known limitations](#known-limitations--by-design)
- [Data sources & credits](#data-sources--credits)
- [Other docs in this repo](#other-docs-in-this-repo)

---

## What this is

This project is a fictional-but-realistic **"Crime Intelligence AI"** portal
for the Karnataka State Police — the kind of internal analytics tool a state
police department might use. It was built in stages: first as a UI/UX
exercise, then rebuilt to fix real bugs, replace synthetic numbers with real
government statistics, turn every placeholder tab into a genuinely working
feature, and add a live-AI chat layer with an honest fallback.

The entire application — markup, styling, charts, and logic — lives in
**one HTML file** (`ksp_crime_dashboard.html`, ~5&nbsp;MB, because it embeds
the full Plotly.js charting library so it works completely offline). There
is no server, no database, and no build step required to *view* it.

## Live demo / how to view it

- **Easiest:** open `ksp_crime_dashboard.html` in any modern browser
  (double-click it, or drag it into a browser window).
- **As a Claude artifact:** if you're viewing this inside Claude, the
  dashboard renders inline and its chat features can use a real Claude model
  automatically (see [Live AI](#the-live-ai-chat-honestly-explained)).

## Feature tour (all 15 tabs)

| Tab | What it does |
|---|---|
| **Dashboard** | 6 KPI cards, a category-trend chart, a Karnataka hotspot map, category breakdown, real-time alerts, most-wanted, and recent FIRs — all real, sourced data unless tagged otherwise. |
| **AI Copilot** | Chat assistant. Tries a live Claude model first, falls back to a fast offline engine automatically — see below. |
| **Chat with Data** | Same engine, framed as direct dataset Q&A ("total cases", a district name, etc.). |
| **Crime Analytics** | The trend chart, category donut, and a top-districts bar chart, all from real KSP figures. |
| **Crime Map** | Full-size hotspot map; bubble size = real 2024 case volume per district. |
| **Network Analysis** | An illustrative criminal-network diagram (clearly labeled fictional). |
| **Predictive Intelligence** | An illustrative "next 7 days" risk projection (clearly labeled, not a real model). |
| **FIR & Case Search** | A searchable table of example FIRs, plus a real, searchable district-by-district case-data table. |
| **Accused & Persons** | An illustrative "most wanted" list (clearly fictional names). |
| **Vehicles & Assets** | A real, cited statistic (Bengaluru motor-vehicle theft, 2023) plus a searchable example vehicle registry. |
| **Reports & PDF** | A **working** export: click Print/Save as PDF and your browser renders a clean, real-data report via a dedicated print stylesheet. |
| **Alerts & Notifications** | A mix of real-figure alerts (e.g. cyber-crime growth) and clearly-labeled illustrative alerts. |
| **Audit Trail** | A **real, live log** of what you actually did this session — tab switches, searches, chats, saves, exports. Resets on reload (no backend log storage). |
| **Department Directory** | A searchable example personnel directory (honestly labeled illustrative — no real KSP staff data exists publicly, nor should it). |
| **Settings** | A genuinely working profile editor (name, badge, photo upload, bio) and project-notes/file-attachment panel, plus a full **Data Sources & Methodology** page. |

Also: a global search bar, a notification bell shortcut, a responsive
hamburger menu below 980px, and an **Emergency SOS** button that places a
real call to India's 112 emergency number (see below).

## Real data vs. illustrative data

Every panel in the app carries a small color-coded tag, and there's a
persistent legend under the top bar so this is never something you have to
read fine print to find:

- 🟢 **"Real, sourced data"** — traces to an exact citation in
  [`data/real/SOURCES.md`](data/real/SOURCES.md): Karnataka State Police
  statistics (district totals, category breakdowns, Bengaluru trend data),
  2022–2024, via the [OpenCity Urban Data Portal](https://data.opencity.in).
- 🟡 **"Illustrative example"** — individual FIR records, named "most
  wanted" suspects, the network diagram, vehicle-registry rows, and
  personnel-directory entries. **No public dataset of individual
  case/suspect records exists anywhere — nor should it, for privacy and
  operational-security reasons.** These sections are clearly labeled rather
  than either faked-as-real or omitted.

One data-integrity decision worth calling out: the most recent published
year (2024) only covers 21 "major" IPC crime heads — a *subset* of all IPC
sections — so it is **not** directly comparable to the fuller 2022/2023
totals. Rather than merge them into one misleading "trend," the dashboard
keeps these methodologies clearly separated throughout (see the Crime Trend
chart, which instead uses Bengaluru's clean, single-methodology 2021–2023
category series).

## The "Live AI" chat, honestly explained

The AI Copilot and Chat with Data panels try, in order:

1. **A real call to the Claude API** (`claude-sonnet-4-6`), grounded in a
   compact summary of the real dataset. This works with **zero setup** when
   the dashboard is viewed as a Claude artifact, because Anthropic proxies
   that request. No API key is ever entered or stored by the user.
2. **If that fails** (no backend available — e.g. a downloaded file opened
   locally, or hosted on plain static hosting with no key/proxy) — it
   **automatically and visibly** falls back to a fast, rule-based offline
   engine that answers from the same real dataset.

The chat header always shows which mode is active: `● Live AI — Claude
Sonnet` or `○ Offline Assistant — rule-based, real KSP data`. It never
pretends to be connected when it isn't.

## Why Emergency SOS calls a real number

Earlier versions of this button just showed a disclaimer alert. That's
honest but useless. The current version is honest *and* useful: clicking it
opens a confirmation panel, and confirming places a real call to **112**,
India's actual national emergency helpline (police / fire / ambulance).

What it deliberately does **not** do: silently auto-dial (a confirmation
step is required so it can't fire by accident), or send your location,
device info, or any dashboard/case data anywhere — it's just a normal phone
call, same as dialing it yourself. Faking a "real dispatch integration" here
would be actively dangerous (someone could rely on it in a genuine emergency
and get nothing) — no static webpage can reach a police department's
internal dispatch system without an official government integration, and
this project doesn't pretend otherwise.

## Architecture

- **Chart rendering.** Charts are registered as plain data
  (`build_charts.py`'s `CHART_REGISTRY`) rather than emitted as
  auto-executing `<script>Plotly.newPlot(...)</script>` tags. A small JS
  layer explicitly measures each chart's real container *after* its tab
  becomes visible and layout has settled (double `requestAnimationFrame`),
  then hands Plotly that exact pixel size. This was a real fix for a real
  bug: charts inside a tab that starts `display:none` used to make Plotly
  guess a zero-size container and silently fall back to a default 700×450
  canvas, which then overflowed into the neighboring panel. Backstopped
  with `overflow:hidden` + `min-width:0` everywhere so the bug class is
  structurally impossible now, not just patched. Verified clean from 320px
  to 4K.
- **Data pipeline.** `real_data.py` loads the raw, sourced CSVs in
  `data/real/`, aligns district names across three years of differently-
  formatted official releases, computes every KPI/aggregate the dashboard
  uses, and writes `data/real_crime_data.json`. `build_dashboard.py` never
  touches raw data directly — only the processed JSON.
- **No external runtime dependencies.** Plotly.js is embedded inline, not
  CDN-loaded, so the file works fully offline.
- **Audit logging, settings, and file uploads** are real client-side
  features (FileReader, canvas image resizing, in-memory state), backed by
  the Claude-artifact `window.storage` API when available, with a graceful
  session-only fallback otherwise (never `localStorage`, which isn't
  supported in that sandbox).

## Project structure

```
ksp_dashboard/
├── ksp_crime_dashboard.html   # the built app — open this file directly
├── build_dashboard.py         # main build script: HTML/CSS/JS templating
├── build_charts.py            # Plotly figure builders + chart registry
├── build_network_svg.py       # the illustrative network-diagram SVG
├── icons.py                   # hand-built inline SVG icon library (no emoji, no CDN)
├── real_data.py                # loads data/real/*.csv -> data/real_crime_data.json
├── karnataka_outline.json      # state outline coordinates for the map
├── data/
│   ├── real_crime_data.json    # generated -- the dashboard's actual dataset
│   └── real/
│       ├── SOURCES.md                          # exact citation per figure
│       ├── ka_districts_total_2022.csv         # real, KSP via OpenCity
│       ├── ka_districts_total_2023.csv         # real, KSP via OpenCity
│       ├── ka_districts_ipc_categories_2024.csv# real, KSP via OpenCity
│       ├── ka_sll_categories_2024_statewide.csv# real, KSP via OpenCity
│       ├── blr_property_crime_2021_2023.csv    # real, Bengaluru City Police
│       ├── blr_cyber_crime_2021_2023.csv       # real, Bengaluru City Police
│       └── blr_women_crime_2021_2023.csv       # real, Bengaluru City Police
└── README.md                  # this file
```

## Building it yourself

Requires Python 3 and `plotly`:

```bash
pip install plotly --break-system-packages   # or use a venv
python3 real_data.py         # (re)builds data/real_crime_data.json from data/real/*.csv
python3 build_dashboard.py   # (re)builds ksp_crime_dashboard.html
```

Both scripts are deterministic — rebuilding produces a byte-identical
`ksp_crime_dashboard.html` given the same source files.

## Responsive design

Verified with zero horizontal overflow and zero console errors from
**320px** (legacy phones) up through **1920px+** desktop displays:

- **≥1300px** — full three-column layout (sidebar, main, right panel).
- **900–1300px** — right panel (alerts/wanted/FIRs) collapses to reclaim
  width; sidebar stays put.
- **<980px** — sidebar becomes a proper slide-in overlay with a hamburger
  toggle in the top bar (an earlier version just made the sidebar vanish
  with no way to navigate — that dead end is fixed).
- **<480px / <360px** — the top bar itself progressively trims (language
  pill, then profile text) so nothing clips even on very old phones.

## Known limitations (by design)

These are intentional scope boundaries, not bugs:

- **No live police case-management feed.** No Indian state police force
  publishes one publicly. "Today" counters are explicitly labeled daily
  *averages* derived from the real 2023 annual total.
- **AI Copilot is not always a live LLM** outside a Claude-artifact context
  — see [above](#the-live-ai-chat-honestly-explained). This is disclosed
  in the UI, live, at all times via the mode badge.
- **Emergency SOS dials a real public number, not a KSP-internal system**
  — see [above](#why-emergency-sos-calls-a-real-number).
- **Individual case/suspect/personnel records are illustrative.** No such
  bulk public dataset exists or should exist.

## Data sources & credits

Primary source: **Karnataka State Police** (ksp.karnataka.gov.in) and
**Bengaluru City Police** (bcp.karnataka.gov.in), retrieved via the
[**OpenCity Urban Data Portal**](https://data.opencity.in) — a public
open-data initiative that republishes official government datasets with
source citation. Full per-figure citations: [`data/real/SOURCES.md`](data/real/SOURCES.md).

## Other docs in this repo


- [`data/real/SOURCES.md`](data/real/SOURCES.md) — exact source citation
  for every real figure used in the dashboard.

---

*Secure. Intelligent. Proactive. Together for a Safer Karnataka.*
