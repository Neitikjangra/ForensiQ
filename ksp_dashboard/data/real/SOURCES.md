# Data sources

All figures in this folder are taken verbatim from officially published
Karnataka State Police (KSP) crime statistics, retrieved via the OpenCity
Urban Data Portal (https://data.opencity.in), a public open-data
initiative that republishes government datasets with source citation.

- `ka_districts_total_2022.csv`, `ka_districts_total_2023.csv` —
  "District and City-wise Total Crimes Registered" (IPC + SLL), Karnataka
  Crime Data 2022 / 2023 collections.
  https://data.opencity.in/dataset/karnataka-crime-data-2022
  https://data.opencity.in/dataset/karnataka-crime-data-2023
  Original source: ksp.karnataka.gov.in

- `ka_districts_ipc_categories_2024.csv` — "District-wise IPC Crimes in
  Karnataka - 2024" (21 crime heads x 39 district/unit rows), the most
  recent year published as of this build.
  https://data.opencity.in/dataset/karnataka-crime-data-2024
  Original source: ksp.karnataka.gov.in

- `ka_sll_categories_2024_statewide.csv` — "SLL Crimes Under Various
  Heads - 2024" (statewide totals only, not district-broken-down).
  Same dataset page as above.

- `blr_property_crime_2021_2023.csv`, `blr_cyber_crime_2021_2023.csv`,
  `blr_women_crime_2021_2023.csv` — Bengaluru City Police category-wise
  reported/detected crime figures, 2021-2023.
  https://data.opencity.in/dataset/bengaluru-crime-data-2023
  Original source: bcp.karnataka.gov.in (Bengaluru City Police)

## What is NOT real data
Individual FIR records, named "Most Wanted" suspects, the criminal
network diagram, and "today"/live counters are clearly-labeled
**illustrative examples** built to match the real, published statistical
proportions above. No public bulk dataset of individual case records or
suspect identities exists (nor should it — that's sensitive operational
and personal data). There is no public live/real-time crime-data feed
for any Indian state police force; "today" figures are disclosed as
daily averages derived from the published annual totals, not a live feed.
