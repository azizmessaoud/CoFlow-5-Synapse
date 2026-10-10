# Citation ledger — Empathize Evidence precision gate

**Rule:** Each named source must support the *exact* sentence it is attached to. Wording for transfer:

> This source supports the mechanism or measurement approach; it does not establish the Tunisian magnitude.

**Locus status:** `verified` = page/section confirmed from the source text available to this run; `from-prior-pack` = locus carried from v2 Empathize trail and still needs human PDF page check before professor submission; `agency-page` = official landing page / statute citation.

---

## Tunisia practice (primary)

| ID | Full cite | Type | Scope | Supports | Locus | Limitation for Grand Tunis sim |
|---|---|---|---|---|---|---|
| TN-1 | Société des Transports de Tunis (TRANSTU). *Parc et Trafic* (operator web pages). https://www.transtu.tn/fr/entreprise/0131-parc-et-trafic.html | Operator publication | Grand Tunis | Institutional role: bus/métro/TGM operator; fleet & trafic reporting | agency-page | Does not prove live AVL or field headway irregularity magnitudes |
| TN-2 | Ministère des Transports. *Horaires des voyages de la TRANSTU (GTFS)*. catalogue-data.transport.tn | Open data | Grand Tunis | Scheduled offer for simulation ingestion | agency-page (dataset) | **Scheduled**, not live positions |
| TN-3 | Décret n° 2000-149 du 24 janvier 2000 (priority / urgent-intervention vehicles and signals) | Statute | Tunisia | Legal priority-vehicle class + equipment rules | agency-page / JORT | Yield duty ≠ cleared downstream storage |
| TN-4 | Décret n° 2010-262 (Code de la route sanction tables) — failure to free way for announced priority vehicles | Statute | Tunisia | Enforcement of yield to priority vehicles | agency-page | Behavioural compliance rates not measured here |
| TN-5 | MEHAT — Unité UGOSMREPSL (éclairage public & signalisation lumineuse) org pages | Agency | Classified road network | Signalisation ownership / maintenance accountability exists | agency-page | Does not claim permanent detectors or adaptive ATC prevalence |
| TN-6 | Loi n° 2007-34 relative à la qualité de l’air; ANPE RNSQA | Statute / agency | Tunisia | Ambient AQ monitoring mandate; traffic-type stations exist | agency-page | City monitor ≠ school-gate personal exposure |
| TN-7 | CODATU / AFD. *Vers une mobilité urbaine durable en Tunisie* (valorisation Tunis, ~2018). https://www.codatu.org/wp-content/uploads/2023/04/doc-valorisation-tunis-v-2-9.pdf | Agency/cooperation report | Tunisian agglomerations / Tunis | Daily congestion, AQ & safety stress after car growth / strained TC; TRANSTU dominant | from-prior-pack (PDF §3 paysage) | Qualitative context; not corridor % delay or AQ µg/m³ |
| TN-8 | Othmani, Boubaker, Rehimi, El Alimi et al. Tunisian intersection SUMO case studies (ICAIGE / Logistiqua) | Peer-reviewed / conference | Tunisian intersections | Local academic practice uses SUMO for static vs adaptive comparison | from-prior-pack (DOI via IEEE) | Lab method only; not CoFlow results |

---

## Transfer literature (by insight)

### I-1 Reliability / upper-tail design

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I1a | UK Department for Transport. *TAG Unit A1.3: User and Provider Impacts*. Reliability ratio for car & non-freight LGV = **0.4** (std. dev. of journey time vs value of time). https://assets.publishing.service.gov.uk/media/6a034015e71c4cdf4026baae/tag-unit-a1-3-user-and-provider-impacts.pdf | Guidance (appraisal) | UK | **Mechanism + numerical appraisal value:** reliability of journey time is monetised separately from mean time; RR=0.4 for cars/non-freight LGV (§6.3.3–6.3.4) | verified §6.3.3–6.3.4 | **Not** a Tunisian WTP study; do not say “Tunisian users pay 0.4×” |
| T-I1b | FHWA. *Traffic Analysis Toolbox Volume VI — Reliability Analysis Guidance Addendum* (HOP-08-054 addendum). P90/P95, buffer index, planning time index | Guidance | US analysis practice | **Metric methods** for travel-time reliability | from-prior-pack | Method, not Tunis magnitude |

**Safe Empathize sentence:** For time-sensitive journeys, upper-tail journey time is a legitimate design target; UK appraisal separately values reliability (TAG A1.3 RR 0.4). This does **not** establish Tunisian preference magnitudes.

### I-2 Empty / ineffective green

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I2a | FHWA. *Automated Traffic Signal Performance Measures* (HOP-20-002). https://ops.fhwa.dot.gov/publications/fhwahop20002/fhwahop20002.pdf | Guidance | US agencies | **Metrics:** AoG, split failure, ped delay, etc. | from-prior-pack | Measurement approach; not Tunis empty-green % |
| T-I2b | FHWA. *Measures of Effectiveness and Validation Guidance for ASCT* (HOP-13-031) | Guidance | US | **MOEs** including arrivals on green, queues, oversaturation | from-prior-pack | Same |

**Safe sentence:** Signal-performance practice treats empty/ineffective green and split failure as recoverable inefficiencies measurable via ATSPM/ASCT MOEs — not a claimed Tunisian prevalence.

### I-3 EVP as space / corridor problem

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I3a | Nelson, E.J. & Bullock, D. (2000). Impact of Emergency Vehicle Preemption on Signalized Corridor Operation. *TRR* 1727:1–11. https://doi.org/10.3141/1727-01 | Peer-reviewed case | Lafayette IN (SR-26) | **Mechanism + case numeric:** dense/closely spaced preemption can raise arterial TT ~**20–30 s**; recovery/transition matters | verified abstract/TRID | US corridor case; externality magnitude not Tunis |
| T-I3b | TN-3 / TN-4 (above) | Statute | Tunisia | Legal priority exists without guaranteeing empty exit | — | — |

**Safe sentence:** Emergency priority is constrained by downstream storage and clearance space, not only by the signal state at the EV’s approach. Tunisian law creates priority status; Nelson & Bullock show dense preemption has measurable arterial externality in a US case.

### I-4 Pedestrian wait / clearance / completion

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I4a | Vallyon, C., Turner, S. & Hodgson, S. (2009). Reducing pedestrian delays at traffic signals. *ATRF*. https://atrf.info/papers/2009/2009_Vallyon_Turner_Hodgson.pdf | Conference paper (NZ sites) | NZ cities | Perceived wait ≈ **2×** actual (attitude surveys in project) | from-prior-pack (ATRF/NZTA line) | NZ survey; not Tunis perception |
| T-I4b | Vallyon, C. & Turner, S. (2011). *NZTA Research Report 440: Reducing pedestrian delay at traffic signals*. https://nzta.govt.nz/assets/resources/research/reports/440/docs/440.pdf | Agency research | NZ | Frustration / red-crossing risk after long waits (~20–30 s discussion in ped delay lit trail) | from-prior-pack | Transfer mechanism |
| T-I4c | UK DfT. *LTN 2/95* — ped-actuated max preset normally 40 s, up to 60 s | Guidance | UK | **Practice bound** on max wait presets | from-prior-pack | UK practice, not Tunis code |
| T-I4d | FHWA. *MUTCD* (2009) §4E — walking speed **3.5 ft/s (1.07 m/s)** | Standard | US | **Design assumption** for clearance | from-prior-pack §4E | Not a Tunisian legal requirement |
| T-I4e | FHWA *HCM* guidance — **1.0 m/s** when substantial older pedestrians | Guidance | US | Population-sensitive clearance assumption | from-prior-pack | Same |
| T-I4f | LaPlante & Kaese (ITE) — assistive speeds cane ~0.8, walker ~0.6 m/s | Professional guidance | US practice | Slower users need more clearance time | from-prior-pack | Speed bands, not Tunis sample |
| T-I4g | Bentzen et al. (2005). *JVIB* — blind pedestrian completion difficulties | Peer-reviewed | US | Completion / alignment difficulties | from-prior-pack | Accessibility mechanism |

**Safe sentence:** Clearance assumptions vary by standard and user population; waiting and crossing are separate service requirements; accessibility needs more than an app-only request. MUTCD/HCM/ITE are transfer design assumptions — not universal Tunisian requirements.

### I-5 Transit person-delay + bunching

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I5a | DfT TAG A1.3 — PT wait/lateness multipliers; Wardman meta-analysis mean wait ≈1.80× IVT (pack trail) | Guidance / meta | UK / multi | **Mechanism:** waiting valued higher than in-vehicle time | TAG verified for lateness 2.5× IVT §6.5.3; Wardman locus from-prior-pack | Appraisal weights ≠ Tunis rider survey |
| T-I5b | Newell, G.F. & Potts, R.B. (1964); Daganzo, C.F. (2009) bus bunching | Theory / peer-reviewed | General | **Mechanism:** headway irregularity self-amplifies | classic cites | Theory, not Tunis CV path |
| T-I5c | Hounsell, N. & McDonald, M. (1986). SCOOT bus priority, Southampton — up to **−39%** bus journey time | Field/transfer case | Southampton UK | **Feasibility** of TSP benefit | from-prior-pack | Feasibility ceiling, **not** CoFlow target |

**Safe sentence:** A delay on a bus can impose delay on many passengers at once; bunching increases irregularity and passenger waiting. Do not use vehicle-class delay ratios as Evidence unless directly sourced.

### I-6 Downstream harm

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I6a | FHWA ASCT MOEs / ATSPM — queue, oversaturation, spillback-related measures | Guidance | US | **Metric / mechanism** of local greed vs network | from-prior-pack | Not Tunis displacement % |
| T-I6b | Varaiya (2013) Max-Pressure — downstream capacity in control logic | Peer-reviewed | Theory/practice | Downstream-aware control motivation | from-prior-pack | Architecture support, not Empathize field |

### I-7 Stops as emission lever (proxy)

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I7a | Deschle, N., van Ark, E.J., van Gijlswijk, R., Janssen, R. (2022). Impact of Signalized Intersections on CO₂ and NOₓ Emissions of Heavy Duty Vehicles. *Energies* 15(3):1242. https://doi.org/10.3390/en15031242 | Peer-reviewed | HDV / intersections | **Mechanism:** signalised stop-start associated with avoidable CO₂/NOₓ for HDVs (pack cites ≤0.32 kg CO₂ / 1.8 g NOₓ per avoided stop — confirm in paper before quoting exact digits in slides) | DOI verified; exact digit locus **from-prior-pack → verify in PDF** | HDV/European conditions; HBEFA/SUMO remain **proxies** for Tunis AQ |
| T-I7b | Kingsley et al. (2014). *IJERPH* — children attending school near major roads (US) | Peer-reviewed | US | Near-road school **exposure context** | from-prior-pack | US demography; not Tunis school inventory |
| T-I7c | TN-6 ANPE / Loi 2007-34 | Statute | Tunisia | Ambient monitoring exists | — | Not street-gate measurement |

**Safe sentence:** Stop-and-go is an actionable signal-control lever associated with avoidable emissions; volume alone is too coarse. Deschle supports intersection/stop effects for HDVs — not “stops always dominate everywhere.”

### I-8 Observability

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I8a | FHWA ATSPM (HOP-20-002) — continuous performance measures for operators | Guidance | US | **Operational practice:** without continuous measures, timing changes are hard to justify/evaluate | from-prior-pack | Interpretive Empathize claim, not Tunis statistic |
| T-I8b | Transport for NSW. *SCATS Core* brochure (2022) — audit trails | Product doc | NSW / export | Audit as shipped product feature | from-prior-pack | Product pattern, not Tunis install |

### I-9 Explainability / override

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I9a | SCATS Core brochure — manual intervention + audit | Product doc | NSW | **Adoption/operability** pattern | from-prior-pack | No “X% distrust AI” |
| T-I9b | Smith et al., CMU Surtrac pilots — fallback to default durations on sensor/network failure; operator monitoring | Pilot / research | Pittsburgh / related | **Fallback + monitoring** under failure | from-prior-pack | US adaptive case |

**Keep distinct:** I-8 = measurement/accountability; I-9 = justification, adoption, controlled override.

### I-10 Incident tail

| ID | Full cite | Type | Scope | Supports | Locus | Limitation |
|---|---|---|---|---|---|---|
| T-I10a | FHWA Freeway Management / TIM materials — incidents often cited as ~**25–30%** of congestion delay in many US metro contexts; Puget Sound regional estimate commonly co-cited in pack | Agency handbook / regional | US metros | **Numerical transfer** for *US* incident share of delay | from-prior-pack — **verify exact handbook edition/page before submission** | **Not** a Tunisian estimate; cite with US scope only |
| T-I10b | FHWA TIM performance measures (e.g. HOP-15-028 / JPO-13-062 trail) — roadway clearance, incident clearance, secondary crashes | Guidance | US | **Metrics**; no universal detection-delay standard | from-prior-pack | Agency-set thresholds |

---

## Human verification still required before professor submission

1. Exact page for NZTA RR440 “20–30 s / red crossing” sentence.
2. Exact Deschle table for 0.32 kg CO₂ / 1.8 g NOₓ.
3. Exact FHWA handbook edition/page for 25–30% incident share.
4. Wardman meta-analysis full bibliographic entry for wait multiplier 1.80.
5. Hounsell & McDonald 1986 full title/page for −39%.
6. Surtrac Smith et al. primary paper DOI for fallback claim.
7. SCATS Core 2022 brochure stable URL + quoted feature list.

Until verified, those loci remain `from-prior-pack` and must not be presented as newly field-validated Tunis facts.
