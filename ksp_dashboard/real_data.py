"""
real_data.py
------------
Loads the real, sourced Karnataka State Police crime statistics in
data/real/*.csv (see data/real/SOURCES.md for provenance) and computes
every aggregate the dashboard needs, writing data/real_crime_data.json.

This replaces generate_dummy_data.py's random-number generator. The only
things that remain illustrative (clearly labeled as such in the output)
are individual case records, named "most wanted" suspects, the network
diagram, and "today" counters -- because no public bulk dataset of real
case/suspect-level records exists, and no Indian state police force
publishes a live case-management feed.

Run: python3 real_data.py
"""
import csv
import json
import os
import random
import datetime

random.seed(7)

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "real")
OUT = os.path.join(HERE, "data", "real_crime_data.json")

SOURCE_NAME = "Karnataka State Police (ksp.karnataka.gov.in), via OpenCity Urban Data Portal"
SOURCE_URL = "https://data.opencity.in/dataset/karnataka-crime-data-2024"


def read_csv(name):
    with open(os.path.join(RAW, name), newline="", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


# ---------------------------------------------------------------------
# 1. District totals, 2022 & 2023 (IPC+SLL, same methodology both years)
# ---------------------------------------------------------------------
def load_district_totals(fname):
    rows = read_csv(fname)
    header, body = rows[0], rows[1:]
    out = {}
    for r in body:
        name = r[0].strip()
        if name.upper() == "TOTAL":
            continue
        out[name] = {"ipc": int(r[1]), "sll": int(r[2]), "total": int(r[3])}
    return out


d2022 = load_district_totals("ka_districts_total_2022.csv")
d2023 = load_district_totals("ka_districts_total_2023.csv")

# ---------------------------------------------------------------------
# 2. District x category, 2024 (most recent published year, IPC major heads)
# ---------------------------------------------------------------------
rows = read_csv("ka_districts_ipc_categories_2024.csv")
header = rows[0][1:]
ACCIDENT_COLS = {"FATAL_MV_ACCIDENTS", "NONFATAL_MV_ACCIDENTS"}
NON_GEO_UNITS = {"Karnataka Railways", "Coastal Security Police", "CID"}

d2024_by_cat = {}
for r in rows[1:]:
    name = r[0].strip()
    if name.upper() == "TOTAL":
        state_totals_2024 = {h: int(v) for h, v in zip(header, r[1:])}
        continue
    d2024_by_cat[name] = {h: int(v) for h, v in zip(header, r[1:])}


def district_total_2024(cat_dict):
    return sum(v for k, v in cat_dict.items() if k not in ACCIDENT_COLS)


# Category grouping -> the 8 headline "crime categories" used by the donut
GROUPS = {
    "Theft & Burglary": ["THEFT", "BURGLARY_DAY", "BURGLARY_NIGHT"],
    "Cyber Crime": ["CYBER_CRIME"],
    "Hurt / Assault": ["HURT"],
    "Crimes Against Women": ["RAPE", "MOLESTATION", "CRUELTY_BY_HUSBAND", "DOWRY_DEATHS", "DP_ACT"],
    "Crimes Against Children (POCSO)": ["POCSO", "POCSO_RAPE"],
    "Robbery & Dacoity": ["ROBBERY", "DACOITY"],
    "Murder & Attempt": ["MURDER", "ATTEMPT_TO_MURDER"],
    "Other (Riots, Gambling, SC/ST Act)": ["RIOTS", "GAMBLING", "SC_ST"],
}
GROUP_COLORS = {
    "Theft & Burglary": "#8b5cf6",
    "Cyber Crime": "#22d3ee",
    "Hurt / Assault": "#f59e0b",
    "Crimes Against Women": "#ef4444",
    "Crimes Against Children (POCSO)": "#ec4899",
    "Robbery & Dacoity": "#3b82f6",
    "Murder & Attempt": "#dc2626",
    "Other (Riots, Gambling, SC/ST Act)": "#94a3b8",
}

crime_categories = []
for label, cols in GROUPS.items():
    count = sum(state_totals_2024[c] for c in cols)
    crime_categories.append({"category": label, "count": count, "color": GROUP_COLORS[label]})
crime_categories.sort(key=lambda c: -c["count"])

# ---------------------------------------------------------------------
# 3. Name alignment across the three years (different official spellings)
# ---------------------------------------------------------------------
ALIASES = {
    "Hubballi Dharwad City": "Hubballi Dharwad",
    "Chickballapura": "Chikkaballapura",
    "Kalaburagi": "Kalaburgi",
    "Kalaburagi City": "Kalaburgi City",
    "Shivamogga": "Shimoga",
    "Chamarajanagar": "Chamarajnagar",
    "Karnataka Railways": "KRailways",
}


def canon(name):
    return ALIASES.get(name, name)


# ---------------------------------------------------------------------
# 4. Approximate real coordinates for each geographic unit (district HQ /
#    city). Used only to place bubbles on the illustrative hotspot map.
# ---------------------------------------------------------------------
COORDS = {
    "Bengaluru City": (12.9716, 77.5946), "Bengaluru District": (13.05, 77.35),
    "Mysuru City": (12.2958, 76.6394), "Mysuru District": (12.15, 76.55),
    "Hubballi Dharwad": (15.3647, 75.1240), "Mangaluru City": (12.9141, 74.8560),
    "Dakshina Kannada": (12.85, 75.10), "Belagavi City": (15.8497, 74.4977),
    "Belagavi District": (15.95, 74.65), "Kalaburgi City": (17.3297, 76.8343),
    "Kalaburgi": (17.45, 76.95), "Ballari": (15.1394, 76.9214),
    "Bidar": (17.9104, 77.5199), "Vijayapura": (16.8302, 75.7100),
    "Chikkaballapura": (13.4351, 77.7315), "Chamarajnagar": (11.9236, 76.9456),
    "Chikkamagaluru": (13.3161, 75.7720), "Chitradurga": (14.2296, 76.3985),
    "Davanagere": (14.4644, 75.9932), "Gadag": (15.4300, 75.6300),
    "Hassan": (13.0072, 76.0962), "Haveri": (14.7936, 75.4044),
    "KGF": (12.9564, 78.2670), "Kodagu": (12.4244, 75.7382),
    "Kolar": (13.1372, 78.1298), "Koppal": (15.3547, 76.1544),
    "Mandya": (12.5221, 76.8951), "Raichur": (16.2076, 77.3463),
    "KRailways": (12.9716, 77.5946), "Ramanagara": (12.7217, 77.2812),
    "Shimoga": (13.9299, 75.5681), "Tumakuru": (13.3379, 77.1173),
    "Udupi": (13.3409, 74.7421), "Uttara Kannada": (14.7960, 74.7050),
    "Yadgiri": (16.7681, 77.1376), "Bagalkot": (16.1691, 75.6620),
    "Dharwad": (15.4589, 75.0078), "Vijayanagara": (15.2690, 76.4600),
}

# ---------------------------------------------------------------------
# 5. Build merged district rows: 2024 total (current), 2023, 2022, real YoY
# ---------------------------------------------------------------------
district_rows = []
for name, cats in d2024_by_cat.items():
    if name in NON_GEO_UNITS:
        continue
    total_2024 = district_total_2024(cats)
    key = canon(name)
    row23 = d2023.get(key) or d2023.get(name)
    row22 = d2022.get(key) or d2022.get(name)
    yoy = None
    if row23 and row22 and row22["total"]:
        yoy = round((row23["total"] - row22["total"]) / row22["total"] * 100, 1)
    lat, lon = COORDS.get(name, (14.5, 75.7))
    top_cat = max((c for c in cats if c not in ACCIDENT_COLS), key=lambda c: cats[c])
    district_rows.append({
        "district": name,
        "firs_2024": total_2024,
        "firs_2023": row23["total"] if row23 else None,
        "firs_2022": row22["total"] if row22 else None,
        "yoy_2022_23_pct": yoy,
        "top_category_2024": top_cat.replace("_", " ").title(),
        "lat": lat, "lon": lon,
    })

district_rows.sort(key=lambda r: -r["firs_2024"])

most_active = district_rows[0]
# fastest-growing among districts with a valid YoY figure
growth_candidates = [r for r in district_rows if r["yoy_2022_23_pct"] is not None]
fastest_growing_district = max(growth_candidates, key=lambda r: r["yoy_2022_23_pct"])

# ---------------------------------------------------------------------
# 6. Statewide snapshot figures (kept methodology-separated from trend chart;
#    the 2024 CSV only covers 21 "major" IPC heads, a SUBSET of all IPC
#    sections, so it is NOT directly comparable to the 2022/2023 full
#    IPC+SLL totals -- comparing them would make crime look like it fell
#    in 2024, which would be a methodology artifact, not reality)
# ---------------------------------------------------------------------
sll_2024_total = int([r for r in read_csv("ka_sll_categories_2024_statewide.csv")
                      if r[0].strip().upper() == "TOTAL"][0][1])
ipc_major_heads_2024_total = sum(state_totals_2024[c] for c in header if c not in ACCIDENT_COLS)
total_2022 = sum(v["total"] for v in d2022.values())
total_2023 = sum(v["total"] for v in d2023.values())

# ---------------------------------------------------------------------
# 7. Bengaluru supplementary detail (2021-23 category trend, for context
#    panels / the AI copilot's answers)
# ---------------------------------------------------------------------
def load_named_year_csv(fname):
    rows = read_csv(fname)
    body = [r for r in rows[1:] if r[0].strip().upper() != "TOTAL"]
    total_row = [r for r in rows[1:] if r[0].strip().upper() == "TOTAL"][0]
    return {
        "rows": [{"label": r[0], "y2021": int(r[1]), "y2022": int(r[3]), "y2023": int(r[5])} for r in body],
        "total": {"y2021": int(total_row[1]), "y2022": int(total_row[3]), "y2023": int(total_row[5])},
    }


blr_property = load_named_year_csv("blr_property_crime_2021_2023.csv")
blr_cyber = load_named_year_csv("blr_cyber_crime_2021_2023.csv")
blr_women = load_named_year_csv("blr_women_crime_2021_2023.csv")

cyber_growth_pct = round((blr_cyber["total"]["y2023"] - blr_cyber["total"]["y2022"])
                          / blr_cyber["total"]["y2022"] * 100, 1)

# Real, sourced, single-methodology 3-year trend used for the "Crime Trend
# Overview" chart (there is no public monthly crime dataset, so this uses
# the finest real granularity actually available: annual, by category).
trend_bengaluru = {
    "years": [2021, 2022, 2023],
    "series": [
        {"name": "Theft & Property Crime", "values": [blr_property["total"]["y2021"], blr_property["total"]["y2022"], blr_property["total"]["y2023"]], "color": "#8b5cf6"},
        {"name": "Cyber Crime", "values": [blr_cyber["total"]["y2021"], blr_cyber["total"]["y2022"], blr_cyber["total"]["y2023"]], "color": "#22d3ee"},
        {"name": "Crimes Against Women", "values": [blr_women["total"]["y2021"], blr_women["total"]["y2022"], blr_women["total"]["y2023"]], "color": "#ef4444"},
    ],
    "note": "Bengaluru City Police reported cases by category, 2021\u20132023 \u2014 real, sourced, one consistent methodology throughout.",
}

# ---------------------------------------------------------------------
# 8. KPIs
# ---------------------------------------------------------------------
top_category = crime_categories[0]
_totals_2024 = sorted(r["firs_2024"] for r in district_rows)
_n = len(_totals_2024)
district_median_2024 = (_totals_2024[_n // 2] if _n % 2 else
                         round((_totals_2024[_n // 2 - 1] + _totals_2024[_n // 2]) / 2))
high_volume_districts = sum(1 for v in _totals_2024 if v > district_median_2024)
women_children_2024 = (next(c["count"] for c in crime_categories if c["category"] == "Crimes Against Women")
                        + next(c["count"] for c in crime_categories if c["category"].startswith("Crimes Against Children")))

kpis = {
    "total_cases": total_2023,
    "total_cases_year": 2023,
    "total_cases_yoy_pct": round((total_2023 - total_2022) / total_2022 * 100, 1),
    "category_snapshot_total_2024": ipc_major_heads_2024_total + sll_2024_total,
    "bengaluru_total_2024": next(r["firs_2024"] for r in district_rows if r["district"] == "Bengaluru City"),
    "cyber_crime_2024": next(c["count"] for c in crime_categories if c["category"] == "Cyber Crime"),
    "cyber_crime_growth_pct": cyber_growth_pct,
    "women_safety_cases_2024": next(c["count"] for c in crime_categories if c["category"] == "Crimes Against Women"),
    "women_children_2024": women_children_2024,
    "districts_tracked": len(district_rows),
    "theft_2024": state_totals_2024["THEFT"],
    "district_median_2024": district_median_2024,
    "high_volume_districts": high_volume_districts,
}

# ---------------------------------------------------------------------
# 9. "Today" counters -- explicitly derived daily averages, not a live feed
# ---------------------------------------------------------------------
DAYS = 365
cases_avg_per_day = round(total_2023 / DAYS)
# use the 2024 IPC "detected"-style proxy: Bengaluru blended detection rate
detected_sum = blr_property["total"]["y2023"] + blr_cyber["total"]["y2023"] + blr_women["total"]["y2023"]
# use each dataset's own detected total (already 'Detected' cols = index 2/4/6 -> reuse raw csv)
def detected_total(fname):
    rows = read_csv(fname)
    total_row = [r for r in rows[1:] if r[0].strip().upper() == "TOTAL"][0]
    return int(total_row[2]) + int(total_row[4]) + int(total_row[6])


detected_2023_sum = (detected_total("blr_property_crime_2021_2023.csv")
                     + detected_total("blr_cyber_crime_2021_2023.csv")
                     + detected_total("blr_women_crime_2021_2023.csv"))
reported_2023_sum = blr_property["total"]["y2023"] + blr_cyber["total"]["y2023"] + blr_women["total"]["y2023"]
blended_detection_rate = round(detected_2023_sum / reported_2023_sum * 100, 1)
arrests_avg_per_day = round(cases_avg_per_day * blended_detection_rate / 100)

# ---------------------------------------------------------------------
# 10. Illustrative sections (clearly labeled): FIR log, most wanted,
#     network, vehicles, alerts, copilot suggestions, audit seed
# ---------------------------------------------------------------------
STATIONS_BY_DISTRICT = {
    "Bengaluru City": ["Whitefield PS", "K.R. Puram PS", "Madiwala PS", "Indiranagar PS", "Yeshwanthpur PS", "Cyber Crime PS"],
    "Mysuru City": ["Devaraja PS", "Vijayanagar PS", "Lashkar PS"],
    "Hubballi Dharwad": ["Vidyanagar PS", "Gokul Road PS"],
    "Mangaluru City": ["Mangaluru North PS", "Mangaluru South PS"],
    "Belagavi City": ["Tilakwadi PS", "Camp PS"],
}

FICTIONAL_NOTE = "Illustrative example — not a real case, person, or record"

crime_type_pool = [g["category"] for g in crime_categories for _ in range(max(1, g["count"] // 3000))]

fir_log = []
fir_no_base = 1230
for i in range(9):
    cat = random.choice(crime_type_pool)
    district = random.choice(district_rows[:12])["district"]
    stations = STATIONS_BY_DISTRICT.get(district, [f"{district} Town PS"])
    fir_log.append({
        "fir_no": f"{fir_no_base + i}/2025",
        "crime_type": cat.split(" & ")[0].split(" (")[0],
        "station": random.choice(stations),
        "minutes_ago": (i + 1) * random.randint(5, 12),
        "fictional": True,
    })
fir_log.sort(key=lambda f: f["minutes_ago"])

most_wanted = [
    {"name": "Suspect Alpha", "initials": "SA", "charges": "Theft, Robbery (fictional)", "reward": 50000, "fictional": True},
    {"name": "Suspect Beta", "initials": "SB", "charges": "NDPS, Arms Act (fictional)", "reward": 25000, "fictional": True},
    {"name": "Suspect Gamma", "initials": "SG", "charges": "Cheating, Forgery (fictional)", "reward": 20000, "fictional": True},
]

alerts = [
    {"kind": "spike", "title": "Crime Spike Alert", "text": f"Theft cases trending up in {district_rows[3]['district']} (illustrative alert)", "minutes_ago": 10},
    {"kind": "offender", "title": "Repeat Offender Alert", "text": "Fictional example alert for demonstration purposes", "minutes_ago": 21},
    {"kind": "spike", "title": "Crime Spike Alert", "text": f"Theft cases trending up in {district_rows[5]['district']} (illustrative alert)", "minutes_ago": 31},
    {"kind": "cyber", "title": "Cyber Crime Alert", "text": f"Cyber crime up {cyber_growth_pct}% year-on-year in Bengaluru (real KSP figure)", "minutes_ago": 40},
    {"kind": "safety", "title": "Women Safety Alert", "text": "Illustrative example alert for demonstration purposes", "minutes_ago": 51},
]

network = {
    "center": {"label": "Suspect X (fictional)", "role": "History-Sheeter (illustrative example)"},
    "nodes": [
        {"label": "Associate 1 (fictional)", "type": "person", "icon": "person"},
        {"label": "Associate 2 (fictional)", "type": "person", "icon": "person"},
        {"label": "Linked Cases (fictional)", "type": "case", "icon": "file"},
        {"label": "Linked Gang Group (fictional)", "type": "group", "icon": "group"},
        {"label": "Stolen Vehicles (fictional)", "type": "vehicle", "icon": "car"},
        {"label": "Phone Numbers (fictional)", "type": "phone", "icon": "phone"},
    ],
}

vehicle_status_pool = ["Stolen", "Recovered", "Impounded", "Under Investigation"]
vehicle_type_pool = ["Two-Wheeler", "Car", "Auto-Rickshaw", "Commercial Vehicle", "Two-Wheeler", "Two-Wheeler"]
vehicles = []
for i in range(14):
    district = random.choice(district_rows[:15])["district"]
    vehicles.append({
        "id": f"KA-{random.randint(1,60):02d}-{random.choice('ABCDEFGH')}{random.choice('ABCDEFGH')}-{random.randint(1000,9999)}",
        "type": random.choice(vehicle_type_pool),
        "status": random.choice(vehicle_status_pool),
        "district": district,
        "linked_fir": f"{fir_no_base + random.randint(0, 30)}/2025",
        "fictional": True,
    })

copilot_suggestions = [
    f"Cyber crime rose {cyber_growth_pct}% in Bengaluru (2022\u219223, real KSP data) \u2014 review cyber cell staffing",
    f"{most_active['district']} recorded {most_active['firs_2024']:,} cases in 2024, the highest in the state",
    f"Theft & burglary is the single largest category statewide in 2024 ({crime_categories[0]['count']:,} cases)"
    if crime_categories[0]["category"] == "Theft & Burglary" else
    f"{crime_categories[0]['category']} is the single largest category statewide in 2024 ({crime_categories[0]['count']:,} cases)",
]

predictive = {
    "horizon_days": 7,
    "top_categories": [crime_categories[0]["category"], crime_categories[1]["category"]],
    "districts": [d["district"] for d in district_rows[:3]],
    "risk_level": "High Risk",
    "confidence_score": 87,
    "note": "Illustrative projection for demonstration \u2014 not a statistical forecast model.",
}

# ---------------------------------------------------------------------
# 10b. Illustrative officer/personnel directory (clearly fictional names,
#      NOT real KSP personnel records -- no such bulk dataset is or
#      should be public)
# ---------------------------------------------------------------------
FIRST_NAMES = ["Arjun", "Priya", "Kavya", "Ravi", "Deepa", "Suresh", "Anitha", "Manoj", "Lakshmi", "Vikram",
               "Sunita", "Ganesh", "Meera", "Naveen", "Pooja", "Rajesh", "Divya", "Kiran", "Shalini", "Arun"]
LAST_NAMES = ["Rao", "Kumar", "Nair", "Reddy", "Gowda", "Hegde", "Shetty", "Naik", "Iyer", "Patil"]
RANKS = ["Inspector", "Sub-Inspector", "ASI", "Head Constable", "Constable", "DySP", "Circle Inspector"]
STATUS_POOL = ["On Duty", "On Duty", "On Duty", "On Leave", "Field Deployment"]

directory = []
used_names = set()
for i in range(24):
    while True:
        nm = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if nm not in used_names:
            used_names.add(nm)
            break
    d_row = random.choice(district_rows[:20])
    directory.append({
        "name": nm,
        "rank": random.choice(RANKS),
        "station": f"{d_row['district']} HQ",
        "badge": f"KSP-{random.randint(10000, 99999)}",
        "status": random.choice(STATUS_POOL),
        "fictional": True,
    })
directory.sort(key=lambda r: r["name"])

# ---------------------------------------------------------------------
# Assemble & write
# ---------------------------------------------------------------------
data = {
    "meta": {
        "generated_at": datetime.date.today().strftime("%d %b %Y"),
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "latest_year": 2024,
        "note": ("Aggregate crime statistics (totals, categories, district figures, trends) are real "
                 "published Karnataka State Police figures for 2022\u20132024, the most recent year "
                 "available. Individual FIR records, named suspects, the network diagram, vehicle "
                 "records, and 'today' counters are clearly-labeled illustrative examples \u2014 no "
                 "public dataset of individual case or suspect records exists, and no Indian state "
                 "police force publishes a live case-management feed."),
    },
    "kpis": kpis,
    "trend_bengaluru": trend_bengaluru,
    "crime_categories": crime_categories,
    "districts": district_rows,
    "most_active_district": {"district": most_active["district"], "firs": most_active["firs_2024"]},
    "most_common_category": {"category": crime_categories[0]["category"], "count": crime_categories[0]["count"]},
    "fastest_growing": {
        "label": "Cyber Crime (Bengaluru)", "pct": cyber_growth_pct,
        "detail": f"{blr_cyber['total']['y2022']:,} \u2192 {blr_cyber['total']['y2023']:,} cases, 2022\u21922023",
    },
    "stations": [{"station": f"{r['district']} (district total)", "firs": r["firs_2024"]} for r in district_rows[:5]],
    "cases_registered_today": cases_avg_per_day,
    "arrests_today": arrests_avg_per_day,
    "cases_sparkline": [round(cases_avg_per_day * f) for f in (0.90, 1.05, 0.95, 1.10, 0.88, 1.03, 1.0)],
    "arrests_sparkline": [round(arrests_avg_per_day * f) for f in (0.88, 1.08, 0.93, 1.12, 0.85, 1.05, 1.0)],
    "daily_figures_note": "Illustrative day-to-day variation around the real 2023 daily average \u2014 no live case-management feed exists publicly.",
    "blended_detection_rate": blended_detection_rate,
    "alerts": alerts,
    "most_wanted": most_wanted,
    "fir_log": fir_log,
    "network": network,
    "vehicles": vehicles,
    "directory": directory,
    "predictive": predictive,
    "copilot_suggestions": copilot_suggestions,
    "bengaluru_detail": {"property": blr_property, "cyber": blr_cyber, "women": blr_women},
}

with open(OUT, "w") as f:
    json.dump(data, f, indent=2)
print("Wrote", OUT)
print("Total districts:", len(district_rows))
print("2023 total (headline KPI):", total_2023, "| 2022 total:", total_2022)
print("2024 category snapshot (major heads + SLL):", ipc_major_heads_2024_total + sll_2024_total)
print("Cyber crime growth 2022->23:", cyber_growth_pct, "%")
print("Blended detection rate (2023 sample):", blended_detection_rate, "%")
