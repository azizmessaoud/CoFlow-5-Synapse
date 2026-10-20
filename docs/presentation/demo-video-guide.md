# Demo video guide

How a user uses TraffiX, when each feature appears, and a scene-by-scene plan for the video.
All times come from a stress test of the 12 scenarios on 20 Oct 2026 (every page and API polled
during each run). "Sim time" is the clock in the scenario bar. At **16× speed**, one simulated
minute takes about 4 real seconds, plus about 10 s to start.

## 1. Before you record

1. Close browser tabs you don't need. The laptop has 16 GB; with many tabs open the page freezes.
2. Start the app without the SUMO window (faster, and closing that window stops the run):
   `py -3.11 scripts\run_live.py`, then open http://localhost:8000.
   Use `--gui` only for a scene that shows SUMO itself.
3. Check the LLM: the Analyst page shows "LLM agent" under answers when it works. It needs
   `GROQ_API_KEY` or `ANTHROPIC_API_KEY` in `.env` and internet. Without it everything still works
   with templates (say so if asked).
4. Pick **16× speed** in the scenario bar, then **Start**. The bar shows the scenario, the clock and "live".
5. Do not use the **heavy** scenario: near its end (after sim 53 min, ~466 vehicles) the page can
   freeze for up to 19 s.

## 2. How a user uses the app

The left menu has one page per person (persona). Each page shows only what that person needs.

| Page | Who | What to show | What to click |
|---|---|---|---|
| Overview | everyone | live map, counts, active alerts | persona cards |
| Pedestrian | Ferjani | each crossing: walk/wait, people waiting, longest wait; rain note | — |
| Car driver | Faycel | incidents, congestion, floods, forecast; trip plan with delay, alerts on the route and Route B | **From / to**, **Find my route** (refreshes every 5 s) |
| Bus passenger | Mamadou | next buses at my stop (ETA, distance, late or regular), alerts for my line | **Line**, **My stop** |
| Bus driver | Hédi | my bus: next junction, gap to the bus ahead, late → priority requested; priority decisions | **Bus** |
| Ambulance crew | Touhami | emergency vehicles on the map, junctions preparing, green / denied decisions | — |
| Traffic operator | Kamel | stale detectors, incidents, rain, forecast; junction modes; **Operator copilot** | **Approve / Dismiss** a suggestion, **Draft incident report** |
| Incident analyst | Tahani | **Ask Synapse** (answers with citations or abstains); decision log; trained models | example questions, **Ask**, filter box, **Verify with CoFlow Synapse** on a log entry |
| Results | team | experiment tables and chart | — |

**Language:** the select at the right of the top bar (EN / FR / عربي) changes the alerts, the
copilot and Synapse answers. Arabic is shown right to left. Page labels stay in English.

**Controllers:** the third select chooses the traffic-light agent: max-pressure (default), predictive
(MPC), reinforcement learning, rules only (no models), or no supermaster.

## 3. When each feature appears

| Feature | Scenario | Sim time | Real time at 16× | Where to see it |
|---|---|---|---|---|
| Peak forecast alert | morning_peak, evening_peak, incident, rain | 0:05 | at start | Operator, Car driver, Bus pages |
| Congestion alert | incident | 8:50 | ~45 s | Operator, Car driver, map in red |
| Rain alert, longer signal timings | rain | 10:00 | ~50 s | Operator ("rain intensity"), Pedestrian, Car driver |
| **Lane blocked (incident)** | incident | 15:55 | ~70 s | Operator (incident count, warning box, copilot suggestion), Car driver, Ambulance crew |
| **Route B** for drivers | incident; rain | 15:55; 21:35 | ~70 s; ~90 s | Car driver: plan a trip through Av. Habib Bourguiba |
| Walk signal after a long wait | most scenarios | 5–25 min | — | Pedestrian |
| Green held until the crossing is clear | most scenarios | 5–28 min | — | Pedestrian |
| Late bus, then bus priority | all; bus_disruption | 17–25 min, then 18–51 min | ~75–100 s | Bus passenger, Bus driver, Operator |
| **Ambulance / police on the way** | emergency | 21:45 | ~90 s | Ambulance crew (preparing → green), Car driver and Pedestrian ("keep the junction clear"), Operator |
| **Sensor fault → junction falls back to fixed mode** | incident | 25:15 | ~105 s | Operator: stale detectors = 1+, J1 mode "fixed (stale data)", copilot suggestion |
| **Flood: road impassable** | rain | 30:00 | ~2 min | Car driver (flooded roads, dashed blue), Operator, all pages |
| Everything at once | combined | rain 5:00, incident 15:55, ambulances 22:50 | ~30 s, ~70 s, ~95 s | good final scene |

Never seen in any scenario: "Priority denied to an ambulance (exit lane full)". Don't promise it.

## 4. Video plan (about 8 minutes)

Matches section 3 of the validation brief: a concrete use case, input → output, the role of each agent.

1. **Overview (30 s).** Say the problem in one sentence. Start **morning_peak** at 16×. Show the
   map filling with cars and the counts. Say: five agents per junction advise one master; only the
   master changes its light.
2. **Ambulance (1.5 min).** Start **emergency**. At ~90 s open **Ambulance crew**: a junction
   "preparing", then "green". Switch to **Car driver**: "keep the junction clear". Say: the emergency
   route agent (network) warns ahead; the emergency agent (junction) requests green; the master grants it.
3. **Incident and Route B (2 min).** Start **incident**. Open **Car driver**, plan a trip, wait ~70 s:
   "Lane blocked on Avenue Habib Bourguiba", then Route B with the time saved. Open **Operator**: the
   incident box and the copilot suggestion; click **Approve** (recorded, not applied). At ~105 s the
   sensor fault: J1 goes to "fixed (stale data)". Say why: stale data must not drive a light.
4. **Rain and flood (1 min).** Start **rain**. ~50 s: rain alert. ~2 min: flood, the road turns dashed blue.
5. **Bus (1 min).** In any running scenario open **Bus passenger**, choose a line and stop: next buses,
   late or regular. Open **Bus driver**: "late: priority requested" and the priority decisions.
6. **Why did it do that? (1.5 min).** Open **Incident analyst**. Ask a question about something already
   on screen (e.g. "Why did J1 switch?", or an ambulance that has appeared). Show the citations
   [#id]. Open a log entry → **Verify with CoFlow Synapse**. Ask about a vehicle that does not exist:
   it abstains. Say: a false claim gives abstain.
7. **Language (20 s).** Switch to FR, then عربي: alerts and copilot change language.
8. **Results (30 s).** Open **Results** and show the comparison with SUMO fixed and actuated
   (3 scenarios × 3 seeds). Say it honestly: pedestrians are much safer, cars mixed, ambulances
   slower, nothing significant yet with 3 seeds.

## 5. Things to know while recording

- Street names come from OpenStreetMap; some are only in Arabic (e.g. شارع الحبيب بورقيبة).
- The built-in example "Why did ambulance 0 get green?" abstains if ambulance 0 has not appeared yet.
  It then lists the vehicles that exist; ask about one of those.
- Copilot **Approve** only records the decision in the log. Nothing is applied automatically (by design).
- The demand is synthetic. Say "simulation", not "Tunis measurements".
