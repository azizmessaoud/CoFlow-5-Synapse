# CoFlow-5 evidence and claim audit

**Research ticket:** Evidence and claim audit  
**Audit date:** 20 September 2026  
**Scope:** `CoFlow-5_System_Requirements_Book.md`, `coflow5-empathize-pack.md`, `coflow5-project-context.md`, the ticket, and the binary-source extraction note.

## Resolution gist

The human-centred design direction is defensible, but the documents overstate the maturity of their evidence base. The named “33-row verified evidence trail” contains **32 data rows**, not 33, and several rows are secondary summaries, obsolete guidance, vendor material, or proposed project criteria rather than verified primary evidence. The strongest corrections are:

1. Change “33-row verified evidence trail” to **“32-row mixed-source evidence register, audited by source type”** unless the register is rebuilt and recounted.
2. Correct Kingsley from **13.5%** to **12.5% of students in the study (6.2% within 100 m plus 6.3% at 100–250 m)**; 13.5% is not the national proximity percentage. The paper is in the *Journal of Exposure Science & Environmental Epidemiology*, not *IJERPH*.
3. Do not attach the **7.6% side-street/travel-time effect** to Nelson and Bullock. Their paper supports the **20–30 s worst arterial increase**; 7.6% comes from a different Virginia Route 7 study.
4. Replace “T-REX was ~14× more expensive to train” with **“T-REX allocated FMA2C/IPPO 1,400 training episodes versus 100 for IDQN/MPLight (14× the episode budget); it did not report a general 14× cost ratio.”**
5. Replace “each minute cuts survival by 7%” with **“in one retrospective Taipei OHCA cohort, each additional minute of ALS response time was associated with 7% lower adjusted odds of survival to discharge (aOR 0.93, 95% CI 0.89–0.97).”**
6. Treat all decision-matrix scores, reward weights, priorities, thresholds, KPI targets, and schedules as **team judgements or proposed targets**, not empirical evidence.

## Classification rules

- **Verified primary evidence:** checked against the owning agency’s documentation, original paper, official product documentation, or authors’ repository.
- **Secondary-only evidence:** located only in a catalogue abstract, synthesis, or source that itself cites another study.
- **Project assumption:** an architectural inference or local design choice not established by the cited source.
- **Proposed target:** an acceptance threshold to test, not a literature result.
- **Unsupported or overstated:** wrong, misattributed, broader than the source, or presented with unjustified certainty.

Absence claims such as “only one study exists,” “no work does X,” or “no seeds/CIs” were treated cautiously. A paper’s failure to report an item supports **“not reported in the inspected paper”**, not a universal claim.

## Claim audit

### Evidence register and decision matrices

| Claim | Classification | Audit result and required wording |
|---|---|---|
| “33-row verified evidence trail” | **Unsupported/overstated** | The evidence table in `coflow5-personas-journeys.md` and the copied pack has **32 data rows**. It also includes explicitly secondary material (for example Pratt via TCRP/Litman), a vendor survey, and items verified only through catalogue abstracts. Use “32-row mixed-source evidence register” unless rebuilt. |
| Every numerical decision-matrix score or weight | **Project assumption / team judgement** | Scores and weights express team preferences; they are not measurements. This includes priority ordering, qualitative architecture ratings, `λ_eco`, reward coefficients, benefit-minus-externality bids, and any weighted option score. Cite evidence for the criteria, but label the numerical score/weight **team judgement** and sensitivity-test it. |
| Acceptance values such as 40 s, −5%, −15%, ≤3%, −25%, −10%, ≤5%, <100 ms, α=0.05, 5–10 s epochs, and week numbers | **Proposed targets** | These are legitimate hypotheses or engineering budgets, but not source-established thresholds. Keep the “proposed” label at every occurrence. Statistical α/Holm is an analysis choice, not evidence that zero displacement will occur. |
| IMATM interviews and Table 9 numbers | **Project placeholders** | The source itself says to replace them. They must not enter the evidence register as observations. |

### Pedestrian waiting and walking speed

| Claim | Classification | Audit result |
|---|---|---|
| Perceived wait is about 2× actual | **Verified primary evidence** | Vallyon, Turner and Hodgson report average perceived delay about double observed average delay at surveyed New Zealand intersections. This is a sample finding, not a universal psychophysical constant. [ATRF paper](https://australasiantransportresearchforum.org.au/wp-content/uploads/2022/03/2009_Vallyon_Turner_Hodgson.pdf) |
| Frustration rises after 20–30 s; two-thirds willing to cross on red | **Verified primary evidence, wording correction** | NZTA RR440 supports disproportionate frustration after about 20–30 s and says two out of three respondents were willing to walk on a solid red. Do not rewrite this as “two-thirds cross on red beyond 30 s”; willingness, admitted behaviour, and an observed threshold are different findings. [NZTA RR440](https://www.nzta.govt.nz/assets/resources/research/reports/440/docs/440.pdf) |
| LTN 2/95 normally 40 s, up to 60 s | **Verified but obsolete primary guidance** | Correct for the maximum vehicle-running period at specified Pelican operation, not a universal pedestrian wait cap. LTN 2/95 was withdrawn in 2019 and superseded. [DfT page](https://www.gov.uk/government/publications/the-design-of-pedestrian-crossings-ltn-295), [official PDF](https://assets.publishing.service.gov.uk/media/5a7d5cc0e5274a3356f2bc27/ltn-2-95_pedestrian-crossings.pdf) |
| MUTCD clearance speed 1.07 m/s | **Verified primary evidence** | The 2009 and 2023 MUTCD use 3.5 ft/s (about 1.07 m/s) for clearance guidance and explicitly say to consider slower speeds where slower pedestrians or wheelchair users routinely cross. The 2023 MUTCD does **not** establish 0.8 m/s as the general design speed. [2009 §4E.06](https://mutcd.fhwa.dot.gov/htm/2009/part4/part4e.htm), [2023 official PDF](https://mutcd.fhwa.dot.gov/pdfs/11th_Edition/mutcd11thedition.pdf) |
| 1.0 m/s if more than 20% of users are 65+ | **Verified primary research recommendation; narrow attribution** | FHWA-RD-98-107 recommends 1.0 m/s for time-limited facilities when users over 65 exceed about 20%. Attribute it to the 1998 FHWA recommended HCM procedures, not as a timeless rule in every HCM edition. [FHWA report](https://www.fhwa.dot.gov/publications/research/safety/pedbike/98107/section2.cfm) |
| Cane 0.8, walker 0.6, wheelchair 1.1, amputee 0.7 m/s | **Secondary-only as currently cited** | FHWA reproduces these mean values from *Human Factors in Traffic Safety* / Perry; LaPlante and Kaeser reviewed prior values rather than collecting this exact dataset. Safe wording: “FHWA training material reproduces mean values of …”; do not call them universal assistive-device speeds. [FHWA course, Table 8-4](https://www.fhwa.dot.gov/publications/research/safety/pedbike/05085/pdf/lesson8lo.pdf) |
| 40 s hard cap for CoFlow-5 | **Proposed target** | It is not created by the cited wait literature or LTN. Test it under declared demand, detection, geometry, and minimum-clearance assumptions. |

### DfT TAG values

| Claim | Classification | Audit result |
|---|---|---|
| Car/non-freight LGV reliability ratio 0.4 | **Verified primary guidance** | TAG A1.3 §6.3.4 recommends 0.4 to value changes in the **standard deviation of journey time** for car and non-freight LGV users. It is an appraisal conversion factor, not a reliability-performance target. [DfT TAG A1.3](https://assets.publishing.service.gov.uk/media/6a034015e71c4cdf4026baae/tag-unit-a1-3-user-and-provider-impacts.pdf) |
| Public-transport waiting is valued 2× in-vehicle time | **Verified primary guidance** | TAG §4.4.1 instructs analysts to multiply value of time by 2 for public-transport waiting and for walking/cycling access or interchange, based on a meta-analysis of over 130 estimates. It is an appraisal multiplier, not proof that every passenger perceives exactly twice the burden. [DfT TAG A1.3](https://assets.publishing.service.gov.uk/media/6a034015e71c4cdf4026baae/tag-unit-a1-3-user-and-provider-impacts.pdf) |
| “Wardman mean 1.80, n=138” | **Not independently verified here** | The official TAG document verifies its own 2× recommendation. Keep the Wardman detail only with a direct citation to the original meta-analysis. |

### Emergency response and preemption

| Claim | Classification | Audit result |
|---|---|---|
| ALS delay −7% survival per minute | **Verified association, overstated causal wording** | The 2022 PLOS ONE study analysed 4,278 adult non-traumatic OHCA cases in Taipei. Each additional minute was associated with lower adjusted odds of survival to discharge (aOR 0.93, 95% CI 0.89–0.97) and favourable neurological outcome (aOR 0.91). “7% lower odds” is not the same as a seven-percentage-point survival loss, and the observational result must not be converted into lives saved by CoFlow-5. [PLOS ONE](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0266969) |
| Cary −14.2%; Houston roughly −16% to −23% | **Cary primary applied report; Houston secondary within later reports** | Cary’s USFA applied-research report supports a 14.2% response-time decrease over its analysed area, with important time/location variation. The inspected Virginia Tech report describes Houston as 16% and 23%, not 18% and 23%. Use site-specific feasibility evidence, not an expected CoFlow-5 effect. [USFA Cary report](https://apps.usfa.fema.gov/pdf/efop/efo42422.pdf), [Virginia Tech report](https://vtechworks.lib.vt.edu/server/api/core/bitstreams/6617d4db-0528-4163-b9bd-b4b55bbf67d1/content) |
| Closely spaced preemptions add 20–30 s arterial travel time | **Verified primary evidence, case-specific** | Nelson and Bullock report that the most severe observed average arterial increase in their simulated SR-26 network was on the order of 20–30 s; a single preemption had minimal overall impact. Do not universalise the value. [DOI/abstract](https://doi.org/10.3141/1727-01) |
| Side-street +7.6% attributed to Nelson and Bullock | **Misattributed** | The 7.6% figure is from a separate Virginia Route 7 evaluation and refers to a westbound travel-time increase in one demand/case comparison. Remove it from the Nelson-and-Bullock parenthesis and cite separately if retained. [Virginia report](https://rosap.ntl.bts.gov/view/dot/35851/dot_35851_DS1.pdf) |
| CoFlow-5 EV targets and civilian-delay budget | **Proposed targets** | The −25%, −10%, and ≤5% values are team acceptance criteria, not consequences of the EMS or EVP literature. |

### Production and adaptive traffic systems

| Claim | Classification | Audit result |
|---|---|---|
| SCATS provides manual intervention and audit trails | **Verified primary product documentation** | The 2022 SCATS Core brochure says SCATS Region provides an audit trail of user-data changes, plan changes, and manual intervention; SCATS Access provides monitoring and manual intervention. This supports operator-control and logging requirements, not a claim that SCATS validates CoFlow-5’s exact fallback ladder. [Transport for NSW brochure](https://www.transport.nsw.gov.au/system/files/media/documents/2022/SCATS-Core-brochure-Final-web-spreads.pdf) |
| SCOOT reduced Southampton bus times up to 39% | **Secondary-only for the exact number; wording correction** | The original conference paper was not accessible in the inspected repository. The TRID catalogue abstract reports bus journey-time reductions up to 39% after SCOOT operation. This is not evidence that a dedicated **bus-priority** feature cut bus times by 39%; dedicated SCOOT bus-priority trials are later work. [University record](https://eprints.soton.ac.uk/75245/), [TRID abstract](https://trid.trb.org/view/310008) |
| SCOOT loses benefits under congestion | **Secondary-only for the 1986 source; generally supported** | The same catalogue abstract says SCOOT may lose many benefits when the network becomes congested. Later studies also report minimal improvements near saturation. Use “benefits can diminish near saturation,” not “SCOOT fails under congestion.” [TRID 1986 abstract](https://trid.trb.org/view/310008), [congestion evaluation abstract](https://trid.trb.org/View/663623) |
| Surtrac falls back to default durations on sensor/network failure | **Verified authors’ primary report, self-reported system evidence** | The CMU report says the Executor may fall back to Scheduler-calculated default phase durations during prolonged sensor or network failure; it also discusses recent-data operation during short communication outages. This supports a fallback requirement, but not CoFlow-5’s full Max-Pressure → actuated → fixed-time ladder. [CMU report](https://publications.ri.cmu.edu/storage/publications/pub_files/2013/1/13-0315.pdf) |

### Exposure, emissions, and incidents

| Claim | Classification | Audit result |
|---|---|---|
| 6.4M children (13.5%) attended schools within 250 m of a major road | **Numerically wrong / overstated** | Kingsley reports 3.2M students (6.2%) within 100 m plus 3.2M (6.3%) at 100–250 m: **6.4M, 12.5%** of the study population. The article is in *Journal of Exposure Science & Environmental Epidemiology*. Correct both percentage and journal. [Original article](https://pmc.ncbi.nlm.nih.gov/articles/PMC4179205/), [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/24496217/) |
| Majority-Black schools 18% more likely to be within 250 m | **Verified primary evidence** | The paper reports 18% higher likelihood (95% CI 13–23%) for schools serving predominantly Black students. Preserve the study period (2005–2006), definitions, and US scope. [PubMed abstract](https://pubmed.ncbi.nlm.nih.gov/24496217/) |
| 33% of public schools within 400 m; 12% within 100 m | **Secondary-only at this precision; scope correction** | The accessible primary publisher abstract reports only **over 30%** and **over 10%** across nine large US metropolitan areas; exact 33%/12% values occur in secondary summaries. Use the primary rounded wording unless the full paper is inspected, and do not imply a census of every US public school. [Publisher DOI](https://doi.org/10.1080/09640560802208173) |
| Avoiding one HDV stop saves up to 0.32 kg CO2 and 1.8 g NOx | **Verified primary evidence, bounded context** | Deschle et al. report “up to” these values for the studied heavy-duty vehicle crossing scenarios under near-free-flow/minimum-interaction conditions. It is not a generic per-stop factor for all fleets and networks. [Original article](https://doi.org/10.3390/en15031242) |
| SUMO/HBEFA values represent air quality or exposure | **Rejected** | SUMO provides modelled tailpipe-emission rates, not ambient concentration, dispersion, inhaled dose, or epidemiological exposure. The project correctly labels them proxies. SUMO also warns about fit errors for some HBEFA classes. [SUMO HBEFA documentation](https://eclipse.dev/sumo/docs/Models/Emissions/HBEFA4-based.html) |
| Incidents cause 25% of congestion | **Verified official agency estimate** | FHWA says incidents account for about 25% of total congestion, with work zones 10% and weather 15%. Preserve “about” and US/FHWA context. [FHWA](https://ops.fhwa.dot.gov/program_areas/reduce-non-cong.htm) |
| Incident-related delay is 25–30% of metropolitan congestion delay | **Verified official handbook estimate** | FHWA’s handbook says 25–30% in most metropolitan areas. This is an estimate, not a universal detection threshold or a measured CoFlow-5 scenario share. [FHWA handbook Ch. 10](https://ops.fhwa.dot.gov/freewaymgmt/publications/frwy_mgmt_handbook/chapter10.htm) |
| A universal incident-detection delay benchmark | **Not verified** | No such universal number was established. CoFlow-5 should set thresholds after a pilot and report delay, false alarms, misses, and recovery by severity. |

### RESCO, T-REX, communications, and LLM systems

| Claim | Classification | Audit result |
|---|---|---|
| RESCO shows SOTA controllers struggle on realistic networks | **Verified with narrower wording** | RESCO used SUMO scenarios based on real traffic networks/data. MPLight diverged on irregular intersections; IPPO was unstable; IDQN outperformed other tested RL methods in the final ten episodes on all but Cologne Regional. Say “in RESCO’s tested scenarios,” not that RL generally fails or that the systems were deployed. [NeurIPS paper](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/file/f0935e4cd5920aa6c7c996a5ee53a70f-Paper-round1.pdf) |
| RESCO tables use best episodes and can overstate final performance | **Verified primary evidence** | Table 1 reports the best episode averaged over five seeds, not final performance; the paper explicitly contrasts MPLight’s best 78 s delay with later divergence above 200 s. [NeurIPS paper](https://datasets-benchmarks-proceedings.neurips.cc/paper_files/paper/2021/file/f0935e4cd5920aa6c7c996a5ee53a70f-Paper-round1.pdf) |
| RESCO proves shared-policy DQN is the correct CoFlow-5 architecture | **Project inference** | RESCO supports choosing a simple DQN baseline and testing heterogeneity, but it does not validate CoFlow-5’s five-role architecture, sole-actuator design, or message bus. |
| T-REX: independent methods degrade under incidents; hierarchy is steadier | **Verified preprint result, bounded to tested setups** | The T-REX preprint reports sharp degradation of independent/decentralised methods under incident distribution shift and more stable hierarchical methods on large irregular networks. It is simulation evidence from a 2025 preprint, not field validation. [T-REX paper](https://arxiv.org/html/2506.13836) |
| T-REX hierarchy costs ~14× more to train | **Overstated** | T-REX trained IDQN/MPLight for 100 episodes and IPPO/FMA2C for 1,400. That is a 14× **episode allocation**, not a measured 14× wall-clock, compute, energy, or monetary cost. The methods also use different best-window evaluation lengths. [T-REX methods](https://arxiv.org/html/2506.13836v1) |
| Communication reliability is “almost never tested” and Finkelberg is essentially the only quantification | **Unsupported exhaustive claim** | Finkelberg verifies that many cited studies assume perfect communications, but one paper cannot prove an exhaustive literature count. Replace with “communication impairment is under-tested; Finkelberg provides a directly relevant quantified example.” |
| Finkelberg communication sensitivity | **Verified primary evidence** | At the highest tested 30 dB SNR penalty, uncorrected average delay rose 22.0% (homogeneous) and 20.7% (heterogeneous); correction reduced the increases to about 1.0% and 7.5%. This was a Vissim+OMNeT++ DSRC simulation, not packet-loss testing of CoFlow-5. [IEEE author PDF](https://toledo.net.technion.ac.il/files/2022/09/IEEE-ITS_Communication_22_Journal.pdf), [DOI](https://doi.org/10.1109/TITS.2022.3140767) |
| CoLLMLight needs asynchronous caching to remain responsive | **Verified for the accepted 2026 design** | The ICLR 2026 version runs cooperative reasoning asynchronously, caches guidance, and uses it in a fast decision module. This supports decoupling slow reasoning from time-critical decisions. It does **not** prove that an LLM must never control a signal: CoLLMLight is itself an LLM signal-control simulation framework. The “LLM never writes TraCI” rule remains a CoFlow-5 safety decision. [ICLR page](https://iclr.cc/virtual/2026/poster/10010107), [OpenReview](https://openreview.net/forum?id=KeJqoEVOeY) |
| AgentSUMO is scenario tooling, not a traffic-control loop | **Verified primary evidence** | AgentSUMO translates natural-language policy requests into executable SUMO scenario plans through an interactive planning protocol and MCP tools. Treating it as advisory scenario tooling is accurate. [Paper](https://arxiv.org/html/2511.06804), [authors’ repository](https://github.com/mw-jeong/AgentSUMO) |
| AgentSUMO has “no seeds, no CIs” | **Verified only as non-reporting** | The inspected paper does not report a multi-seed protocol, replicate counts, confidence intervals, or uncertainty estimates. Write “not reported in the paper,” not “the implementation has none.” SUMO itself supports fixed and varied seeds. [AgentSUMO paper](https://arxiv.org/html/2511.06804), [SUMO randomness docs](https://sumo.dlr.de/docs/Simulation/Randomness.html) |

### Direct-CO2 reward

| Claim | Classification | Audit result |
|---|---|---|
| Direct CO2 reward is unavailable or inherently invalid | **Rejected** | SUMO exposes per-edge CO2 emission estimates through TraCI, so a direct modelled-CO2 reward is implementable. [SUMO TraCI edge values](https://sumo.dlr.de/daily/userdoc/TraCI/Edge_Value_Retrieval.html) |
| Direct CO2 reward is a standard RESCO reward | **Rejected** | Original RESCO’s listed reward metrics are travel time, approximated signal delay, waiting time, queue length, and pressure. CO2 is not one of its five standard metrics. [RESCO paper](https://people.engr.tamu.edu/guni/papers/NeurIPS-signals.pdf) |
| Direct CO2 is an effective reward by default | **Unsupported/overstated** | Schumacher et al. directly tested SUMO CO2 as a DQN reward and found it inefficient relative to some proxy rewards; combined rewards were sensitive to weights and scenarios. CoFlow-5 should compare direct CO2, traffic proxies, and mixed rewards by ablation rather than assume one. [SUMO Conference paper](https://doi.org/10.52825/scp.v4i.222) |
| CO2/NOx reward values are air-quality evidence | **Rejected** | They remain model outputs/proxies. Any reward weight is a team judgement and requires sensitivity analysis; any claim about local exposure requires a dispersion/exposure model or field measurements. |

### Remaining numerical register entries

The following numbers in the 32-row register were **not promoted to verified primary evidence in this audit** because the original source was not directly inspected or the row explicitly relies on an intermediary:

- TfL “compliance drops after 30 s” (cited through a London Assembly question);
- Austroads 20–120 s tolerable waits and >90 s cycle advice (cited through NZTA);
- exact LPI effects of −28%, −58.7%, CMF 0.87, −5.45%, and −14.7%;
- Wardman 1.80 / n=138 and US walking/waiting 2–5×;
- the claim that headway-based holding is best under disruption;
- NFPA turnout/travel/alarm values and NHS category response values;
- the 2025 BMC −6%/min and 2.1× survival figures;
- New Orleans “≤30 min for 75%” TIM performance;
- EY’s “>2/3” public-opinion result; and
- EMVLight’s −42.6% result where it appears outside the 32-row table.

These may be true, but until checked against their owning standard or original paper they should be labelled **secondary/unverified**, not “verified evidence.” The EY row is vendor survey evidence even if its arithmetic is accurate.

## Recommended claim corrections

Use the following replacements consistently across the requirements book, Empathize pack, project context, slides, and future reports:

1. **Evidence trail:** “A 32-row mixed-source evidence register; rows are tagged primary, secondary, vendor, or proposed.”
2. **Walking speed:** “The MUTCD uses 3.5 ft/s (1.07 m/s) for clearance and calls for lower values where slower users routinely cross; FHWA material reproduces assistive-device means around 0.6–1.1 m/s.”
3. **Pedestrian waiting:** “In one New Zealand study, perceived mean wait was about twice observed mean wait; frustration rose disproportionately after about 20–30 s.”
4. **DfT:** “TAG uses 0.4 as an appraisal reliability ratio for car/non-freight LGV journey-time variability and 2× value of time for public-transport waiting.”
5. **EMS:** “In a Taipei OHCA cohort, each additional ALS-response minute was associated with 7% lower adjusted odds of survival to discharge; CoFlow-5 makes no lives-saved claim.”
6. **Preemption externality:** “Nelson and Bullock observed a worst case on the order of 20–30 s extra average arterial travel time under closely spaced preemptions; the 7.6% result is from a separate Virginia study.”
7. **SCOOT:** “A catalogue abstract reports up to 39% shorter bus journey times in the Southampton SCOOT evaluation; this is not a CoFlow-5 guarantee and should not be labelled a dedicated bus-priority effect.”
8. **School proximity:** “In 2005–2006, 6.4M students (12.5% of the studied population) attended US schools within 250 m of a major roadway.”
9. **RESCO:** “In RESCO’s tested realistic SUMO scenarios, several advanced methods were unstable; IDQN was highly competitive, and best-episode reporting differed materially from final performance.”
10. **T-REX:** “FMA2C/IPPO received 1,400 episodes versus 100 for IDQN/MPLight; this is a 14× episode budget, not a general 14× cost.”
11. **Finkelberg:** “Communication impairment is under-tested; Finkelberg quantified large delay and fairness effects under severe simulated DSRC distortion.”
12. **CoLLMLight:** “Its accepted design decouples asynchronous cached cooperative reasoning from faster decisions; CoFlow-5’s ban on LLM actuation is an architectural safety choice.”
13. **AgentSUMO:** “AgentSUMO is interactive scenario-generation and analysis tooling; its paper does not report seeds or confidence intervals.”
14. **Direct CO2:** “SUMO modelled CO2 can be used directly as a reward, but published experiments found direct CO2 inefficient for DQN in tested scenarios; reward choice and weights require ablation.”
15. **All matrices:** “Decision-matrix scores and weights are team judgements. Evidence informs the criteria, not the numeric score.”

## Bottom line

The evidence supports the **needs** (slower pedestrians, reliability, transit waiting, preemption externalities, operator intervention/audit, local exposure checks, incident impact, and communication-failure testing). It does not empirically validate the selected five-agent decomposition, sole-writer rule, fallback sequence, reward weights, arbitration order, KPI thresholds, or schedule. Those remain coherent **project assumptions and proposed targets** to be tested against fixed-time, actuated, and Max-Pressure baselines.
