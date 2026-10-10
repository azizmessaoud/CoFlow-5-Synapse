# Tunisia practice evidence for Empathize (simulation setting)

Purpose: ground User Personas in **real Tunisian institutions and practice** for the CoFlow-5 Tunis SUMO showcase, without treating simulation outputs or IMATM placeholders as field results.

## What is Evidence here

| Kind | Use in Empathize |
|---|---|
| Official Tunisian law, agencies, open data, operator publications | **Primary** practice Evidence |
| Peer-reviewed / institutional Tunisian mobility studies (CODATU–AFD, Tunisian SUMO papers) | **Primary** context Evidence |
| SCATS / Surtrac / SCOOT / DfT / FHWA | **Transfer** Evidence for product needs operators already have elsewhere — not claims that Tunis already runs those systems |
| IMATM interview quotes, Table 9 digits, assumed protocol counts | **Not Evidence** (source self-labels placeholders) |
| SUMO/HBEFA KPIs | Simulation proxies for Test — not Tunis air quality or lives saved |

## Tunisian practice anchors (verified sources)

1. **TRANSTU** — Société des Transports de Tunis: bus + métro + TGM operator for Grand Tunis; public “Parc et Trafic” reporting (fleet, availability, passenger-km). Multiple bus **dépôts** and metro traffic/regulation services exist in operator organisation (official reports / org pages). Empathize roles: Rosa (dépôt / régulation), Chidi (scheduled rider), Hichem-like driver needs map to Chidi’s regularity need without inventing a ninth persona.
2. **Open data (Ministère des Transports)** — `catalogue-data.transport.tn`: official **TRANSTU GTFS** (scheduled bus/métro/TGM) and national stop référentiel. Simulation may ingest scheduled GTFS; it is **not** live AVL or observed road demand.
3. **Priority vehicles** — Décret n° **2000-149** (24 Jan 2000) lists priority / urgent-intervention vehicles and signal equipment rules; Code de la route enforcement (e.g. Décret 2010-262 tables) requires yielding to announced priority vehicles. Empathize: Marcus’s legal priority exists; corridor pre-clearance remains a design gap, not automatic signal integration.
4. **Signalisation lumineuse** — Ministère de l’Équipement (MEHAT) UGOSMREPSL follows public lighting and luminous signalling on the classified road network; municipalities operate local junctions. Empathize: Yuki’s role exists; adaptive ATC with permanent detection is **not** evidenced as the Tunis default.
5. **Air quality** — Loi **2007-34**; **ANPE** RNSQA ambient network (urban / traffic station types) and NT 106.04. Empathize: Maria’s concern is legitimate nationally; street-front exposure at a school gate is **not** the same as a city monitor — SUMO/HBEFA stays a proxy.
6. **Mobility context** — CODATU / AFD *Vers une mobilité urbaine durable en Tunisie* (valorisation Tunis): daily congestion, air pollution and road safety linked to modal shift toward cars and unstable collective transport after demand outgrew capacity; TRANSTU dominant public operator in Grand Tunis. Empathize: David/Chidi/Maria pains are structural, not invented for the course.
7. **Tunisian simulation practice** — Othmani, Boubaker, Rehimi, El Alimi and follow-on Logistiqua work: Tunisian intersections studied in **SUMO + Python**, comparing static vs adaptive lights for queues, energy, emissions. Empathize: local academic practice already uses SUMO as a **decision lab**, matching this project’s simulation posture.

## Simulation honesty (ADR-aligned)

- Tunis showcase = OSM geometry + official **scheduled** TRANSTU GTFS + **synthetic/calibrated** road demand until observed loops are verified.
- Results do **not** establish Tunis-wide field performance, measured AQ, or lives saved.
- Fixed-time / actuated / Max-Pressure comparisons stay on the controlled grid first; Tunis is relevance + data-ingestion story.
- World ATC metrics (ATSPM, reliability indices, TIM) are the **transfer measurement language** — see `world-truths-and-metrics.md`.

## Roster mapping (do not stack)

| CoFlow-5 (keep) | IMATM Tunis colour (same job) |
|---|---|
| Amara | Nadia — slower pedestrian |
| David | Amine — predictability |
| Chidi | Hichem — transit regularity (driver vs rider viewpoint) |
| Rosa | TRANSTU ops / dépôt régulation (not named in IMATM six) |
| Marcus | Karim — ambulance / urgent intervention |
| Yuki | Emna — municipal traffic / signal operator |
| Maria | Leila — resident / near-junction exposure |
| Omar | Incident / network awareness (Emna+Karim overlap in IMATM S-9) |
