"""
generate_dummy_data.py
-----------------------
Creates every dummy dataset needed to power the Karnataka State Police
Crime Intelligence dashboard (exact-replica version). All data here is
SYNTHETIC / FICTIONAL, generated for UI demo purposes only -- no real
crime records, no real persons, no real case data.

Outputs a single data/dummy_data.json bundling every dataset, plus
data/*.csv copies of the tabular ones (districts, stations, fir_log,
most_wanted, alerts) so they can be inspected/edited independently.
"""
import json
import random
import os
from datetime import datetime, timedelta
from faker import Faker

random.seed(42)
fake = Faker("en_IN")
Faker.seed(42)

OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)

TODAY = datetime(2025, 5, 26)  # matches "Last Updated: 26 May 2025" on the sample

# ---------------------------------------------------------------------
# 1. Real Karnataka districts/cities with approximate real coordinates
#    (place names + coordinates are real geography; crime figures are
#    entirely synthetic).
# ---------------------------------------------------------------------
DISTRICTS = [
    {"name": "Bengaluru City", "lat": 12.9716, "lon": 77.5946},
    {"name": "Mysuru",         "lat": 12.2958, "lon": 76.6394},
    {"name": "Hubballi-Dharwad", "lat": 15.3647, "lon": 75.1240},
    {"name": "Belagavi",       "lat": 15.8497, "lon": 74.4977},
    {"name": "Kalaburagi",     "lat": 17.3297, "lon": 76.8343},
    {"name": "Ballari",        "lat": 15.1394, "lon": 76.9214},
    {"name": "Davanagere",     "lat": 14.4644, "lon": 75.9932},
    {"name": "Shivamogga",     "lat": 13.9299, "lon": 75.5681},
    {"name": "Mangaluru",      "lat": 12.9141, "lon": 74.8560},
    {"name": "Tumakuru",       "lat": 13.3379, "lon": 77.1173},
    {"name": "Udupi",          "lat": 13.3409, "lon": 74.7421},
    {"name": "Vijayapura",     "lat": 16.8302, "lon": 75.7100},
    {"name": "Raichur",        "lat": 16.2076, "lon": 77.3463},
    {"name": "Bidar",          "lat": 17.9104, "lon": 77.5199},
    {"name": "Chikkamagaluru", "lat": 13.3161, "lon": 75.7720},
    {"name": "Hassan",         "lat": 13.0072, "lon": 76.0962},
    {"name": "Kolar",          "lat": 13.1372, "lon": 78.1298},
    {"name": "Mandya",         "lat": 12.5221, "lon": 76.8951},
    {"name": "Chitradurga",    "lat": 14.2296, "lon": 76.3985},
    {"name": "Koppal",         "lat": 15.3547, "lon": 76.1544},
]

district_rows = []
for d in DISTRICTS:
    base = random.randint(400, 2200)
    if d["name"] == "Bengaluru City":
        base = random.randint(16000, 19500)  # match sample's "Bengaluru City FIRs: 18,547"
    firs = base
    solved = int(firs * random.uniform(0.55, 0.72))
    yoy = round(random.uniform(-22, 28), 1)
    district_rows.append({
        "district": d["name"], "lat": d["lat"], "lon": d["lon"],
        "firs": firs, "cases_solved": solved,
        "risk_intensity": round(min(100, firs / 195), 1),
        "yoy_change_pct": yoy,
    })

most_active = max(district_rows, key=lambda r: r["firs"])
most_improved = min(district_rows, key=lambda r: r["yoy_change_pct"])

# ---------------------------------------------------------------------
# 2. Crime categories (2025), matching the sample's donut slices
# ---------------------------------------------------------------------
CRIME_CATEGORIES = [
    {"category": "Theft", "count": 56789, "color": "#8b5cf6"},
    {"category": "Assault", "count": 45612, "color": "#f59e0b"},
    {"category": "Cheating", "count": 34567, "color": "#22c55e"},
    {"category": "Cyber Crime", "count": 28945, "color": "#3b82f6"},
    {"category": "Robbery", "count": 25478, "color": "#ef4444"},
    {"category": "Other", "count": 54398, "color": "#94a3b8"},
]
total_firs_2025 = sum(c["count"] for c in CRIME_CATEGORIES)
most_common_category = max(CRIME_CATEGORIES, key=lambda c: c["count"])

# ---------------------------------------------------------------------
# 3. Monthly crime trend, 2024 vs 2025 (Jan-Dec), synthetic seasonal wave
# ---------------------------------------------------------------------
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def seasonal_series(base, amplitude, noise, months=12):
    vals = []
    for i in range(months):
        seasonal = amplitude * random.uniform(0.6, 1.0) * (1 if i % 3 != 0 else -1)
        v = base + seasonal + random.uniform(-noise, noise)
        vals.append(round(max(v, base * 0.4)))
    return vals

trend_2024 = seasonal_series(base=22000, amplitude=6000, noise=1500)
trend_2025 = seasonal_series(base=20500, amplitude=7500, noise=1800, months=5)  # data only up to May 2025

# ---------------------------------------------------------------------
# 4. Today's snapshot sparklines: cases registered / arrests, last 14 days
# ---------------------------------------------------------------------
def daily_sparkline(base, noise, days=14):
    return [max(0, round(base + random.uniform(-noise, noise))) for _ in range(days)]

cases_registered_today = 1247
arrests_today = 312
cases_sparkline = daily_sparkline(cases_registered_today * 0.85, cases_registered_today * 0.25)
arrests_sparkline = daily_sparkline(arrests_today * 0.85, arrests_today * 0.25)

# ---------------------------------------------------------------------
# 5. Top police stations by FIRs
# ---------------------------------------------------------------------
STATIONS = [
    {"station": "Bengaluru City PS", "firs": 4567},
    {"station": "Whitefield PS", "firs": 3456},
    {"station": "Madiwala PS", "firs": 2987},
    {"station": "Yeshwanthpur PS", "firs": 2654},
    {"station": "K.R. Puram PS", "firs": 2345},
]

# ---------------------------------------------------------------------
# 6. KPI summary cards
# ---------------------------------------------------------------------
kpis = {
    "total_firs": total_firs_2025,
    "total_firs_delta": 18.6,
    "cases_solved": int(total_firs_2025 * 0.593),
    "cases_solved_delta": 22.4,
    "conviction_rate": 68.7,
    "conviction_rate_delta": 5.3,
    "active_investigations": 66342,
    "active_investigations_delta": 12.7,
    "repeat_offenders": 8472,
    "repeat_offenders_delta": 14.8,
    "crime_hotspots": 23,
    "cases_registered_today": cases_registered_today,
    "cases_registered_delta": 8.4,
    "arrests_today": arrests_today,
    "arrests_delta": 11.2,
}

# ---------------------------------------------------------------------
# 7. Criminal network analysis -- entirely fictional demo entity, styled
#    like the sample's node graph. Clearly a synthetic placeholder case
#    file, not a real person.
# ---------------------------------------------------------------------
network = {
    "center": {"id": "suspect", "label": "Suspect X", "role": "History-Sheeter (demo record)"},
    "nodes": [
        {"id": "assoc1", "label": "Associate 1", "type": "person", "icon": "person"},
        {"id": "assoc2", "label": "Associate 2", "type": "person", "icon": "person"},
        {"id": "vehicles", "label": "Stolen Vehicles (12)", "type": "asset", "icon": "car"},
        {"id": "phones", "label": "Phone Numbers (7)", "type": "asset", "icon": "phone"},
        {"id": "gang", "label": "Linked Gang Group", "type": "group", "icon": "group"},
        {"id": "cases", "label": "Linked Cases (23)", "type": "case", "icon": "file"},
    ],
}

# ---------------------------------------------------------------------
# 8. Predictive intelligence (dummy next-7-day forecast)
# ---------------------------------------------------------------------
predictive = {
    "horizon_days": 7,
    "top_categories": ["Theft", "Robbery"],
    "districts": ["Bengaluru City", "Mysuru", "Tumakuru"],
    "risk_level": "High Risk",
    "confidence_score": 87,
}

# ---------------------------------------------------------------------
# 9. AI Copilot canned suggestions (used for quick-suggestion cards
#    and as a keyword-matched fallback in the on-page chat demo)
# ---------------------------------------------------------------------
copilot_suggestions = [
    "3 repeat offenders released from prison are active in Bengaluru",
    "Theft cases are increasing 32% in weekend nights",
    "2 new criminal gangs formed in last 15 days",
]

# ---------------------------------------------------------------------
# 10. Real-time alerts feed
# ---------------------------------------------------------------------
alert_templates = [
    ("Crime Spike Alert", "Theft cases increased by {pct}% in {district}", "spike"),
    ("Repeat Offender Alert", "{name} spotted in {district}", "offender"),
    ("Cyber Fraud Alert", "UPI fraud cases increased in {district}", "cyber"),
    ("Women Safety Alert", "High risk zone detected in {district}", "safety"),
]
alerts = []
mins_ago = 10
for i in range(6):
    title, tmpl, kind = random.choice(alert_templates)
    district = random.choice(DISTRICTS)["name"]
    text = tmpl.format(pct=random.randint(15, 45), district=district, name=fake.name())
    alerts.append({"title": title, "text": text, "kind": kind, "minutes_ago": mins_ago})
    mins_ago += random.randint(5, 20)

# ---------------------------------------------------------------------
# 11. Most wanted (fictional demo entries -- no real photos, initials only)
# ---------------------------------------------------------------------
most_wanted = []
charges_pool = ["Theft, Robbery, Assault", "NDPS, Arms Act", "Cheating, Forgery",
                 "Extortion, Assault", "Burglary, Theft"]
for i in range(3):
    name = fake.name_male()
    most_wanted.append({
        "name": name,
        "initials": "".join([p[0] for p in name.split()[:2]]).upper(),
        "charges": charges_pool[i % len(charges_pool)],
        "reward": [50000, 25000, 20000][i],
    })

# ---------------------------------------------------------------------
# 12. Recent FIR log
# ---------------------------------------------------------------------
fir_crime_types = ["Theft", "Assault", "Cyber Crime", "Robbery", "Cheating", "Burglary"]
fir_log = []
fir_no = 1234
mins_ago = 2
for i in range(6):
    station = random.choice(STATIONS)["station"]
    crime = random.choice(fir_crime_types)
    fir_log.append({
        "fir_no": f"{fir_no}/2025",
        "crime_type": crime,
        "station": station,
        "minutes_ago": mins_ago,
    })
    fir_no -= 1
    mins_ago += random.randint(3, 10)

# ---------------------------------------------------------------------
# Bundle + write
# ---------------------------------------------------------------------
bundle = {
    "generated_at": TODAY.strftime("%d %b %Y %H:%M:%S"),
    "kpis": kpis,
    "districts": district_rows,
    "most_active_district": most_active,
    "most_improved_district": most_improved,
    "crime_categories": CRIME_CATEGORIES,
    "most_common_category": most_common_category,
    "months": MONTHS[:len(trend_2024)],
    "trend_2024": trend_2024,
    "trend_2025": trend_2025,
    "cases_sparkline": cases_sparkline,
    "arrests_sparkline": arrests_sparkline,
    "stations": STATIONS,
    "network": network,
    "predictive": predictive,
    "copilot_suggestions": copilot_suggestions,
    "alerts": alerts,
    "most_wanted": most_wanted,
    "fir_log": fir_log,
}

with open(os.path.join(OUT_DIR, "dummy_data.json"), "w") as f:
    json.dump(bundle, f, indent=2)

# Also drop a couple of the tabular pieces as plain CSVs for easy editing
import csv
with open(os.path.join(OUT_DIR, "districts.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(district_rows[0].keys()))
    w.writeheader()
    w.writerows(district_rows)

with open(os.path.join(OUT_DIR, "stations.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["station", "firs"])
    w.writeheader()
    w.writerows(STATIONS)

with open(os.path.join(OUT_DIR, "fir_log.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["fir_no", "crime_type", "station", "minutes_ago"])
    w.writeheader()
    w.writerows(fir_log)

print("Generated data/dummy_data.json (+ districts.csv, stations.csv, fir_log.csv)")
print("Total FIRs 2025:", total_firs_2025)
print("Most active district:", most_active["district"], most_active["firs"])
print("Most improved district:", most_improved["district"], most_improved["yoy_change_pct"])
