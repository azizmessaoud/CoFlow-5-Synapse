# Learnings

Durable discoveries go here, then get promoted into `docs/` or `.kiro/specs/`.

Do not store secrets. Do not treat a chat conclusion as gated work.

## 2026-09-21

- Course authority is `SUMO_forStudents.docx` → `docs/source/course-brief.md`.
- Design Thinking 1–3 are done. Prototype/Test are the queue.
- Harness pattern lifted from flyrank-bih/harness-engineering-playbook. Product is SUMO, not Shopify.
- Output style from ayghri/i-have-adhd. Next action first.
- ADR-0001 beats older docs that make A1 an RL or LLM controller.

## 2026-09-22

- Native Windows Python 3.11.9 and Eclipse SUMO 1.27.1 both run. Headless `sumo.exe` and TraCI from `SUMO_HOME\\tools` completed the frozen smoke scenario (20 vehicles, 102 TraCI steps).
- Row 01 cannot gate: Windows Code Integrity policy `{0283ac0f-fff1-49ae-ada1-8a933130cad6}` blocks unsigned `libsumo` DLLs (`geos_c.dll`, `jupedsim.dll`). WSL Python is still not an allowed workaround.
- Do not import `libsumo` at module load; TraCI-only product code can proceed while that policy stands.
- ADR-0003: hosted API/UI is read-only over tagged evidence; PR CI stays SUMO-free; `eval.yml` must fail if `libsumo` cannot load; MLflow must not mint a second `run_id`.
- Rows 02–09 gated on TraCI. Daily watch command is `py -3.11 scripts\\watch_sumo.py smoke`. Headless A1 is `generate_max_pressure_artifacts.py`. Live A1 window is `watch_sumo.py a1`. Do not use `run_native_smoke.py` until libsumo is allowed.

- Row 08 VERIFY: all four named test files passed with counts 4, 3, 3, and 9; the verdict comes from tests and files, not an agent score.
- Row 08 VERIFY: eight contracted message faults each left A1 on legal local Max-Pressure control, with 8 legal and 0 illegal decisions.
- Row 08 VERIFY: recovery followed only `COOPERATIVE_MAX_PRESSURE -> ACTUATED -> FIXED_TIME`; optional DQN did not replace the ladder.
- Row 08 VERIFY: Synapse available, killed, retrieval unavailable, and provider unavailable all produced the same action-sequence hash while failures stayed visible.
- Row 08 VERIFY: click `harness/work/08-failure-injection/artifacts/action-sequence-comparison.json`; rerun `py -3.11 -m pytest tests/contracts/test_synapse_non_actuation.py -q`; pass means explanations cannot change light actions.
